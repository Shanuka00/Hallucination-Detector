"""
Demonstration script for the Hallucination Detection System
Run this to see the system in action without the web interface
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from targetllm_stub import get_targetllm_response
from claimllm_stub import extract_claims_with_claimllm, simulate_claimllm_api_call
from claim_verifier_stub import verify_with_llm1, verify_with_llm2
from models import ClaimVerification
from graph_builder import build_hallucination_graph

def demonstrate_analysis(question):
    """
    Demonstrate the complete hallucination detection process
    """
    print("=" * 80)
    print("🧠 HALLUCINATION DETECTION SYSTEM DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Step 1: Get LLM response
    print("1️⃣ USER QUESTION:")
    print(f"   {question}")
    print()
    
    print("2️⃣ TARGETLLM RESPONSE:")
    llm_response = get_targetllm_response(question)
    print(f"   {llm_response}")
    print()
    
    # Step 2: Extract claims using ClaimLLM
    print("3️⃣ CLAIMLLM API CALL FOR CLAIM EXTRACTION:")
    claimllm_result = simulate_claimllm_api_call(llm_response)
    claims_text = claimllm_result["claims"]
    
    print(f"   🔗 API Call Status: {claimllm_result['status']}")
    print(f"   🤖 ClaimLLM Model: {claimllm_result['metadata']['model']}")
    print(f"   ⏱️ Processing Time: {claimllm_result['metadata']['processing_time_ms']}ms")
    print(f"   📊 Claims Extracted: {claimllm_result['total_claims_extracted']}")
    print(f"   🎯 Extraction Confidence: {claimllm_result['metadata']['confidence']}")
    print()
    
    print("4️⃣ EXTRACTED FACTUAL CLAIMS:")
    
    if not claims_text:
        print("   No factual claims detected.")
        return
    
    for i, claim in enumerate(claims_text, 1):
        print(f"   C{i}: {claim}")
    print()
    
    # Step 3: Verify claims
    print("5️⃣ CLAIM VERIFICATION:")
    verified_claims = []
    
    for i, claim in enumerate(claims_text):
        llm1_response = verify_with_llm1(claim)
        llm2_response = verify_with_llm2(claim)
        
        verification = ClaimVerification(
            id=f"C{i+1}",
            claim=claim,
            llm1_verification=llm1_response,
            llm2_verification=llm2_response
        )
        verified_claims.append(verification)
        
        risk_level = verification.get_risk_level().upper()
        confidence = verification.get_confidence_score()
        
        # Color coding for terminal output
        risk_colors = {
            "HIGH": "\033[91m❌",    # Red
            "MEDIUM": "\033[93m⚠️",  # Yellow  
            "LOW": "\033[92m✅"      # Green
        }
        reset_color = "\033[0m"
        
        print(f"   C{i+1}: {claim}")
        print(f"       LLM1: {llm1_response}")
        print(f"       LLM2: {llm2_response}")
        print(f"       Risk Level: {risk_colors.get(risk_level, '❓')} {risk_level} RISK{reset_color}")
        print(f"       Confidence: {confidence:.2f}")
        print()
    
    # Step 4: Generate summary
    print("6️⃣ RISK ASSESSMENT SUMMARY:")
    
    risk_counts = {"high": 0, "medium": 0, "low": 0}
    for claim in verified_claims:
        risk_level = claim.get_risk_level()
        risk_counts[risk_level] += 1
    
    total_claims = len(verified_claims)
    print(f"   Total Claims: {total_claims}")
    print(f"   🔴 High Risk: {risk_counts['high']} ({risk_counts['high']/total_claims*100:.1f}%)")
    print(f"   🟡 Medium Risk: {risk_counts['medium']} ({risk_counts['medium']/total_claims*100:.1f}%)")
    print(f"   🟢 Low Risk: {risk_counts['low']} ({risk_counts['low']/total_claims*100:.1f}%)")
    
    # Overall assessment
    risk_score = (
        risk_counts["high"] * 1.0 +
        risk_counts["medium"] * 0.5 +
        risk_counts["low"] * 0.1
    ) / total_claims
    
    if risk_score > 0.7:
        overall_assessment = "\033[91m🚨 HIGH RISK - Response likely contains hallucinations\033[0m"
    elif risk_score > 0.4:
        overall_assessment = "\033[93m⚠️ MEDIUM RISK - Some claims may be inaccurate\033[0m"
    else:
        overall_assessment = "\033[92m✅ LOW RISK - Response appears factually accurate\033[0m"
    
    print(f"   Overall Assessment: {overall_assessment}")
    print()
    
    # Step 5: Graph metrics
    print("7️⃣ GRAPH ANALYSIS:")
    graph_data = build_hallucination_graph(verified_claims)
    metrics = graph_data['metrics']
    
    print(f"   Connected Components: {metrics['connected_components']}")
    print(f"   Average Confidence: {metrics['average_confidence']:.2f}")
    print(f"   Graph Density: {metrics['density']:.2f}")
    print(f"   Risk Assessment: {metrics['risk_assessment']}")
    print()

def run_demo():
    """
    Run demonstration with multiple sample questions
    """
    sample_questions = [
        "Tell me about Isaac Newton",
        "What do you know about Albert Einstein?", 
        "Explain World War 2",
        "Describe Python programming language",
        "What is climate change?"
    ]
    
    for i, question in enumerate(sample_questions, 1):
        demonstrate_analysis(question)
        
        if i < len(sample_questions):
            print("\n" + "🔄 " * 40)
            input("Press Enter to continue to the next example...")
            print()

def interactive_demo():
    """
    Interactive mode where user can enter their own questions
    """
    print("🔬 INTERACTIVE HALLUCINATION DETECTION")
    print("Enter questions to analyze for potential hallucinations.")
    print("Type 'quit' to exit, 'demo' to run sample questions.")
    print()
    
    while True:
        question = input("Enter your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        elif question.lower() == 'demo':
            run_demo()
            continue
        elif not question:
            print("Please enter a question or 'quit' to exit.")
            continue
        
        try:
            demonstrate_analysis(question)
            print("\n" + "-" * 80)
        except Exception as e:
            print(f"❌ Error analyzing question: {e}")
        
        print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hallucination Detection System Demo")
    parser.add_argument("--mode", choices=["demo", "interactive"], default="interactive",
                       help="Run mode: 'demo' for sample questions, 'interactive' for user input")
    parser.add_argument("--question", type=str, help="Single question to analyze")
    
    args = parser.parse_args()
    
    print("🧠 HALLUCINATION DETECTION SYSTEM")
    print("Detecting potential factual errors in LLM responses")
    print()
    
    if args.question:
        demonstrate_analysis(args.question)
    elif args.mode == "demo":
        run_demo()
    else:
        interactive_demo()
