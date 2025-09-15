"""
Demonstration script for the Hallucination Detection System
Run this to see the system in action without the web interface
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from config import config

# Choose real implementations when simulation is disabled
if not getattr(config, 'USE_SIMULATION', True):
    # Use the real backend service wrappers
    from real_llm_services import real_llm_service

    def get_targetllm_response(question: str):
        return real_llm_service.get_target_response(question)

    def extract_claims_with_claimllm(text: str):
        # Use Mistral for claim extraction instead of Gemini
        return real_llm_service.extract_claims_with_mistral(text)

    def simulate_claimllm_api_call(text: str):
        # Provide the same metadata-shaped dict used by the demo when using the real extractor
        start = __import__('time').time()
        claims = real_llm_service.extract_claims_with_mistral(text)
        elapsed_ms = int((__import__('time').time() - start) * 1000)
        return {
            "claims": claims,
            "status": "ok",
            "metadata": {
                "model": getattr(config, 'EXTRACTION_MODEL', 'mistral-small'),
                "processing_time_ms": elapsed_ms,
                "confidence": 0.95
            },
            "total_claims_extracted": len(claims)
        }

    def verify_with_llm1(claim: str):
        return real_llm_service.verify_claims_with_gemini([claim])[0]

    def verify_with_llm2(claim: str):
        return real_llm_service.verify_claims_with_deepseek([claim])[0]

    def bulk_verify_claims(claims_list):
        # Separate bulk verification: LLM1 (Gemini) and LLM2 (DeepSeek)
        llm1_results = real_llm_service.verify_claims_with_gemini(claims_list)
        llm2_results = real_llm_service.verify_claims_with_deepseek(claims_list)
        return {"llm1": llm1_results, "llm2": llm2_results}
else:
    # Fallback to existing stubbed implementations for offline/demo mode
    from targetllm_stub import get_targetllm_response
    from claimllm_stub import extract_claims_with_claimllm, simulate_claimllm_api_call
    from claim_verifier_stub import verify_with_llm1, verify_with_llm2, bulk_verify_claims
from models import ClaimVerification
from graph_builder import build_hallucination_graph

# Import confidence scoring system
try:
    from confidence_scorer import ConfidenceScorer, format_confidence_analysis
    from wikipedia_service import WikipediaService
    from multi_kg_service import MultiKGService
except ImportError:
    # Fallback if confidence_scorer is not available
    print("Warning: Advanced confidence scoring not available")
    ConfidenceScorer = None
    format_confidence_analysis = None
    WikipediaService = None
    MultiKGService = None

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
    # Bulk verify all claims in one API call
    print("5️⃣ BULK CLAIM VERIFICATION:")
    bulk_results = bulk_verify_claims(claims_text)
    
    # Handle separate LLM1/LLM2 results when using real APIs
    if isinstance(bulk_results, dict) and 'llm1' in bulk_results and 'llm2' in bulk_results:
        print("   LLM1 (Gemini) Results:")
        for i, status in enumerate(bulk_results['llm1'], 1):
            print(f"     C{i}: {status}")
        print("   LLM2 (DeepSeek) Results:")
        for i, status in enumerate(bulk_results['llm2'], 1):
            print(f"     C{i}: {status}")
    else:
        # Fallback for simulation mode
        for i, status in enumerate(bulk_results, 1):
            print(f"   C{i}: {status}")
    print()
    
    # Step 3: Verify claims
    print("6️⃣ CLAIM VERIFICATION:")
    verified_claims = []
    
    # Initialize external verification services using config flags
    wiki_service = None
    multi_kg_service = None
    if WikipediaService and getattr(config, 'WIKIPEDIA_ENABLED', True):
        try:
            wiki_service = WikipediaService(use_simulation=getattr(config, 'WIKIPEDIA_USE_SIMULATION', True))
        except Exception as e:
            print(f"   ⚠️ Could not initialize Wikipedia service: {e}")
    if MultiKGService:
        try:
            multi_kg_service = MultiKGService()
            print(f"   ✅ Multi-KG service initialized (Wikidata + DBpedia)")
        except Exception as e:
            print(f"   ⚠️ Could not initialize Multi-KG service: {e}")

    # Debug line to show which external verification is active
    external_status = "Multi-KG (REAL)" if multi_kg_service else ("Wikipedia (REAL)" if (wiki_service and not wiki_service.use_simulation) else "SIM")
    print(f"   External Verifier: {external_status}")
    
    for i, claim in enumerate(claims_text):
        llm1_response = verify_with_llm1(claim)
        llm2_response = verify_with_llm2(claim)
        
        verification = ClaimVerification(
            id=f"C{i+1}",
            claim=claim,
            llm1_verification=llm1_response,
            llm2_verification=llm2_response
        )
        
        # Check if we should verify externally for medium risk claims
        if verification.should_check_wikipedia():
            external_checked = False
            # Try Multi-KG consensus first (research-grade approach)
            if multi_kg_service:
                try:
                    kg_status = multi_kg_service.verify_claim(claim)
                    print(f"   � Multi-KG consensus for C{i+1}: {kg_status}")
                    # Map Multi-KG status into wikipedia_status field to reuse existing logic
                    verification.wikipedia_status = kg_status
                    verification.is_wikipedia_checked = True
                    external_checked = True
                except Exception as e:
                    print(f"   ⚠️ Multi-KG check failed for C{i+1}: {e}")
            # Fallback to Wikipedia if Multi-KG unavailable
            if not external_checked and wiki_service:
                try:
                    wiki_status = wiki_service.verify_claim_with_wikipedia(claim)
                    verification.wikipedia_status = wiki_status
                    verification.is_wikipedia_checked = True
                    print(f"   🌐 Wikipedia fallback for C{i+1}: {wiki_status}")
                except Exception as e:
                    print(f"   ⚠️ Wikipedia check failed for C{i+1}: {e}")
        
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
        if verification.is_wikipedia_checked:
            print(f"       Wikipedia: {verification.wikipedia_status}")
        print(f"       Risk Level: {risk_colors.get(risk_level, '❓')} {risk_level} RISK{reset_color}")
        print(f"       Confidence: {confidence:.2f}")
        print()
    
    # Step 4: Generate summary
    print("7️⃣ RISK ASSESSMENT SUMMARY:")
    
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
    print("8️⃣ GRAPH ANALYSIS:")
    graph_data = build_hallucination_graph(verified_claims)
    metrics = graph_data['metrics']
    
    print(f"   Connected Components: {metrics['connected_components']}")
    print(f"   Average Confidence: {metrics['average_confidence']:.2f}")
    print(f"   Graph Density: {metrics['density']:.2f}")
    print(f"   Risk Assessment: {metrics['risk_assessment']}")
    print()
    
    # Step 6: Advanced Confidence Scoring Analysis
    if ConfidenceScorer and format_confidence_analysis:
        print("9️⃣ ADVANCED CONFIDENCE SCORING:")
        
        # Initialize confidence scorer with standard weights
        scorer = ConfidenceScorer(alpha=0.4, beta=0.4, gamma=0.2)
        
        # Calculate overall confidence and detailed analysis
        overall_confidence, analysis = scorer.calculate_overall_confidence(verified_claims)
        
        # Format and display the analysis
        confidence_report = format_confidence_analysis(overall_confidence, analysis)
        print(confidence_report)
        print()
    else:
        print("9️⃣ ADVANCED CONFIDENCE SCORING: Not available")
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
