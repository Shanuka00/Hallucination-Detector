"""
Hallucination Detection Web Application - Main FastAPI Backend
Enhanced with REAL LLM APIs and Multi-KG verification
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os

from real_llm_services import (
    get_target_response,
    extract_claims_with_llm,
)
from prioritized_voting import verify_with_prioritized_voting
from multi_kg_service import MultiKGService
from models import ClaimVerification
from confidence_scorer import ConfidenceScorer

# Map select box choices to concrete model identifiers
TARGET_MODEL_LABELS: Dict[str, str] = {
    "mistral": "mistral-small",
    "openai": "o1-preview",
    "gemini": "gemini-1.5-flash",
    "deepseek": "deepseek-chat",
}

# Initialize services
multi_kg_service = MultiKGService()
confidence_scorer = ConfidenceScorer(alpha=0.4, beta=0.4, gamma=0.2)

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
                "high": 0,
                "medium": 0,
                "low": 0,
                "wikipedia_checks": 0,
                "total_claims": 0,
                "overall_confidence": 0.0,
                "extraction_model": "openai-gpt-4o-mini",
                "target_model": target_model_label,
            }
            fallback_confidence = {
                "overall_confidence": 0.0,
                "total_claims": 0,
                "claim_details": [],
                "weights_config": {"alpha": 0.4, "beta": 0.4, "gamma": 0.2},
            }
            return AnalysisResponse(
                original_question=query.question,
                llm_response=llm_response,
                claims=[],
                summary=summary,
                confidence_analysis=fallback_confidence,
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

        # Step 4: External verification with Multi-KG for medium-risk items
        wikipedia_checks_count = 0
        for claim_verification in verified_claims:
            if claim_verification.should_check_wikipedia():
                try:
                    external_result = multi_kg_service.verify_claim(claim_verification.claim)
                except Exception:
                    external_result = "Unclear"

                claim_verification.wikipedia_status = external_result
                claim_verification.wikipedia_summary = f"Multi-KG consensus: {external_result}"
                claim_verification.is_wikipedia_checked = True
                wikipedia_checks_count += 1

        # Step 5: Compute overall confidence metrics
        overall_confidence, confidence_analysis = confidence_scorer.calculate_overall_confidence(verified_claims)

        # Step 6: Summarise risk buckets and metadata
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        for claim in verified_claims:
            risk_counts[claim.get_risk_level()] += 1

        # Collect verification LLM names used
        verifier_llms = set()
        for claim in verified_claims:
            if claim.llm1_name:
                verifier_llms.add(claim.llm1_name)
            if claim.llm2_name:
                verifier_llms.add(claim.llm2_name)
            if claim.llm3_name:
                verifier_llms.add(claim.llm3_name)
        
        summary = {
            **risk_counts,
            "wikipedia_checks": wikipedia_checks_count,
            "total_claims": len(verified_claims),
            "overall_confidence": overall_confidence,
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
            confidence_analysis=confidence_analysis,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "hallucination-detector"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
