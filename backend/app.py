"""
Hallucination Detection Web Application - Main FastAPI Backend
Simplified version with prioritized LLM voting
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
from pathlib import Path
from datetime import datetime

from real_llm_services import (
    get_target_response,
    extract_claims_with_llm,
)
from prioritized_voting import verify_with_prioritized_voting
from models import ClaimVerification
from metrics_calculator import MetricsCalculator

# Map select box choices to concrete model identifiers
TARGET_MODEL_LABELS: Dict[str, str] = {
    "mistral": "mistral-small",
    "openai": "o1-preview",
    "gemini": "gemini-1.5-flash",
    "deepseek": "deepseek-chat",
}

app = FastAPI(title="Enhanced Hallucination Detection API", version="2.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend for convenience
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


class UserQuery(BaseModel):
    question: str
    target_llm: Optional[str] = "mistral"


class AnalysisResponse(BaseModel):
    original_question: str
    llm_response: str
    claims: List[ClaimVerification]
    summary: Dict[str, Any]
    confidence_analysis: Dict[str, Any]


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Enhanced Hallucination Detection API is running"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_hallucination(query: UserQuery) -> AnalysisResponse:
    try:
        target_choice = (query.target_llm or "mistral").lower()
        target_model_label = TARGET_MODEL_LABELS.get(target_choice, TARGET_MODEL_LABELS["mistral"])

        # Step 1: Get response from the selected target LLM
        llm_response = get_target_response(query.question, target_choice)

        # Step 2: Extract factual claims using OpenAI
        claims_text = extract_claims_with_llm(llm_response)

        if not claims_text:
            summary = {
                "total_claims": 0,
                "verified": 0,
                "refuted": 0,
                "uncertain": 0,
                "extraction_model": "openai-gpt-4o-mini",
                "target_model": target_model_label,
            }
            return AnalysisResponse(
                original_question=query.question,
                llm_response=llm_response,
                claims=[],
                summary=summary,
                confidence_analysis={},
            )

        # Step 3: Verify claims with prioritized voting system
        verification_results = verify_with_prioritized_voting(claims_text, target_choice)

        verified_claims: List[ClaimVerification] = []
        for index, result in enumerate(verification_results):
            verified_claims.append(
                ClaimVerification(
                    id=f"C{index + 1}",
                    claim=result["claim"],
                    llm1_verification=result["llm1_result"],
                    llm2_verification=result["llm2_result"],
                    llm1_name=result["llm1_name"],
                    llm2_name=result["llm2_name"],
                    llm3_name=result["llm3_name"],
                    llm3_verification=result["llm3_result"],
                    voting_used=result["voting_used"],
                    final_verdict=result["final_verdict"],
                )
            )

        # Step 4: Collect verification LLM names used
        verifier_llms = set()
        # Count verdicts
        verified_count = 0
        refuted_count = 0
        uncertain_count = 0
        
        for claim in verified_claims:
            if claim.llm1_name:
                verifier_llms.add(claim.llm1_name)
            if claim.llm2_name:
                verifier_llms.add(claim.llm2_name)
            if claim.llm3_name:
                verifier_llms.add(claim.llm3_name)
            
            # Count based on final verdict
            verdict = claim.final_verdict.lower() if claim.final_verdict else "uncertain"
            if verdict == "yes":
                verified_count += 1
            elif verdict == "no":
                refuted_count += 1
            else:
                uncertain_count += 1
        
        summary = {
            "total_claims": len(verified_claims),
            "verified": verified_count,
            "refuted": refuted_count,
            "uncertain": uncertain_count,
            "extraction_model": "openai-gpt-4o-mini",
            "verifier_llms": list(verifier_llms),
            "target_model": target_model_label,
            "voting_enabled": True,
        }

        return AnalysisResponse(
            original_question=query.question,
            llm_response=llm_response,
            claims=verified_claims,
            summary=summary,
            confidence_analysis={},  # Empty, not used anymore
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "hallucination-detector"}


# ============================================================================
# Manual Annotation Endpoints for TruthfulQA Evaluation
# ============================================================================

# Storage directory for annotations
ANNOTATIONS_DIR = Path("data/annotations")
ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/api/save-annotation")
async def save_annotation(request: Request):
    """
    Save manual annotations for a question
    
    Request body:
    {
        "question_id": "Q123",
        "target_model": "mistral",
        "annotations": {"claim_1": "correct", "claim_2": "incorrect", ...},
        "timestamp": "2025-10-19T12:00:00"
    }
    """
    try:
        data = await request.json()
        
        question_id = data.get('question_id')
        target_model = data.get('target_model')
        annotations = data.get('annotations', {})
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        if not question_id or not target_model:
            raise HTTPException(status_code=400, detail="Missing question_id or target_model")
        
        # Create filename with timestamp
        safe_timestamp = timestamp.replace(':', '-').replace('.', '-')
        filename = f"{target_model}_{question_id}_{safe_timestamp}.json"
        filepath = ANNOTATIONS_DIR / filename
        
        # Save annotation data
        annotation_data = {
            'question_id': question_id,
            'target_model': target_model,
            'annotations': annotations,
            'timestamp': timestamp,
            'total_claims': len(annotations),
            'annotated_by': 'manual'
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(annotation_data, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "message": "Annotations saved successfully",
            "filepath": str(filepath),
            "total_claims": len(annotations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save annotations: {str(e)}")


@app.post("/api/save-predictions")
async def save_predictions(request: Request):
    """
    Save system predictions for later comparison with manual annotations
    
    Request body:
    {
        "question_id": "Q123",
        "target_model": "mistral",
        "predictions": {
            "claim_1": {"claim": "...", "final_verdict": "Yes", ...},
            ...
        }
    }
    """
    try:
        data = await request.json()
        
        question_id = data.get('question_id')
        target_model = data.get('target_model')
        predictions = data.get('predictions', {})
        
        if not question_id or not target_model:
            raise HTTPException(status_code=400, detail="Missing question_id or target_model")
        
        # Save predictions
        filename = f"{target_model}_{question_id}_predictions.json"
        filepath = ANNOTATIONS_DIR / filename
        
        prediction_data = {
            'question_id': question_id,
            'target_model': target_model,
            'predictions': predictions,
            'timestamp': datetime.now().isoformat(),
            'total_claims': len(predictions)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(prediction_data, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "message": "Predictions saved successfully",
            "filepath": str(filepath)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save predictions: {str(e)}")


@app.post("/api/calculate-metrics")
async def calculate_metrics(request: Request):
    """
    Calculate precision, recall, F1 for annotated question
    
    Request body:
    {
        "question_id": "Q123",
        "target_model": "mistral"
    }
    """
    try:
        data = await request.json()
        
        question_id = data.get('question_id')
        target_model = data.get('target_model')
        
        if not question_id or not target_model:
            raise HTTPException(status_code=400, detail="Missing question_id or target_model")
        
        # Find the most recent annotation file
        pattern = f"{target_model}_{question_id}_*.json"
        annotation_files = sorted(ANNOTATIONS_DIR.glob(pattern))
        annotation_files = [f for f in annotation_files if not f.name.endswith('_predictions.json') 
                           and not f.name.endswith('_metrics.json')]
        
        if not annotation_files:
            raise HTTPException(status_code=404, detail="No annotations found for this question")
        
        latest_annotation = annotation_files[-1]
        
        # Load annotations
        with open(latest_annotation, 'r', encoding='utf-8') as f:
            annotation_data = json.load(f)
        
        annotations = annotation_data['annotations']
        
        # Load predictions
        predictions_file = ANNOTATIONS_DIR / f"{target_model}_{question_id}_predictions.json"
        
        if not predictions_file.exists():
            raise HTTPException(status_code=404, detail="No predictions found for this question")
        
        with open(predictions_file, 'r', encoding='utf-8') as f:
            prediction_data = json.load(f)
        
        predictions = prediction_data['predictions']
        
        # Calculate metrics
        calculator = MetricsCalculator()
        metrics = calculator.calculate_metrics(annotations, predictions)
        
        # Save metrics
        metrics_data = {
            'question_id': question_id,
            'target_model': target_model,
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'annotations': annotations,
            'predictions': {k: v['final_verdict'] for k, v in predictions.items()}
        }
        
        metrics_file = ANNOTATIONS_DIR / f"{target_model}_{question_id}_metrics.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "metrics": metrics,
            "metrics_file": str(metrics_file)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")


@app.get("/api/aggregate-metrics/{target_model}")
async def get_aggregate_metrics(target_model: str):
    """
    Get aggregate metrics for a target model across all annotated questions
    
    Args:
        target_model: Name of the target model (e.g., "mistral", "openai")
    """
    try:
        calculator = MetricsCalculator()
        aggregate = calculator.aggregate_metrics(target_model, ANNOTATIONS_DIR)
        
        if 'error' in aggregate:
            raise HTTPException(status_code=404, detail=aggregate['error'])
        
        return aggregate
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get aggregate metrics: {str(e)}")


@app.get("/api/evaluation-progress")
async def get_evaluation_progress():
    """
    Get progress of manual annotation across all models
    
    Returns count of annotated questions per model
    """
    try:
        models = ["mistral", "openai", "anthropic", "gemini", "deepseek"]
        progress = {}
        
        for model in models:
            # Count unique question IDs for this model
            pattern = f"{model}_*_metrics.json"
            metrics_files = list(ANNOTATIONS_DIR.glob(pattern))
            
            question_ids = set()
            for f in metrics_files:
                # Extract question_id from filename
                parts = f.stem.split('_')
                if len(parts) >= 2:
                    question_ids.add(parts[1])
            
            progress[model] = {
                'completed': len(question_ids),
                'total': 50,
                'percentage': (len(question_ids) / 50) * 100 if len(question_ids) > 0 else 0
            }
        
        total_completed = sum(p['completed'] for p in progress.values())
        total_required = 50 * len(models)  # 50 questions × 5 models = 250
        
        return {
            'per_model': progress,
            'overall': {
                'completed': total_completed,
                'total': total_required,
                'percentage': (total_completed / total_required) * 100 if total_completed > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
