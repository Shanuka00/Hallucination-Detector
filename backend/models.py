"""
Data models for the hallucination detection system
"""

from pydantic import BaseModel
from typing import Literal
from enum import Enum

class VerificationResponse(str, Enum):
    YES = "Yes"
    NO = "No"
    UNCERTAIN = "Uncertain"

class ClaimVerification(BaseModel):
    id: str
    claim: str
    claude_verification: str
    gemini_verification: str
    
    def get_risk_level(self) -> Literal["high", "medium", "low"]:
        """
        Determine hallucination risk based on verifier agreement
        """
        claude = self.claude_verification.lower()
        gemini = self.gemini_verification.lower()
        
        # Both disagree (both say No) = High risk
        if claude == "no" and gemini == "no":
            return "high"
        
        # Mixed responses or uncertainty = Medium risk
        if (claude == "no" and gemini in ["yes", "uncertain"]) or \
           (gemini == "no" and claude in ["yes", "uncertain"]) or \
           "uncertain" in [claude, gemini]:
            return "medium"
        
        # Both agree (both say Yes) = Low risk
        if claude == "yes" and gemini == "yes":
            return "low"
        
        # Default to medium for any other cases
        return "medium"
    
    def get_confidence_score(self) -> float:
        """
        Calculate confidence score (0-1) based on agreement
        """
        risk = self.get_risk_level()
        if risk == "low":
            return 0.9
        elif risk == "medium":
            return 0.5
        else:  # high
            return 0.1

class HallucinationResult(BaseModel):
    total_claims: int
    high_risk_claims: int
    medium_risk_claims: int
    low_risk_claims: int
    overall_confidence: float
    
    @classmethod
    def from_claims(cls, claims: list[ClaimVerification]):
        """
        Create result summary from list of verified claims
        """
        total = len(claims)
        high = sum(1 for c in claims if c.get_risk_level() == "high")
        medium = sum(1 for c in claims if c.get_risk_level() == "medium")
        low = sum(1 for c in claims if c.get_risk_level() == "low")
        
        # Overall confidence is average of individual confidences
        overall_conf = sum(c.get_confidence_score() for c in claims) / total if total > 0 else 0
        
        return cls(
            total_claims=total,
            high_risk_claims=high,
            medium_risk_claims=medium,
            low_risk_claims=low,
            overall_confidence=round(overall_conf, 2)
        )
