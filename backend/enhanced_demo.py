"""
Enhanced Hallucination Detection System Demo
Demonstrates the new LLM-based claim extraction and Wikipedia verification
"""

from llm_services import llm_service, LLMProvider
from wikipedia_service import wikipedia_service
from models import ClaimVerification
from graph_builder import build_hallucination_graph
import json

def run_enhanced_demo():
    """Run a comprehensive demo of the enhanced system"""
    
    print("🧠 Enhanced Hallucination Detection System Demo")
    print("=" * 60)
    
    # Test query
    test_query = "Tell me about Isaac Newton"
    
    print(f"\n📝 Query: {test_query}")
    print("-" * 40)
    
    # Step 1: Get target response
    print("\n1️⃣ Getting target LLM response...")
    llm_response = llm_service.get_target_response(test_query)
    print(f"Response: {llm_response}")
    
    # Step 2: Extract claims using LLM
    print("\n2️⃣ Extracting claims with LLM (Claude)...")
    claims_text = llm_service.extract_claims_with_llm(llm_response, LLMProvider.CLAUDE)
    print(f"Extracted {len(claims_text)} claims:")
    for i, claim in enumerate(claims_text, 1):
        print(f"  {i}. {claim}")
    
    # Step 3: Batch verify claims
    print("\n3️⃣ Batch verifying claims...")
    claude_verifications = llm_service.verify_batch_with_llm(claims_text, LLMProvider.CLAUDE)
    gemini_verifications = llm_service.verify_batch_with_llm(claims_text, LLMProvider.GEMINI)
    
    print("Claude verifications:", claude_verifications)
    print("Gemini verifications:", gemini_verifications)
    
    # Step 4: Create verification objects
    print("\n4️⃣ Creating claim verification objects...")
    verified_claims = []
    for i, claim in enumerate(claims_text):
        claude_response = claude_verifications[i] if i < len(claude_verifications) else "Uncertain"
        gemini_response = gemini_verifications[i] if i < len(gemini_verifications) else "Uncertain"
        
        verification = ClaimVerification(
            id=f"C{i+1}",
            claim=claim,
            claude_verification=claude_response,
            gemini_verification=gemini_response
        )
        verified_claims.append(verification)
    
    # Step 5: Check medium-risk claims with Wikipedia
    print("\n5️⃣ Checking medium-risk claims with Wikipedia...")
    wikipedia_checks = 0
    for claim_verification in verified_claims:
        initial_risk = claim_verification.get_risk_level()
        print(f"\n   Claim {claim_verification.id}: {initial_risk} risk")
        
        if claim_verification.should_check_wikipedia():
            print(f"   → Checking with Wikipedia...")
            wiki_result = wikipedia_service.verify_claim_with_wikipedia(claim_verification.claim)
            wiki_summary_data = wikipedia_service.get_summary_from_wikipedia(claim_verification.claim)
            
            claim_verification.wikipedia_status = wiki_result
            claim_verification.wikipedia_summary = wiki_summary_data.get("extract", "")[:200] + "..." if wiki_summary_data.get("extract") else None
            claim_verification.is_wikipedia_checked = True
            wikipedia_checks += 1
            
            final_risk = claim_verification.get_risk_level()
            print(f"   → Wikipedia says: {wiki_result}")
            print(f"   → Final risk: {final_risk}")
        else:
            print(f"   → No Wikipedia check needed")
    
    # Step 6: Display results summary
    print("\n6️⃣ Final Results Summary:")
    print("=" * 40)
    
    risk_counts = {"high": 0, "medium": 0, "low": 0}
    for claim in verified_claims:
        risk_level = claim.get_risk_level()
        risk_counts[risk_level] += 1
        
        print(f"\n📋 {claim.id}: {claim.claim[:60]}...")
        print(f"   Claude: {claim.claude_verification} | Gemini: {claim.gemini_verification}")
        if claim.is_wikipedia_checked:
            print(f"   Wikipedia: {claim.wikipedia_status} 📖")
        print(f"   🎯 Risk Level: {risk_level.upper()}")
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Claims: {len(verified_claims)}")
    print(f"   High Risk: {risk_counts['high']}")
    print(f"   Medium Risk: {risk_counts['medium']}")
    print(f"   Low Risk: {risk_counts['low']}")
    print(f"   Wikipedia Checks: {wikipedia_checks}")
    
    # Step 7: Build and display graph data
    print("\n7️⃣ Building hallucination graph...")
    graph_data = build_hallucination_graph(verified_claims)
    print(f"   Graph nodes: {len(graph_data['nodes'])}")
    print(f"   Graph edges: {len(graph_data['edges'])}")
    print(f"   Overall risk assessment: {graph_data['metrics'].get('risk_assessment', 'Unknown')}")
    
    return {
        "query": test_query,
        "llm_response": llm_response,
        "claims": [claim.model_dump() for claim in verified_claims],
        "graph_data": graph_data,
        "summary": {
            **risk_counts,
            "total_claims": len(verified_claims),
            "wikipedia_checks": wikipedia_checks
        }
    }

def test_different_scenarios():
    """Test different types of queries to show system capabilities"""
    
    test_cases = [
        "Tell me about Isaac Newton",
        "What do you know about Albert Einstein?", 
        "Explain World War 2",
        "Describe Python programming language"
    ]
    
    print("\n🔬 Testing Different Scenarios")
    print("=" * 60)
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {query}")
        print("-" * 30)
        
        # Quick analysis
        llm_response = llm_service.get_target_response(query)
        claims = llm_service.extract_claims_with_llm(llm_response, LLMProvider.CLAUDE)
        
        print(f"Response length: {len(llm_response)} chars")
        print(f"Claims extracted: {len(claims)}")
        
        if claims:
            # Test verification
            claude_results = llm_service.verify_batch_with_llm(claims, LLMProvider.CLAUDE)
            gemini_results = llm_service.verify_batch_with_llm(claims, LLMProvider.GEMINI)
            
            agreement_count = sum(1 for c, g in zip(claude_results, gemini_results) if c == g)
            print(f"Verifier agreement: {agreement_count}/{len(claims)} claims")
        
        print()

if __name__ == "__main__":
    # Run the main demo
    result = run_enhanced_demo()
    
    # Test different scenarios
    test_different_scenarios()
    
    print("\n✅ Demo completed! The enhanced system is ready.")
    print("💡 To use real APIs instead of simulation:")
    print("   1. Set API keys in environment variables")
    print("   2. Update config.py: USE_SIMULATION = False")
    print("   3. Install required API client libraries")
