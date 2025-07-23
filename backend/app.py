"""
Hallucination Detection Web Application - Main FastAPI Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import json

from chatgpt_stub import get_chatgpt_response
from claim_extractor import extract_claims
from claim_verifier_stub import verify_with_claude, verify_with_gemini
from graph_builder import build_hallucination_graph
from models import ClaimVerification, HallucinationResult

app = FastAPI(title="Hallucination Detection API", version="1.0.0")

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
    summary: Dict[str, int]

@app.get("/")
async def root():
    return {"message": "Hallucination Detection API is running"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_hallucination(query: UserQuery):
    """
    Main endpoint to analyze potential hallucinations in LLM responses
    """
    try:
        # Step 1: Get simulated ChatGPT response
        llm_response = get_chatgpt_response(query.question)
        
        # Step 2: Extract factual claims
        claims_text = extract_claims(llm_response)
        
        # Step 3: Verify each claim with multiple models
        verified_claims = []
        for i, claim in enumerate(claims_text):
            claude_response = verify_with_claude(claim)
            gemini_response = verify_with_gemini(claim)
            
            verification = ClaimVerification(
                id=f"C{i+1}",
                claim=claim,
                claude_verification=claude_response,
                gemini_verification=gemini_response
            )
            verified_claims.append(verification)
        
        # Step 4: Build hallucination graph
        graph_data = build_hallucination_graph(verified_claims)
        
        # Step 5: Generate summary statistics
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        for claim in verified_claims:
            risk_level = claim.get_risk_level()
            risk_counts[risk_level] += 1
        
        return AnalysisResponse(
            original_question=query.question,
            llm_response=llm_response,
            claims=verified_claims,
            graph_data=graph_data,
            summary=risk_counts
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hallucination-detector"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
