"""
Demonstration of the Confidence Scoring System with Example Calculations
This script shows the detailed mathematical calculations for the confidence scoring examples.
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from confidence_scorer import ConfidenceScorer
from models import ClaimVerification

def demonstrate_example_calculations():
    """
    Demonstrate the confidence scoring with the specific examples from the requirements
    """
    print("=" * 80)
    print("🎯 CONFIDENCE SCORING SYSTEM - EXAMPLE CALCULATIONS")
    print("=" * 80)
    print()
    
    # Initialize confidence scorer with the specified weights
    scorer = ConfidenceScorer(alpha=0.4, beta=0.4, gamma=0.2)
    
    print("📊 CONFIGURATION:")
    print(f"   α (Cross-Model Weight): {scorer.alpha}")
    print(f"   β (External Weight): {scorer.beta}")
    print(f"   γ (Context Weight): {scorer.gamma}")
    print(f"   Formula: Confidence = α × CrossModelScore + β × ExternalScore + γ × ContextScore")
    print()
    
    # Example 1: "The Eiffel Tower is in Paris"
    print("🗼 EXAMPLE 1: High Confidence Claim")
    claim1 = ClaimVerification(
        id="C1",
        claim="The Eiffel Tower is in Paris",
        llm1_verification="Yes",
        llm2_verification="Yes",
        wikipedia_status="Supports",
        is_wikipedia_checked=True
    )
    
    confidence1, components1 = scorer.calculate_claim_confidence(claim1)
    
    print(f"   Claim: {claim1.claim}")
    print(f"   LLM1: {claim1.llm1_verification} | LLM2: {claim1.llm2_verification}")
    print(f"   Wikipedia: {claim1.wikipedia_status}")
    print()
    print("   📊 COMPONENT SCORES:")
    print(f"   Cross-Model Score = {components1['cross_model_score']:.1f} (Both models agree on 'Yes')")
    print(f"   External Score = {components1['external_score']:.1f} (Wikipedia verifies)")
    print(f"   Context Score = {components1['context_score']:.1f} (Simple factual claim)")
    print()
    print("   🧮 CALCULATION:")
    print(f"   Confidence = {scorer.alpha} × {components1['cross_model_score']:.1f} + {scorer.beta} × {components1['external_score']:.1f} + {scorer.gamma} × {components1['context_score']:.1f}")
    print(f"   Confidence = {components1['cross_model_weighted']:.2f} + {components1['external_weighted']:.2f} + {components1['context_weighted']:.2f}")
    print(f"   Confidence = {confidence1:.2f}")
    print()
    
    # Example 2: "Einstein invented time travel"
    print("🚫 EXAMPLE 2: Low Confidence Claim")
    claim2 = ClaimVerification(
        id="C2", 
        claim="Einstein invented time travel",
        llm1_verification="No",
        llm2_verification="No",
        wikipedia_status="Contradicts",
        is_wikipedia_checked=True
    )
    
    confidence2, components2 = scorer.calculate_claim_confidence(claim2)
    
    print(f"   Claim: {claim2.claim}")
    print(f"   LLM1: {claim2.llm1_verification} | LLM2: {claim2.llm2_verification}")
    print(f"   Wikipedia: {claim2.wikipedia_status}")
    print()
    print("   📊 COMPONENT SCORES:")
    print(f"   Cross-Model Score = {components2['cross_model_score']:.1f} (Both models disagree with claim)")
    print(f"   External Score = {components2['external_score']:.1f} (Wikipedia contradicts)")
    print(f"   Context Score = {components2['context_score']:.1f} (Complex claim)")
    print()
    print("   🧮 CALCULATION:")
    print(f"   Confidence = {scorer.alpha} × {components2['cross_model_score']:.1f} + {scorer.beta} × {components2['external_score']:.1f} + {scorer.gamma} × {components2['context_score']:.1f}")
    print(f"   Confidence = {components2['cross_model_weighted']:.2f} + {components2['external_weighted']:.2f} + {components2['context_weighted']:.2f}")
    print(f"   Confidence = {confidence2:.2f}")
    print()
    
    # Calculate Overall Confidence for the response
    print("🎯 OVERALL CONFIDENCE CALCULATION:")
    print()
    
    verified_claims = [claim1, claim2]
    overall_confidence, analysis = scorer.calculate_overall_confidence(verified_claims)
    
    print("   Individual Claim Confidences:")
    for i, detail in enumerate(analysis['claim_details'], 1):
        print(f"   Claim {i}: {detail['confidence']:.2f}")
    print()
    
    print("   Claim Weights (based on complexity/importance):")
    for i, detail in enumerate(analysis['claim_details'], 1):
        print(f"   Claim {i}: {detail['weight']:.1f}")
    print()
    
    print("   Weighted Contributions:")
    for i, detail in enumerate(analysis['claim_details'], 1):
        print(f"   Claim {i}: {detail['confidence']:.2f} × {detail['weight']:.1f} = {detail['weighted_confidence']:.3f}")
    print()
    
    print("   📊 FINAL CALCULATION:")
    print(f"   Formula: OverallConfidence = Σ(Confidence_i × Weight_i) / Σ(Weight_i)")
    print(f"   OverallConfidence = ({analysis['claim_details'][0]['weighted_confidence']:.3f} + {analysis['claim_details'][1]['weighted_confidence']:.3f}) / ({analysis['claim_details'][0]['weight']:.1f} + {analysis['claim_details'][1]['weight']:.1f})")
    print(f"   OverallConfidence = {analysis['total_weighted_confidence']:.3f} / {analysis['total_weights']:.1f}")
    print(f"   OverallConfidence = {overall_confidence:.3f}")
    print()
    
    # Assessment
    if overall_confidence >= 0.8:
        assessment = "🟢 HIGH CONFIDENCE"
    elif overall_confidence >= 0.6:
        assessment = "🟡 MEDIUM CONFIDENCE"
    elif overall_confidence >= 0.4:
        assessment = "🟠 LOW-MEDIUM CONFIDENCE"
    else:
        assessment = "🔴 LOW CONFIDENCE"
    
    print(f"   🎯 FINAL ASSESSMENT: {assessment}")
    print(f"   Overall Confidence Score: {overall_confidence:.3f}")
    print()
    
    # Evaluation Metrics Example
    print("📊 EVALUATION METRICS:")
    print()
    print("   For a dataset with known hallucinations, the system calculates:")
    print("   • Precision: % of flagged claims that are actually hallucinations")
    print("   • Recall: % of actual hallucinations that were flagged")  
    print("   • F1-Score: Harmonic mean of precision and recall")
    print()
    print("   Example with 100 claims:")
    print("   • True Hallucinations: 20")
    print("   • System Flagged (Confidence < 0.5): 25")
    print("   • Correctly Flagged Hallucinations: 18")
    print()
    print("   Precision = 18/25 = 0.72 (72%)")
    print("   Recall = 18/20 = 0.90 (90%)")
    print("   F1-Score = 2 × (0.72 × 0.90) / (0.72 + 0.90) = 0.80")
    print()

if __name__ == "__main__":
    demonstrate_example_calculations()
