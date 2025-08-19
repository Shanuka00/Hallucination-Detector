"""
Advanced Confidence Scoring System for Individual Claims and Overall Response
Implements the mathematical formulas for confidence calculation based on:
- Cross-Model Score (agreement between LLMs)
- External Score (Wikipedia verification)
- Context Score (claim complexity)
"""

import re
from typing import List, Dict, Tuple
from models import ClaimVerification
import math

class ConfidenceScorer:
    """
    Advanced confidence scoring system for hallucination detection
    """
    
    def __init__(self, alpha: float = 0.4, beta: float = 0.4, gamma: float = 0.2):
        """
        Initialize with configurable weights
        
        Args:
            alpha: Weight for Cross-Model Score (default 0.4)
            beta: Weight for External Score (default 0.4) 
            gamma: Weight for Context Score (default 0.2)
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        
        # Ensure weights sum to 1.0
        total_weight = alpha + beta + gamma
        if abs(total_weight - 1.0) > 0.001:
            print(f"Warning: Weights sum to {total_weight}, normalizing to 1.0")
            self.alpha = alpha / total_weight
            self.beta = beta / total_weight
            self.gamma = gamma / total_weight
    
    def calculate_cross_model_score(self, llm1_response: str, llm2_response: str) -> float:
        """
        Calculate Cross-Model Score based on agreement between LLMs
        
        Args:
            llm1_response: Response from first LLM verifier
            llm2_response: Response from second LLM verifier
            
        Returns:
            Score between 0.0 and 1.0
        """
        llm1 = llm1_response.lower().strip()
        llm2 = llm2_response.lower().strip()
        
        # Perfect agreement cases
        if llm1 == llm2:
            if llm1 == "yes":
                return 0.9  # High confidence when both agree on "Yes"
            elif llm1 == "no":
                return 0.1  # Low confidence when both agree on "No" (likely hallucination)
            else:  # both uncertain
                return 0.3  # Low-medium confidence when both uncertain
        
        # Disagreement cases
        if (llm1 == "yes" and llm2 == "no") or (llm1 == "no" and llm2 == "yes"):
            return 0.2  # Low confidence on direct disagreement
        
        # Mixed with uncertain
        if "uncertain" in [llm1, llm2]:
            other_response = llm2 if llm1 == "uncertain" else llm1
            if other_response == "yes":
                return 0.5  # Medium confidence
            elif other_response == "no":
                return 0.3  # Low-medium confidence
        
        return 0.4  # Default for any other cases
    
    def calculate_external_score(self, wikipedia_status: str, is_checked: bool) -> float:
        """
        Calculate External Score based on Wikipedia verification
        
        Args:
            wikipedia_status: Wikipedia verification status
            is_checked: Whether Wikipedia was actually checked
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not is_checked:
            return 0.5  # Neutral score when not checked
        
        status_lower = wikipedia_status.lower()
        
        if status_lower == "supports":
            return 0.9  # High confidence when Wikipedia supports
        elif status_lower == "contradicts":
            return 0.1  # Low confidence when Wikipedia contradicts
        elif status_lower == "unclear":
            return 0.4  # Low-medium confidence when unclear
        elif status_lower in ["notfound", "not_found"]:
            return 0.3  # Lower confidence when no Wikipedia info found
        else:
            return 0.5  # Default neutral score
    
    def calculate_context_score(self, claim: str) -> float:
        """
        Calculate Context Score based on claim complexity and characteristics
        
        Args:
            claim: The claim text to analyze
            
        Returns:
            Score between 0.0 and 1.0
        """
        claim_lower = claim.lower()
        
        # Start with base score
        score = 0.5
        
        # Simple factual patterns get higher scores
        patterns = {
            # Dates and years
            r'\b(19|20)\d{2}\b': 0.2,  # Contains year
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b': 0.3,  # Specific dates
            
            # Names and places
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b': 0.1,  # Proper names
            r'\bin\s+[A-Z][a-z]+\b': 0.1,  # Location references
            
            # Numbers and measurements
            r'\b\d+(\.\d+)?\s*(km|miles|meters|feet|kg|pounds|years|months|days)\b': 0.15,  # Measurements
            
            # Scientific terms
            r'\b(theory|law|principle|equation|formula)\s+of\b': 0.1,  # Scientific concepts
        }
        
        for pattern, bonus in patterns.items():
            if re.search(pattern, claim_lower):
                score += bonus
        
        # Complexity penalties
        word_count = len(claim.split())
        if word_count > 20:
            score -= 0.2  # Penalty for very long claims
        elif word_count > 15:
            score -= 0.1  # Smaller penalty for long claims
        elif word_count < 5:
            score += 0.1  # Bonus for concise claims
        
        # Subjective language reduces confidence
        subjective_words = ['probably', 'might', 'could', 'seems', 'appears', 'likely', 'perhaps', 'possibly']
        subjective_count = sum(1 for word in subjective_words if word in claim_lower)
        score -= subjective_count * 0.1
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))
    
    def calculate_claim_confidence(self, claim_verification: ClaimVerification) -> Tuple[float, Dict[str, float]]:
        """
        Calculate confidence for a single claim using the formula:
        Confidence = α × CrossModelScore + β × ExternalScore + γ × ContextScore
        
        Args:
            claim_verification: ClaimVerification object
            
        Returns:
            Tuple of (confidence_score, component_scores)
        """
        # Calculate component scores
        cross_model_score = self.calculate_cross_model_score(
            claim_verification.llm1_verification,
            claim_verification.llm2_verification
        )
        
        external_score = self.calculate_external_score(
            claim_verification.wikipedia_status or "NotChecked",
            claim_verification.is_wikipedia_checked
        )
        
        context_score = self.calculate_context_score(claim_verification.claim)
        
        # Apply the confidence formula
        confidence = (
            self.alpha * cross_model_score +
            self.beta * external_score +
            self.gamma * context_score
        )
        
        component_scores = {
            'cross_model_score': cross_model_score,
            'external_score': external_score,
            'context_score': context_score,
            'cross_model_weighted': self.alpha * cross_model_score,
            'external_weighted': self.beta * external_score,
            'context_weighted': self.gamma * context_score
        }
        
        return confidence, component_scores
    
    def calculate_claim_weight(self, claim: str) -> float:
        """
        Calculate weight for a claim based on its importance/complexity
        
        Args:
            claim: The claim text
            
        Returns:
            Weight value (higher for more important claims)
        """
        # Base weight
        weight = 1.0
        
        # Length-based weighting (longer claims might be more important)
        word_count = len(claim.split())
        if word_count > 15:
            weight += 0.3
        elif word_count > 10:
            weight += 0.2
        elif word_count < 5:
            weight -= 0.2
        
        # Important topic keywords
        important_keywords = [
            'theory', 'discovery', 'invention', 'principle', 'law',
            'born', 'died', 'published', 'awarded', 'prize',
            'president', 'founded', 'established', 'created'
        ]
        
        claim_lower = claim.lower()
        keyword_count = sum(1 for keyword in important_keywords if keyword in claim_lower)
        weight += keyword_count * 0.1
        
        # Ensure reasonable bounds
        return max(0.5, min(2.0, weight))
    
    def calculate_overall_confidence(self, verified_claims: List[ClaimVerification]) -> Tuple[float, Dict]:
        """
        Calculate overall confidence for the entire response using weighted average:
        OverallConfidence = Σ(Confidence_i × Weight_i) / Σ(Weight_i)
        
        Args:
            verified_claims: List of ClaimVerification objects
            
        Returns:
            Tuple of (overall_confidence, detailed_analysis)
        """
        if not verified_claims:
            return 0.0, {}
        
        total_weighted_confidence = 0.0
        total_weights = 0.0
        claim_details = []
        
        for i, claim in enumerate(verified_claims):
            # Calculate individual claim confidence
            confidence, components = self.calculate_claim_confidence(claim)
            
            # Calculate claim weight
            weight = self.calculate_claim_weight(claim.claim)
            
            # Add to totals
            weighted_confidence = confidence * weight
            total_weighted_confidence += weighted_confidence
            total_weights += weight
            
            # Store details for analysis
            claim_details.append({
                'claim_id': claim.id,
                'claim_text': claim.claim,
                'confidence': confidence,
                'weight': weight,
                'weighted_confidence': weighted_confidence,
                'components': components,
                'llm1_response': claim.llm1_verification,
                'llm2_response': claim.llm2_verification,
                'wikipedia_status': claim.wikipedia_status,
                'wikipedia_checked': claim.is_wikipedia_checked
            })
        
        # Calculate overall confidence
        overall_confidence = total_weighted_confidence / total_weights if total_weights > 0 else 0.0
        
        # Create detailed analysis
        analysis = {
            'overall_confidence': overall_confidence,
            'total_claims': len(verified_claims),
            'total_weights': total_weights,
            'total_weighted_confidence': total_weighted_confidence,
            'weights_config': {
                'alpha': self.alpha,
                'beta': self.beta,
                'gamma': self.gamma
            },
            'claim_details': claim_details,
            'summary_stats': {
                'avg_confidence': sum(detail['confidence'] for detail in claim_details) / len(claim_details),
                'min_confidence': min(detail['confidence'] for detail in claim_details),
                'max_confidence': max(detail['confidence'] for detail in claim_details),
                'avg_weight': sum(detail['weight'] for detail in claim_details) / len(claim_details)
            }
        }
        
        return overall_confidence, analysis

