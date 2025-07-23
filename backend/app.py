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

# Import new LLM services
from llm_services import llm_service, LLMProvider
from wikipedia_service import wikipedia_service
from graph_builder import build_hallucination_graph
from models import ClaimVerification, HallucinationResult

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
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

class UserQuery(BaseModel):
    question: str

class AnalysisResponse(BaseModel):
    original_question: str
    llm_response: str
    claims: List[ClaimVerification]
    graph_data: Dict[str, Any]
    summary: Dict[str, Any]  # Enhanced to include Wikipedia stats

@app.get("/")
async def root():
    return {"message": "Enhanced Hallucination Detection API is running"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_hallucination(query: UserQuery):
    """
    Enhanced endpoint to analyze potential hallucinations using LLM extraction and verification
    """
    try:
        # Step 1: Get target LLM response (ChatGPT simulation)
        llm_response = llm_service.get_target_response(query.question)
        
        # Step 2: Extract factual claims using LLM (Claude)
        claims_text = llm_service.extract_claims_with_llm(llm_response, LLMProvider.CLAUDE)
        
        if not claims_text:
            # Fallback: no claims found
            return AnalysisResponse(
                original_question=query.question,
                llm_response=llm_response,
                claims=[],
                graph_data={"nodes": [], "edges": [], "metrics": {}},
                summary={"high": 0, "medium": 0, "low": 0, "wikipedia_checks": 0}
            )
        
        # Step 3: Batch verify claims with both models
        claude_verifications = llm_service.verify_batch_with_llm(claims_text, LLMProvider.CLAUDE)
        gemini_verifications = llm_service.verify_batch_with_llm(claims_text, LLMProvider.GEMINI)
        
        # Step 4: Create claim verification objects
        verified_claims = []
        for i, claim in enumerate(claims_text):
            claude_response = claude_verifications[i] if i < len(claude_verifications) else "Uncertain"
            gemini_response = gemini_verifications[i] if i < len(gemini_verifications) else "Uncertain"
            
            verification = ClaimVerification(
                id=f"C{i+1}",
                claim=claim,
                claude_verification=claude_response,
                gemini_verification=gemini_response
            )
            verified_claims.append(verification)
        
        # Step 5: Check medium-risk claims with Wikipedia
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
        
        # Step 6: Build hallucination graph with enhanced data
        graph_data = build_hallucination_graph(verified_claims)
        
        # Step 7: Generate enhanced summary statistics
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        for claim in verified_claims:
            risk_level = claim.get_risk_level()
            risk_counts[risk_level] += 1
        
        # Add Wikipedia statistics
        enhanced_summary = {
            **risk_counts,
            "wikipedia_checks": wikipedia_checks_count,
            "total_claims": len(verified_claims),
            "overall_confidence": sum(c.get_confidence_score() for c in verified_claims) / len(verified_claims) if verified_claims else 0
        }
        
        return AnalysisResponse(
            original_question=query.question,
            llm_response=llm_response,
            claims=verified_claims,
            graph_data=graph_data,
            summary=enhanced_summary
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hallucination-detector"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
