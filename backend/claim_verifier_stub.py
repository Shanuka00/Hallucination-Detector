"""
Simulated Claude and Gemini verifier models for claim verification
"""

import re
from typing import Literal

def verify_with_claude(claim: str) -> Literal["Yes", "No", "Uncertain"]:
    """
    Simulate Claude's verification responses with domain knowledge
    """
    claim_lower = claim.lower()
    
    # Newton-related facts
    if "newton" in claim_lower or "he" in claim_lower:  # Handle pronoun references
        if "1643" in claim:
            return "Yes"  # Newton was indeed born in 1643
        elif "berlin" in claim_lower:
            return "No"   # Newton was born in England, not Berlin
        elif "1687" in claim and ("gravity" in claim_lower or "gravitation" in claim_lower):
            return "Yes"  # Principia was published in 1687
        elif "apple" in claim_lower and "gravity" in claim_lower:
            return "Uncertain"  # Apple story is likely apocryphal
        elif "royal society" in claim_lower and "president" in claim_lower:
            return "Yes"  # Newton was president of Royal Society
        elif "calculus" in claim_lower and "principia" in claim_lower:
            return "Yes"  # Newton did invent calculus and write Principia
        elif "1727" in claim and "death" in claim_lower:
            return "Yes"  # Newton died in 1727
    
    # Location-based checks (for context-dependent claims)
    if "berlin" in claim_lower and ("born" in claim_lower or "birth" in claim_lower):
        return "No"  # Most famous historical figures weren't born in Berlin
    
    # Einstein-related facts
    elif "einstein" in claim_lower:
        if "1879" in claim:
            return "Yes"  # Correct birth year
        elif "munich" in claim_lower:
            return "No"   # Einstein was born in Ulm, not Munich
        elif "1922" in claim and "nobel" in claim_lower:
            return "No"   # Einstein won Nobel in 1921, not 1922
        elif "quantum mechanics" in claim_lower and "nobel" in claim_lower:
            return "No"   # Won for photoelectric effect, not quantum mechanics
    
    # World War 2 facts
    elif "world war" in claim_lower or "ww2" in claim_lower:
        if "1939" in claim and "1945" in claim:
            return "Yes"  # Correct duration
        elif "september 1945" in claim_lower and "japan" in claim_lower:
            return "No"   # Japan surrendered in August, not September
    
    # Python programming facts
    elif "python" in claim_lower and ("programming" in claim_lower or "language" in claim_lower):
        if "guido van rossum" in claim_lower and "1991" in claim:
            return "Yes"  # Correct creator and year
        elif "monty python" in claim_lower:
            return "Yes"  # Correctly named after Monty Python
        elif "python 3" in claim_lower and "2008" in claim:
            return "Yes"  # Python 3.0 was indeed released in 2008
    
    # Climate change facts
    elif "climate change" in claim_lower:
        if "1.1" in claim and "temperature" in claim_lower:
            return "Yes"  # Approximately correct temperature increase
        elif "fossil fuels" in claim_lower and "greenhouse" in claim_lower:
            return "Yes"  # Correct primary cause
    
    # Default responses for unrecognized claims
    if any(year in claim for year in ["1643", "1687", "1879", "1939", "1945"]):
        return "Uncertain"  # Be cautious about specific dates
    
    return "Uncertain"

def verify_with_gemini(claim: str) -> Literal["Yes", "No", "Uncertain"]:
    """
    Simulate Gemini's verification responses (sometimes agrees/disagrees with Claude)
    """
    claim_lower = claim.lower()
    
    # Newton-related facts (different perspective from Claude sometimes)
    if "newton" in claim_lower or "he" in claim_lower:  # Handle pronoun references
        if "1643" in claim:
            return "Yes"  # Agrees with Claude on birth year
        elif "berlin" in claim_lower:
            return "No"   # Agrees Newton not born in Berlin
        elif "1687" in claim and ("gravity" in claim_lower or "gravitation" in claim_lower):
            return "Uncertain"  # More cautious about the apple story connection
        elif "apple" in claim_lower and "gravity" in claim_lower:
            return "No"   # More definitive that apple story is myth
        elif "1727" in claim and "death" in claim_lower:
            return "Yes"  # Newton died in 1727
        elif "calculus" in claim_lower and "principia" in claim_lower:
            return "Yes"  # Agrees on Newton's achievements
        elif "royal society" in claim_lower and "president" in claim_lower:
            return "Yes"  # Agrees on Royal Society presidency
    
    # Location-based checks (for context-dependent claims)
    if "berlin" in claim_lower and ("born" in claim_lower or "birth" in claim_lower):
        return "No"  # Most famous historical figures weren't born in Berlin
    
    # Einstein-related facts
    elif "einstein" in claim_lower:
        if "1879" in claim:
            return "Yes"  # Agrees on birth year
        elif "munich" in claim_lower:
            return "No"   # Agrees Einstein not born in Munich
        elif "1922" in claim and "nobel" in claim_lower:
            return "Uncertain"  # Less certain about exact Nobel year
        elif "princeton" in claim_lower and "1933" in claim:
            return "Yes"  # Einstein did move to Princeton in 1933
    
    # World War 2 facts
    elif "world war" in claim_lower:
        if "1939" in claim and "1945" in claim:
            return "Yes"  # Agrees on duration
        elif "may 1945" in claim_lower and "germany" in claim_lower:
            return "Yes"  # Germany surrendered in May 1945
        elif "september" in claim_lower and "japan" in claim_lower:
            return "No"   # Japan surrendered in August
    
    # Python programming facts
    elif "python" in claim_lower:
        if "guido" in claim_lower and "1991" in claim:
            return "Yes"  # Agrees on creator and year
        elif "interpreted" in claim_lower:
            return "Yes"  # Python is interpreted
        elif "backward compatible" in claim_lower and "not" in claim_lower:
            return "Yes"  # Python 3 is not backward compatible with Python 2
    
    # Climate change facts
    elif "climate" in claim_lower:
        if "temperature" in claim_lower and "increased" in claim_lower:
            return "Yes"  # Agrees on temperature increase
        elif "19th century" in claim_lower:
            return "Yes"  # Agrees on timeframe
    
    # Default more conservative responses
    if any(word in claim_lower for word in ["approximately", "generally", "often", "usually"]):
        return "Yes"  # More lenient with qualified statements
    
    return "Uncertain"

def get_verification_explanation(claim: str, model: str, response: str) -> str:
    """
    Generate explanation for why a model gave a particular verification response
    """
    explanations = {
        ("claude", "Yes"): f"Claude verified this claim as factually accurate based on historical records.",
        ("claude", "No"): f"Claude identified this claim as factually incorrect.",
        ("claude", "Uncertain"): f"Claude could not definitively verify this claim due to insufficient evidence or conflicting sources.",
        ("gemini", "Yes"): f"Gemini confirmed this claim matches established facts.",
        ("gemini", "No"): f"Gemini determined this claim contains factual errors.",
        ("gemini", "Uncertain"): f"Gemini expressed uncertainty about this claim's accuracy."
    }
    
    return explanations.get((model.lower(), response), f"{model} responded: {response}")
