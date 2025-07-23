"""
Extract factual claims from LLM responses using rule-based NLP
"""

import re
from typing import List

def extract_claims(text: str) -> List[str]:
    """
    Extract factual claims from text using sentence parsing and fact detection
    """
    # Split text into sentences
    sentences = split_into_sentences(text)
    
    # Filter for sentences that contain factual claims
    claims = []
    for sentence in sentences:
        if is_factual_claim(sentence):
            # Clean and normalize the sentence
            claim = clean_claim(sentence)
            if claim and len(claim.strip()) > 10:  # Minimum length filter
                claims.append(claim)
    
    return claims

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into individual sentences
    """
    # Basic sentence splitting on periods, exclamation marks, and question marks
    # Handle abbreviations and decimals
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    # Clean up sentences
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            cleaned_sentences.append(sentence)
    
    return cleaned_sentences

def is_factual_claim(sentence: str) -> bool:
    """
    Determine if a sentence contains a factual claim worth verifying
    """
    sentence_lower = sentence.lower()
    
    # Skip sentences that are clearly not factual claims
    skip_patterns = [
        r'^(however|therefore|thus|hence|consequently)',
        r'^(in conclusion|to summarize|in summary)',
        r'^(i think|i believe|i feel|it seems|perhaps|maybe)',
        r'\?$',  # Questions
        r'^(let me|let us|we should|you should)',
    ]
    
    for pattern in skip_patterns:
        if re.search(pattern, sentence_lower):
            return False
    
    # Look for factual claim indicators
    factual_indicators = [
        # Dates and years
        r'\b(19|20)\d{2}\b',
        r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
        
        # Names and proper nouns (capitalized words)
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
        
        # Numbers and measurements
        r'\b\d+(?:\.\d+)?\s*(years?|months?|days?|hours?|minutes?|seconds?)\b',
        r'\b\d+(?:\.\d+)?\s*(degrees?|celsius|fahrenheit|km|miles?|meters?|feet)\b',
        
        # Specific verbs indicating facts
        r'\b(was|were|is|are|born|died|created|invented|discovered|founded|established)\b',
        r'\b(published|released|developed|wrote|served|became|graduated)\b',
        
        # Location indicators
        r'\bin\s+[A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*\b',  # "in Location" or "in City, Country"
        
        # Achievement/award indicators
        r'\b(won|received|awarded|prize|nobel|award)\b',
        
        # Scientific/technical terms
        r'\b(theory|law|principle|equation|formula|theorem)\b',
    ]
    
    # Sentence must contain at least one factual indicator
    for pattern in factual_indicators:
        if re.search(pattern, sentence_lower):
            return True
    
    return False

def clean_claim(sentence: str) -> str:
    """
    Clean and normalize a factual claim
    """
    # Remove extra whitespace
    claim = re.sub(r'\s+', ' ', sentence.strip())
    
    # Ensure proper punctuation
    if not claim.endswith(('.', '!', '?')):
        claim += '.'
    
    # Remove any markdown or formatting
    claim = re.sub(r'\*\*(.*?)\*\*', r'\1', claim)  # Bold
    claim = re.sub(r'\*(.*?)\*', r'\1', claim)      # Italic
    claim = re.sub(r'`(.*?)`', r'\1', claim)        # Code
    
    return claim

def extract_claims_detailed(text: str) -> List[dict]:
    """
    Extract claims with additional metadata for analysis
    """
    sentences = split_into_sentences(text)
    detailed_claims = []
    
    for i, sentence in enumerate(sentences):
        if is_factual_claim(sentence):
            claim = clean_claim(sentence)
            if claim and len(claim.strip()) > 10:
                # Analyze claim characteristics
                claim_info = {
                    "text": claim,
                    "position": i,
                    "contains_date": bool(re.search(r'\b(19|20)\d{2}\b', claim)),
                    "contains_name": bool(re.search(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', claim)),
                    "contains_location": bool(re.search(r'\bin\s+[A-Z][a-z]+', claim.lower())),
                    "contains_number": bool(re.search(r'\b\d+(?:\.\d+)?\b', claim)),
                    "word_count": len(claim.split()),
                }
                detailed_claims.append(claim_info)
    
    return detailed_claims

# Test the extractor with sample text
if __name__ == "__main__":
    sample_text = "Isaac Newton was born in 1643. He discovered gravity in 1687. He was born in Berlin."
    claims = extract_claims(sample_text)
    print("Extracted claims:")
    for i, claim in enumerate(claims, 1):
        print(f"{i}. {claim}")
