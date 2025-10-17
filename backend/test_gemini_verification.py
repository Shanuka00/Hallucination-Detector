import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

# Test claims
test_claims = [
    "Isaac Newton was born in 1643",
    "Einstein won the Nobel Prize in 1921",
    "Mars has 5 moons"
]

claims_text = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(test_claims)])

prompt = f"""For each claim below, respond with ONLY one word: "Yes", "No", or "Uncertain"

Yes = the claim is factually correct according to widely accepted knowledge
No = the claim is factually incorrect 
Uncertain = the claim is ambiguous, partially true, or you're not confident

Claims:
{claims_text}

Response format:
1. [Yes/No/Uncertain]
2. [Yes/No/Uncertain]
3. [Yes/No/Uncertain]
etc."""

print("Testing Gemini Verification...")
print(f"\nPrompt:\n{prompt}")
print("\n" + "="*80 + "\n")

try:
    response = gemini_model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=200,
        )
    )
    
    print(f"Raw Gemini Response:\n{response.text}")
    print("\n" + "="*80 + "\n")
    
    # Try parsing
    import re
    verifications = []
    lines = response.text.strip().split('\n')
    
    print("Parsing each line:")
    for i, line in enumerate(lines):
        line = line.strip()
        print(f"Line {i}: '{line}'")
        
        # Match patterns like "1. Yes", "1) No", "1 Uncertain"
        match = re.match(r'^\d+[\.\)\s]+(\w+)', line)
        if match:
            response_word = match.group(1).strip()
            print(f"  -> Matched: '{response_word}'")
            
            # Normalize
            if response_word.lower() in ['yes', 'true', 'correct', 'supported']:
                verifications.append('Yes')
            elif response_word.lower() in ['no', 'false', 'incorrect', 'contradicted']:
                verifications.append('No')
            else:
                verifications.append('Uncertain')
        else:
            print(f"  -> No match!")
    
    print("\n" + "="*80 + "\n")
    print(f"Final parsed results: {verifications}")
    print(f"Expected count: {len(test_claims)}")
    
    # Fill missing
    while len(verifications) < len(test_claims):
        verifications.append('Uncertain')
    
    print(f"Final (with padding): {verifications[:len(test_claims)]}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