def format_confidence_analysis(overall_confidence: float, analysis: Dict) -> str:
    """
    Format the confidence analysis into a readable report
    """
    report = []
    
    report.append("=" * 80)
    report.append("🎯 DETAILED CONFIDENCE SCORING ANALYSIS")
    report.append("=" * 80)
    report.append("")
    
    # Configuration
    weights = analysis['weights_config']
    report.append("📊 SCORING CONFIGURATION:")
    report.append(f"   α (Cross-Model Weight): {weights['alpha']:.1f}")
    report.append(f"   β (External Weight): {weights['beta']:.1f}")
    report.append(f"   γ (Context Weight): {weights['gamma']:.1f}")
    report.append("")
    
    # Individual claim analysis
    report.append("🔍 INDIVIDUAL CLAIM ANALYSIS:")
    for detail in analysis['claim_details']:
        comp = detail['components']
        report.append(f"   {detail['claim_id']}: {detail['claim_text']}")
        report.append(f"       LLM1: {detail['llm1_response']} | LLM2: {detail['llm2_response']}")
        if detail['wikipedia_checked']:
            report.append(f"       Wikipedia: {detail['wikipedia_status']}")
        
        report.append(f"       📈 Cross-Model Score: {comp['cross_model_score']:.3f} (weighted: {comp['cross_model_weighted']:.3f})")
        report.append(f"       🌐 External Score: {comp['external_score']:.3f} (weighted: {comp['external_weighted']:.3f})")
        report.append(f"       🧠 Context Score: {comp['context_score']:.3f} (weighted: {comp['context_weighted']:.3f})")
        report.append(f"       ⚖️ Claim Weight: {detail['weight']:.2f}")
        report.append(f"       🎯 Final Confidence: {detail['confidence']:.3f}")
        report.append(f"       📊 Weighted Contribution: {detail['weighted_confidence']:.3f}")
        report.append("")
    
    # Calculation details
    report.append("🧮 OVERALL CONFIDENCE CALCULATION:")
    report.append(f"   Formula: OverallConfidence = Σ(Confidence_i × Weight_i) / Σ(Weight_i)")
    report.append(f"   Total Weighted Confidence: {analysis['total_weighted_confidence']:.3f}")
    report.append(f"   Total Weights: {analysis['total_weights']:.3f}")
    report.append(f"   Overall Confidence: {analysis['total_weighted_confidence']:.3f} ÷ {analysis['total_weights']:.3f} = {overall_confidence:.3f}")
    report.append("")
    
    # Summary statistics
    stats = analysis['summary_stats']
    report.append("📈 SUMMARY STATISTICS:")
    report.append(f"   Average Confidence: {stats['avg_confidence']:.3f}")
    report.append(f"   Minimum Confidence: {stats['min_confidence']:.3f}")
    report.append(f"   Maximum Confidence: {stats['max_confidence']:.3f}")
    report.append(f"   Average Weight: {stats['avg_weight']:.2f}")
    report.append("")
    
    # Final assessment
    report.append("🎯 FINAL ASSESSMENT:")
    if overall_confidence >= 0.8:
        assessment = "🟢 HIGH CONFIDENCE - Response appears highly reliable"
    elif overall_confidence >= 0.6:
        assessment = "🟡 MEDIUM CONFIDENCE - Response has moderate reliability"
    elif overall_confidence >= 0.4:
        assessment = "🟠 LOW-MEDIUM CONFIDENCE - Response has concerning elements"
    else:
        assessment = "🔴 LOW CONFIDENCE - Response likely contains significant hallucinations"
    
    report.append(f"   Overall Confidence Score: {overall_confidence:.3f}")
    report.append(f"   Assessment: {assessment}")
    
    return "\n".join(report)
