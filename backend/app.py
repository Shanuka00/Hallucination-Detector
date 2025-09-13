"""
Hallucination Detection Web Application - Main FastAPI Backend
Enhanced with REAL LLM APIs and Multi-KG verification
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import json

# Import REAL services
from real_llm_services import (
    get_target_response,
    extract_claims_with_llm,
    verify_batch_with_llm1,
    verify_batch_with_gemini
)
from multi_kg_service import MultiKGService
from graph_builder import build_hallucination_graph
from models import ClaimVerification
from confidence_scorer import ConfidenceScorer

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
    Enhanced endpoint using REAL APIs: Mistral + OpenAI + Gemini + Multi-KG
    """
    try:
        # Step 1: Get target LLM response (Mistral)
        llm_response = get_target_response(query.question)
        
        # Step 2: Extract factual claims using OpenAI
        claims_text = extract_claims_with_llm(llm_response)
        
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
                    "overall_confidence": 0.0
                },
                confidence_analysis={
                    "overall_confidence": 0.0,
                    "total_claims": 0,
                    "claim_details": [],
                    "weights_config": {"alpha": 0.4, "beta": 0.4, "gamma": 0.2}
                }
            )
        
        # Step 3: Verify claims with both real LLMs
        llm1_verifications = verify_batch_with_llm1(claims_text)  # OpenAI o1-preview
        llm2_verifications = verify_batch_with_gemini(claims_text)  # Gemini
        
        verified_claims = []
        for i, claim in enumerate(claims_text):
            llm1_response = llm1_verifications[i] if i < len(llm1_verifications) else "Uncertain"
            llm2_response = llm2_verifications[i] if i < len(llm2_verifications) else "Uncertain"
            
            verification = ClaimVerification(
                id=f"C{i+1}",
                claim=claim,
                llm1_verification=llm1_response,
                llm2_verification=llm2_response
            )
            verified_claims.append(verification)
        
        # Step 4: Check medium-risk claims with Multi-KG external verification
        wikipedia_checks_count = 0
        for claim_verification in verified_claims:
            if claim_verification.should_check_wikipedia():
                # Perform Multi-KG external verification for medium-risk claims
                external_result = multi_kg_service.verify_claim(claim_verification.claim)
                
                claim_verification.wikipedia_status = external_result
                claim_verification.wikipedia_summary = f"Multi-KG consensus: {external_result}"
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
        
        # Add Real API statistics
        enhanced_summary = {
            **risk_counts,
            "wikipedia_checks": wikipedia_checks_count,
            "total_claims": len(verified_claims),
            "overall_confidence": overall_confidence,
            "extraction_model": "gpt-3.5-turbo",
            "llm1_model": "o1-preview", 
            "llm2_model": "gemini-1.5-flash",
            "target_model": "mistral-small"
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
