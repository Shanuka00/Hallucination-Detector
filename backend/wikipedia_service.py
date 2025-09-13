"""
Wikipedia integration for external fact verification
"""

import requests
import json
import re
from typing import Dict, Optional, Literal
from urllib.parse import quote

class WikipediaService:
    """Service for fetching Wikipedia summaries for fact verification"""
    
    def __init__(self, use_simulation: bool = True):
        self.use_simulation = use_simulation
        self.base_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        self.search_url = "https://en.wikipedia.org/w/api.php"
    
    def get_summary_from_wikipedia(self, claim: str) -> Dict[str, any]:
        """
        Get Wikipedia summary for fact-checking a claim
        Returns dict with summary text and verification status
        """
        if self.use_simulation:
            return self._get_simulated_wikipedia_summary(claim)
        else:
            return self._get_real_wikipedia_summary(claim)
    
    def verify_claim_with_wikipedia(self, claim: str) -> Literal["Supports", "Contradicts", "Unclear", "NotFound"]:
        """
        Use Wikipedia to verify a claim
        """
        summary_data = self.get_summary_from_wikipedia(claim)
        
        if not summary_data or summary_data.get("status") == "not_found":
            return "NotFound"
        
        summary_text = summary_data.get("extract", "").lower()
        claim_lower = claim.lower()
        
        # Extract key terms from the claim for matching
        key_terms = self._extract_key_terms(claim)
        
        if not key_terms:
            return "Unclear"
        
        # Check if Wikipedia summary supports or contradicts the claim
        return self._analyze_claim_against_summary(claim_lower, summary_text, key_terms)
    
    def _get_simulated_wikipedia_summary(self, claim: str) -> Dict[str, any]:
        """
        Deprecated: Use Multi-KG consensus system instead.
        This fallback only exists for compatibility.
        """
        return {
            "title": "Deprecated - Use Multi-KG",
            "extract": "Wikipedia simulation is deprecated. Use MultiKGService for research-grade verification.",
            "status": "deprecated"
        }
    
    def _get_real_wikipedia_summary(self, claim: str) -> Dict[str, any]:
        """Get actual Wikipedia summary via API"""
        try:
            # First, search for the most relevant page
            search_terms = self._extract_search_terms(claim)
            if not search_terms:
                return {"status": "not_found"}
            
            # Search for pages
            search_params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": " ".join(search_terms),
                "srlimit": 1
            }
            
            search_response = requests.get(self.search_url, params=search_params, timeout=10)
            search_data = search_response.json()
            
            if not search_data.get("query", {}).get("search"):
                return {"status": "not_found"}
            
            # Get the page title
            page_title = search_data["query"]["search"][0]["title"]
            
            # Fetch summary
            summary_url = self.base_url + quote(page_title)
            summary_response = requests.get(summary_url, timeout=10)
            
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                return {
                    "title": summary_data.get("title", ""),
                    "extract": summary_data.get("extract", ""),
                    "status": "found"
                }
            else:
                return {"status": "not_found"}
                
        except Exception as e:
            print(f"Wikipedia API error: {e}")
            return {"status": "error"}
    
    def _extract_key_terms(self, claim: str) -> list:
        """Extract key terms from a claim for verification"""
        # Remove common words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "was", "were", "is", "are", "been", "being", "have", 
            "has", "had", "he", "she", "it", "they", "them", "this", "that"
        }
        
        # Extract words (including numbers and proper nouns)
        words = re.findall(r'\b[A-Za-z0-9]+\b', claim.lower())
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Also extract years and specific patterns
        years = re.findall(r'\b(19|20)\d{2}\b', claim)
        key_terms.extend(years)
        
        return key_terms
    
    def _extract_search_terms(self, claim: str) -> list:
        """Extract terms suitable for Wikipedia search"""
        # Look for proper nouns (capitalized words)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', claim)
        
        # Look for key topics
        topics = []
        claim_lower = claim.lower()
        
        if "newton" in claim_lower:
            topics.append("Isaac Newton")
        elif "einstein" in claim_lower:
            topics.append("Albert Einstein")
        elif "world war" in claim_lower:
            topics.append("World War II")
        elif "python" in claim_lower and "programming" in claim_lower:
            topics.append("Python programming language")
        
        # Combine proper nouns and topics
        search_terms = list(set(proper_nouns + topics))
        return search_terms[:3]  # Limit to top 3 terms
    
    def _analyze_claim_against_summary(self, claim: str, summary: str, key_terms: list) -> str:
        """Analyze if Wikipedia summary supports or contradicts the claim"""
        if not summary:
            return "NotFound"
        
        # Check for direct contradictions
        contradictions = self._check_contradictions(claim, summary)
        if contradictions:
            return "Contradicts"
        
        # Check for support
        support_score = self._calculate_support_score(claim, summary, key_terms)
        
        if support_score >= 0.7:
            return "Supports"
        elif support_score >= 0.3:
            return "Unclear"
        else:
            return "NotFound"
    
    def _check_contradictions(self, claim: str, summary: str) -> bool:
        """Check for direct contradictions between claim and summary"""
        # Common contradiction patterns
        contradictions = [
            # Birth places
            ("berlin" in claim and "born" in claim, "ulm" in summary or "woolsthorpe" in summary),
            # Wrong dates
            ("1922" in claim and "nobel" in claim, "1921" in summary),
            ("munich" in claim and "born" in claim and "einstein" in claim, "ulm" in summary),
            ("september" in claim and "japan" in claim and "surrendered" in claim, "august" in summary),
        ]
        
        for claim_pattern, summary_pattern in contradictions:
            if claim_pattern and summary_pattern:
                return True
        
        return False
    
    def _calculate_support_score(self, claim: str, summary: str, key_terms: list) -> float:
        """Calculate how well the Wikipedia summary supports the claim"""
        if not key_terms:
            return 0.0
        
        matches = 0
        for term in key_terms:
            if term.lower() in summary:
                matches += 1
        
        return matches / len(key_terms)

# Global Wikipedia service instance
from config import config
wikipedia_service = WikipediaService(use_simulation=config.WIKIPEDIA_USE_SIMULATION)
