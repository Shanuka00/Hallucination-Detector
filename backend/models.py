"""
Data models for the hallucination detection system
"""

from pydantic import BaseModel
from typing import Literal, Optional
from enum import Enum

class VerificationResponse(str, Enum):
    YES = "Yes"
    NO = "No"
    UNCERTAIN = "Uncertain"

class WikipediaStatus(str, Enum):
    SUPPORTS = "Supports"
    CONTRADICTS = "Contradicts"
    UNCLEAR = "Unclear"
    NOT_FOUND = "NotFound"
    NOT_CHECKED = "NotChecked"

class ClaimVerification(BaseModel):
    id: str
    claim: str
    llm1_verification: str
    llm2_verification: str
    llm1_name: Optional[str] = None  # Name of first verifier LLM
    llm2_name: Optional[str] = None  # Name of second verifier LLM
    llm3_name: Optional[str] = None  # Name of third verifier LLM (if voting used)
    llm3_verification: Optional[str] = None  # Third LLM's verdict (if voting used)
    voting_used: bool = False  # Whether 3-way voting was needed
    final_verdict: str = "Uncertain"  # Final verdict after voting
    wikipedia_status: Optional[str] = "NotChecked"
    wikipedia_summary: Optional[str] = None
    is_wikipedia_checked: bool = False
    final_risk_level: Optional[str] = None
    
    def get_risk_level(self) -> Literal["high", "medium", "low"]:
        """
        Determine hallucination risk based on final verdict and Wikipedia check
        """
        # Use final verdict from voting system
        verdict = self.final_verdict.lower()
        
        # Base risk from verdict
        if verdict == "yes":
            base_risk = "low"
        elif verdict == "no":
            base_risk = "high"
        else:  # Uncertain
            base_risk = "medium"
        
        # Apply Wikipedia adjustment if checked
        if self.is_wikipedia_checked and self.wikipedia_status:
            return self._adjust_risk_with_wikipedia(base_risk, self.wikipedia_status)
        
        return base_risk
    
    def _get_base_risk(self, llm1: str, llm2: str) -> Literal["high", "medium", "low"]:
        """Get base risk level from LLM verifiers (legacy method)"""
        # Both disagree (both say No) = High risk
        if llm1 == "no" and llm2 == "no":
            return "high"
        
        # Mixed responses or uncertainty = Medium risk
        if (llm1 == "no" and llm2 in ["yes", "uncertain"]) or \
           (llm2 == "no" and llm1 in ["yes", "uncertain"]) or \
           "uncertain" in [llm1, llm2]:
            return "medium"
        
        # Both agree (both say Yes) = Low risk
        if llm1 == "yes" and llm2 == "yes":
            return "low"
        
        # Default to medium for any other cases
        return "medium"
    
    def _adjust_risk_with_wikipedia(self, base_risk: str, wiki_status: str) -> Literal["high", "medium", "low"]:
        """Adjust risk level based on Wikipedia verification"""
        wiki_status_lower = wiki_status.lower()
        
        if wiki_status_lower == "supports":
            # Wikipedia supports the claim - lower the risk
            if base_risk == "medium":
                return "low"
            # Keep high and low as they are (Wikipedia might not catch all nuances)
            return base_risk
        
        elif wiki_status_lower == "contradicts":
            # Wikipedia contradicts - this is a strong signal of hallucination
            return "high"
        
        elif wiki_status_lower in ["unclear", "notfound"]:
            # Wikipedia doesn't help - keep original assessment
            return base_risk
        
        return base_risk
    
    def get_confidence_score(self) -> float:
        """
        Calculate confidence score (0-1) based on agreement and external verification
        """
        risk = self.get_risk_level()
        base_confidence = {"low": 0.9, "medium": 0.5, "high": 0.1}[risk]
        
        # Boost confidence if Wikipedia was checked and provided clear result
        if self.is_wikipedia_checked and self.wikipedia_status in ["Supports", "Contradicts"]:
            base_confidence = min(0.95, base_confidence + 0.1)
        
        return base_confidence
    
    def should_check_wikipedia(self) -> bool:
        """
        Determine if this claim should be checked with Wikipedia
        Only check medium risk claims to potentially resolve uncertainty
        """
        base_risk = self._get_base_risk(
            self.llm1_verification.lower(),
            self.llm2_verification.lower()
        )
        return base_risk == "medium"

class HallucinationResult(BaseModel):
    total_claims: int
    high_risk_claims: int
    medium_risk_claims: int
    low_risk_claims: int
    overall_confidence: float
    wikipedia_checks_performed: int
    
    @classmethod
    def from_claims(cls, claims: list[ClaimVerification]):
        """
        Create result summary from list of verified claims
        """
        total = len(claims)
        high = sum(1 for c in claims if c.get_risk_level() == "high")
        medium = sum(1 for c in claims if c.get_risk_level() == "medium")
        low = sum(1 for c in claims if c.get_risk_level() == "low")
        wiki_checks = sum(1 for c in claims if c.is_wikipedia_checked)
        
        # Overall confidence is average of individual confidences
        overall_conf = sum(c.get_confidence_score() for c in claims) / total if total > 0 else 0
        
        return cls(
            total_claims=total,
            high_risk_claims=high,
            medium_risk_claims=medium,
            low_risk_claims=low,
            overall_confidence=round(overall_conf, 2),
            wikipedia_checks_performed=wiki_checks
        )
