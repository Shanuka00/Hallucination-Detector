"""
Hallucination Detection Web Application - Main FastAPI Backend
Enhanced with LLM-based claim extraction and Wikipedia verification
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import json

# Import services
from targetllm_stub import get_targetllm_response
from claimllm_stub import extract_claims_with_claimllm, simulate_claimllm_api_call
from claim_verifier_stub import verify_with_llm1, verify_with_llm2
from wikipedia_service import WikipediaService
from graph_builder import build_hallucination_graph
from models import ClaimVerification
from confidence_scorer import ConfidenceScorer

# Initialize services
wikipedia_service = WikipediaService(use_simulation=True)
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

# Mount static files for frontend
import os
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

class UserQuery(BaseModel):
    question: str

class AnalysisResponse(BaseModel):
    original_question: str
    llm_response: str
    claims: List[ClaimVerification]
    graph_data: Dict[str, Any]
    summary: Dict[str, Any]  # Enhanced to include Wikipedia stats
    confidence_analysis: Dict[str, Any]  # New: Detailed confidence scoring

@app.get("/")
async def root():
    return {"message": "Enhanced Hallucination Detection API is running"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_hallucination(query: UserQuery):
    """
    Enhanced endpoint to analyze potential hallucinations using LLM extraction and verification
    """
    try:
        # Step 1: Get target LLM response
        llm_response = get_targetllm_response(query.question)
        
        # Step 2: Extract factual claims using ClaimLLM
        claimllm_result = simulate_claimllm_api_call(llm_response)
        claims_text = claimllm_result["claims"]
        
        if not claims_text:
            # Fallback: no claims found
            return AnalysisResponse(
                original_question=query.question,
                llm_response=llm_response,
                claims=[],
                graph_data={"nodes": [], "edges": [], "metrics": {}},
                summary={
                    "high": 0, "medium": 0, "low": 0, 
                    "wikipedia_checks": 0,
                    "total_claims": 0,
                    "overall_confidence": 0.0,
                    "claimllm_processing_time": claimllm_result["metadata"]["processing_time_ms"],
                    "claimllm_confidence": claimllm_result["metadata"]["confidence"],
                    "claimllm_model": claimllm_result["metadata"]["model"]
                },
                confidence_analysis={
                    "overall_confidence": 0.0,
                    "total_claims": 0,
                    "claim_details": [],
                    "weights_config": {"alpha": 0.4, "beta": 0.4, "gamma": 0.2}
                }
            )
        
        # Step 3: Verify claims with both LLMs
        verified_claims = []
        for i, claim in enumerate(claims_text):
            llm1_response = verify_with_llm1(claim)
            llm2_response = verify_with_llm2(claim)
            
            verification = ClaimVerification(
                id=f"C{i+1}",
                claim=claim,
                llm1_verification=llm1_response,
                llm2_verification=llm2_response
            )
            verified_claims.append(verification)
        
        # Step 4: Check medium-risk claims with Wikipedia
        wikipedia_checks_count = 0
        for claim_verification in verified_claims:
            if claim_verification.should_check_wikipedia():
                # Perform Wikipedia check for medium-risk claims
                wiki_result = wikipedia_service.verify_claim_with_wikipedia(claim_verification.claim)
                wiki_summary_data = wikipedia_service.get_summary_from_wikipedia(claim_verification.claim)
                
                claim_verification.wikipedia_status = wiki_result
                claim_verification.wikipedia_summary = wiki_summary_data.get("extract", "")[:200] + "..." if wiki_summary_data.get("extract") else None
                claim_verification.is_wikipedia_checked = True
                wikipedia_checks_count += 1
        
        # Step 6: Calculate advanced confidence scores
        overall_confidence, confidence_analysis = confidence_scorer.calculate_overall_confidence(verified_claims)
        
        # Step 7: Build hallucination graph with enhanced data
        graph_data = build_hallucination_graph(verified_claims)
        
        # Step 8: Generate enhanced summary statistics
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        for claim in verified_claims:
            risk_level = claim.get_risk_level()
            risk_counts[risk_level] += 1
        
        # Add ClaimLLM and Wikipedia statistics
        enhanced_summary = {
            **risk_counts,
            "wikipedia_checks": wikipedia_checks_count,
            "total_claims": len(verified_claims),
            "overall_confidence": overall_confidence,
            "claimllm_processing_time": claimllm_result["metadata"]["processing_time_ms"],
            "claimllm_confidence": claimllm_result["metadata"]["confidence"],
            "claimllm_model": claimllm_result["metadata"]["model"]
        }
        
        return AnalysisResponse(
            original_question=query.question,
            llm_response=llm_response,
            claims=verified_claims,
            graph_data=graph_data,
            summary=enhanced_summary,
            confidence_analysis=confidence_analysis
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hallucination-detector"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
