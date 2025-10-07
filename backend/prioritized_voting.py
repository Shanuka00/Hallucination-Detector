"""
Prioritized LLM Voting System for Hallucination Detection
Implements hierarchical verification with conflict resolution
"""

from typing import List, Dict, Tuple, Literal
from real_llm_services import (
    verify_batch_with_openai,
    verify_batch_with_anthropic,
    verify_batch_with_gemini,
    verify_batch_with_deepseek
)

# Priority order for factual verification (from research)
LLM_PRIORITY_ORDER = ["openai", "anthropic", "gemini", "deepseek"]

# Map LLM names to verification functions
LLM_VERIFIERS = {
    "openai": verify_batch_with_openai,
    "anthropic": verify_batch_with_anthropic,
    "gemini": verify_batch_with_gemini,
    "deepseek": verify_batch_with_deepseek,
}


class PrioritizedVotingSystem:
    """
    Implements prioritized LLM voting for claim verification
    """
    
    def __init__(self):
        self.priority_order = LLM_PRIORITY_ORDER
        self.verifiers = LLM_VERIFIERS
    
    def get_verification_llms(self, target_llm: str) -> List[str]:
        """
        Get the prioritized list of LLMs for verification, excluding the target LLM.
        Returns first 4 from priority list (or 3 if target is in the list).
        
        Args:
            target_llm: The target LLM being tested (to exclude from verification)
        
        Returns:
            List of LLM names to use for verification
        """
        target_lower = target_llm.lower() if target_llm else ""
        
        # Get verification LLMs excluding target
        verification_llms = [
            llm for llm in self.priority_order 
            if llm != target_lower
        ]
        
        # Return first 4 (we'll use first 2, then 3rd if needed)
        return verification_llms[:4]
    
    def verify_claims_with_voting(
        self, 
        claims: List[str], 
        target_llm: str = "mistral"
    ) -> List[Dict[str, str]]:
        """
        Verify claims using prioritized LLM voting system.
        
        Process:
        1. Send claims to first two priority LLMs (excluding target)
        2. If they agree (Yes/Yes, No/No, Uncertain/Uncertain), use that result
        3. If they contradict, send to next priority LLM
        4. Final logic:
           - If 2 out of 3 agree, use the majority
           - If all 3 different, mark as Uncertain
        
        Args:
            claims: List of factual claims to verify
            target_llm: The target LLM being tested
        
        Returns:
            List of dictionaries with verification results for each claim
        """
        if not claims:
            return []
        
        # Get prioritized verification LLMs
        verification_llms = self.get_verification_llms(target_llm)
        
        if len(verification_llms) < 2:
            raise ValueError("Need at least 2 LLMs for verification")
        
        # Step 1: Get verifications from first two LLMs
        llm1_name = verification_llms[0]
        llm2_name = verification_llms[1]
        
        print(f"Verifying with {llm1_name} and {llm2_name}...")
        llm1_results = self.verifiers[llm1_name](claims)
        llm2_results = self.verifiers[llm2_name](claims)
        
        # Step 2: Compare results and identify conflicts
        results = []
        contradicted_indices = []
        
        for i, claim in enumerate(claims):
            result1 = llm1_results[i] if i < len(llm1_results) else "Uncertain"
            result2 = llm2_results[i] if i < len(llm2_results) else "Uncertain"
            
            # Normalize responses
            result1 = self._normalize_response(result1)
            result2 = self._normalize_response(result2)
            
            # Check if they agree
            if result1 == result2:
                # Agreement - use this result
                results.append({
                    "claim": claim,
                    "llm1_name": llm1_name,
                    "llm1_result": result1,
                    "llm2_name": llm2_name,
                    "llm2_result": result2,
                    "llm3_name": None,
                    "llm3_result": None,
                    "final_verdict": result1,
                    "voting_used": False
                })
            else:
                # Contradiction - mark for third LLM verification
                contradicted_indices.append(i)
                results.append({
                    "claim": claim,
                    "llm1_name": llm1_name,
                    "llm1_result": result1,
                    "llm2_name": llm2_name,
                    "llm2_result": result2,
                    "llm3_name": None,
                    "llm3_result": None,
                    "final_verdict": "Uncertain",  # Temporary
                    "voting_used": True
                })
        
        # Step 3: Resolve contradictions with third LLM
        if contradicted_indices and len(verification_llms) >= 3:
            llm3_name = verification_llms[2]
            contradicted_claims = [claims[i] for i in contradicted_indices]
            
            print(f"Resolving {len(contradicted_claims)} contradictions with {llm3_name}...")
            llm3_results = self.verifiers[llm3_name](contradicted_claims)
            
            # Apply voting logic
            for idx, global_idx in enumerate(contradicted_indices):
                result1 = results[global_idx]["llm1_result"]
                result2 = results[global_idx]["llm2_result"]
                result3 = self._normalize_response(
                    llm3_results[idx] if idx < len(llm3_results) else "Uncertain"
                )
                
                # Update with third LLM result
                results[global_idx]["llm3_name"] = llm3_name
                results[global_idx]["llm3_result"] = result3
                
                # Apply voting logic
                final_verdict = self._apply_voting_logic(result1, result2, result3)
                results[global_idx]["final_verdict"] = final_verdict
        
        return results
    
    def _normalize_response(self, response: str) -> Literal["Yes", "No", "Uncertain"]:
        """Normalize LLM response to Yes/No/Uncertain"""
        response_lower = response.lower().strip()
        
        if response_lower in ["yes", "true", "correct", "supported", "agree"]:
            return "Yes"
        elif response_lower in ["no", "false", "incorrect", "contradicted", "disagree"]:
            return "No"
        else:
            return "Uncertain"
    
    def _apply_voting_logic(
        self, 
        result1: str, 
        result2: str, 
        result3: str
    ) -> Literal["Yes", "No", "Uncertain"]:
        """
        Apply voting logic to three LLM results.
        - If 2 or more agree, use that result
        - If all 3 are different, mark as Uncertain
        """
        results = [result1, result2, result3]
        
        # Count occurrences
        yes_count = results.count("Yes")
        no_count = results.count("No")
        uncertain_count = results.count("Uncertain")
        
        # Majority voting
        if yes_count >= 2:
            return "Yes"
        elif no_count >= 2:
            return "No"
        elif uncertain_count >= 2:
            return "Uncertain"
        else:
            # All three are different - mark as Uncertain
            return "Uncertain"


# Global instance
prioritized_voting_system = PrioritizedVotingSystem()


# Convenience function
def verify_with_prioritized_voting(
    claims: List[str], 
    target_llm: str = "mistral"
) -> List[Dict[str, str]]:
    """
    Verify claims using the prioritized voting system.
    
    Args:
        claims: List of factual claims to verify
        target_llm: The target LLM being tested
    
    Returns:
        List of verification results with voting details
    """
    return prioritized_voting_system.verify_claims_with_voting(claims, target_llm)
