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
