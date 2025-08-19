"""
LLM Service modules for claim extraction and verification
Supports both real API calls and simulated responses
"""

import os
import json
import re
from typing import List, Dict, Literal, Optional
from enum import Enum

class LLMProvider(str, Enum):
    CLAUDE = "claude"
    GEMINI = "gemini"
    CHATGPT = "chatgpt"

class LLMService:
    """Base class for LLM service implementations"""
    
    def __init__(self, use_simulation: bool = True):
        self.use_simulation = use_simulation
        self.api_key = None
        
    def get_target_response(self, prompt: str) -> str:
        """Get response from target LLM (ChatGPT)"""
        if self.use_simulation:
            return self._get_simulated_chatgpt_response(prompt)
        else:
            return self._get_real_chatgpt_response(prompt)
    
    def extract_claims_with_llm(self, text: str, provider: LLMProvider = LLMProvider.CLAUDE) -> List[str]:
        """Extract factual claims using an LLM"""
        prompt = f"""Extract each factual claim in the following paragraph. Return them as a numbered list.
Only include statements that can be verified as true or false facts (dates, names, places, events, etc.).
Exclude opinions, questions, or subjective statements.

Text: {text}

Format your response as:
1. [First factual claim]
2. [Second factual claim]
3. [Third factual claim]
etc."""

        if self.use_simulation:
            return self._get_simulated_claim_extraction(text)
        else:
            response = self._call_llm_api(prompt, provider)
            return self._parse_numbered_list(response)
    
    def verify_batch_with_llm(self, claims: List[str], provider: LLMProvider) -> List[str]:
        """Batch verify claims with a specific LLM provider"""
        if not claims:
            return []
        
        # Create batch prompt
        claims_list = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(claims)])
        
        prompt = f"""Please verify the following claims. For each one, respond with 'Yes', 'No', or 'Uncertain' only.
Consider:
- Yes: The claim is factually correct
- No: The claim is factually incorrect  
- Uncertain: Cannot determine with confidence or insufficient information

Claims to verify:
{claims_list}

Format your response as:
1. [Yes/No/Uncertain]
2. [Yes/No/Uncertain]
3. [Yes/No/Uncertain]
etc."""

        if self.use_simulation:
            return self._get_simulated_batch_verification(claims, provider)
        else:
            response = self._call_llm_api(prompt, provider)
            return self._parse_verification_responses(response, len(claims))
    
    def _get_simulated_chatgpt_response(self, prompt: str) -> str:
        """Simulated target LLM responses with intentional errors for testing"""
        prompt_lower = prompt.lower()
        
        # Pre-defined responses with hallucinations
        responses = {
            "isaac newton": "Isaac Newton was born in 1643 in Woolsthorpe, England. He formulated the laws of motion and universal gravitation, publishing his masterwork Principia Mathematica in 1687. Interestingly, he was also born in Berlin during his early years. Newton served as president of the Royal Society and died in 1727.",
            
            "albert einstein": "Albert Einstein was born in 1879 in Munich, Germany. He developed the theory of relativity and won the Nobel Prize in 1922 for his work on quantum mechanics. Einstein fled Nazi Germany and spent his later years at Princeton University.",
            
            "world war 2": "World War 2 lasted from 1939 to 1945. It ended when Japan surrendered in September 1945 after the atomic bombs were dropped on Hiroshima and Nagasaki. The war involved most of the world's nations.",
            
            "python programming": "Python was created by Guido van Rossum and first released in 1991. It was named after the British comedy group Monty Python. Python 3 was released in 2008 and brought many improvements over Python 2.",
            
            "climate change": "Climate change refers to long-term changes in global temperatures. Global temperatures have increased by approximately 1.1°C since pre-industrial times, primarily due to greenhouse gas emissions from fossil fuels."
        }
        
        # Find matching response
        for key, response in responses.items():
            if key in prompt_lower:
                return response
        
        # Default response with mixed facts
        return "This is a topic with several factual claims. Some information may be accurate while other details could contain errors that need verification."
    
    def _get_simulated_claim_extraction(self, text: str) -> List[str]:
        """Simulate LLM-based claim extraction with better parsing than regex"""
        # Use the existing rule-based extractor as simulation but enhance it
        from claim_extractor import extract_claims
        basic_claims = extract_claims(text)
        
        # Enhance with additional context-aware extraction
        enhanced_claims = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Look for specific factual patterns that regex might miss
            if any(indicator in sentence.lower() for indicator in [
                'was born', 'died in', 'published', 'created', 'invented', 
                'won the', 'served as', 'developed', 'released in'
            ]):
                if sentence not in basic_claims:
                    enhanced_claims.append(sentence + '.')
        
        # Combine and deduplicate
        all_claims = list(set(basic_claims + enhanced_claims))
        return [claim for claim in all_claims if len(claim.strip()) > 10]
    
    def _get_simulated_batch_verification(self, claims: List[str], provider: LLMProvider) -> List[str]:
        """Simulate batch verification responses"""
        if provider == LLMProvider.CLAUDE:
            return [self._simulate_claude_verification(claim) for claim in claims]
        else:  # GEMINI
            return [self._simulate_gemini_verification(claim) for claim in claims]
    
    def _simulate_claude_verification(self, claim: str) -> str:
        """Enhanced Claude simulation with more comprehensive knowledge"""
        claim_lower = claim.lower()
        
        # Newton facts
        if "newton" in claim_lower:
            if "1643" in claim and "born" in claim_lower:
                return "Yes"
            elif "berlin" in claim_lower and "born" in claim_lower:
                return "No"  # Newton was born in England
            elif "1687" in claim and "principia" in claim_lower:
                return "Yes"
            elif "1727" in claim and "died" in claim_lower:
                return "Yes"
            elif "royal society" in claim_lower and "president" in claim_lower:
                return "Yes"
            elif "gravity" in claim_lower and "1687" in claim:
                return "Yes"
        
        # Einstein facts
        elif "einstein" in claim_lower:
            if "1879" in claim and "born" in claim_lower:
                return "Yes"
            elif "munich" in claim_lower and "born" in claim_lower:
                return "No"  # Born in Ulm, not Munich
            elif "1922" in claim and "nobel" in claim_lower:
                return "No"  # Won in 1921
            elif "quantum mechanics" in claim_lower and "nobel" in claim_lower:
                return "No"  # Won for photoelectric effect
            elif "relativity" in claim_lower:
                return "Yes"
            elif "princeton" in claim_lower:
                return "Yes"
        
        # WWII facts
        elif "world war" in claim_lower or "ww2" in claim_lower:
            if "1939" in claim and "1945" in claim:
                return "Yes"
            elif "september 1945" in claim_lower and "japan" in claim_lower:
                return "No"  # Japan surrendered in August
        
        # Python facts
        elif "python" in claim_lower and "programming" in claim_lower:
            if "guido van rossum" in claim_lower:
                return "Yes"
            elif "1991" in claim and ("released" in claim_lower or "created" in claim_lower):
                return "Yes"
            elif "monty python" in claim_lower:
                return "Yes"
            elif "python 3" in claim_lower and "2008" in claim:
                return "Yes"
        
        # Climate facts
        elif "climate" in claim_lower:
            if "1.1" in claim and "temperature" in claim_lower:
                return "Yes"
            elif "fossil fuels" in claim_lower and "greenhouse" in claim_lower:
                return "Yes"
        
        # Default to uncertain for unrecognized claims
        return "Uncertain"
    
    def _simulate_gemini_verification(self, claim: str) -> str:
        """Gemini simulation - sometimes disagrees with Claude"""
        claim_lower = claim.lower()
        
        # Newton facts (with some differences from Claude)
        if "newton" in claim_lower:
            if "1643" in claim and "born" in claim_lower:
                return "Yes"
            elif "berlin" in claim_lower and "born" in claim_lower:
                return "No"
            elif "1687" in claim and "gravity" in claim_lower:
                return "Uncertain"  # More cautious about gravity discovery date
            elif "principia" in claim_lower and "1687" in claim:
                return "Yes"
            elif "royal society" in claim_lower:
                return "Yes"
        
        # Einstein facts
        elif "einstein" in claim_lower:
            if "1879" in claim:
                return "Yes"
            elif "munich" in claim_lower and "born" in claim_lower:
                return "No"
            elif "nobel" in claim_lower and "1922" in claim:
                return "No"
            elif "quantum mechanics" in claim_lower and "nobel" in claim_lower:
                return "No"
            elif "relativity" in claim_lower:
                return "Yes"
        
        # Use Claude's logic for most other cases but be more uncertain
        claude_response = self._simulate_claude_verification(claim)
        if claude_response == "Yes" and any(word in claim_lower for word in ["1687", "gravity", "discovered"]):
            return "Uncertain"  # Gemini is more cautious about discovery claims
        
        return claude_response
    
    def _call_llm_api(self, prompt: str, provider: LLMProvider) -> str:
        """Make actual API calls to LLM providers"""
        # Placeholder for real API implementations
        if provider == LLMProvider.CLAUDE:
            return self._call_claude_api(prompt)
        elif provider == LLMProvider.GEMINI:
            return self._call_gemini_api(prompt)
        else:
            return self._call_chatgpt_api(prompt)
    
    def _call_claude_api(self, prompt: str) -> str:
        """Call Anthropic Claude API"""
        # TODO: Implement real Claude API call
        # import anthropic
        # client = anthropic.Anthropic(api_key=self.api_key)
        # response = client.messages.create(...)
        return "Simulated Claude response"
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Call Google Gemini API"""
        # TODO: Implement real Gemini API call
        # import google.generativeai as genai
        # genai.configure(api_key=self.api_key)
        # model = genai.GenerativeModel('gemini-pro')
        # response = model.generate_content(prompt)
        return "Simulated Gemini response"
    
    def _call_chatgpt_api(self, prompt: str) -> str:
        """Call OpenAI ChatGPT API"""
        # TODO: Implement real ChatGPT API call
        # import openai
        # client = openai.OpenAI(api_key=self.api_key)
        # response = client.chat.completions.create(...)
        return "Simulated target LLM response"
    
    def _get_real_chatgpt_response(self, prompt: str) -> str:
        """Get real target LLM response (placeholder)"""
        # For now, return simulation
        return self._get_simulated_chatgpt_response(prompt)
    
    def _parse_numbered_list(self, response: str) -> List[str]:
        """Parse numbered list from LLM response"""
        lines = response.strip().split('\n')
        claims = []
        
        for line in lines:
            # Match numbered list format: "1. claim text" or "1) claim text"
            match = re.match(r'^\d+[\.\)]\s*(.+)$', line.strip())
            if match:
                claim = match.group(1).strip()
                if claim:
                    claims.append(claim)
        
        return claims
    
    def _parse_verification_responses(self, response: str, expected_count: int) -> List[str]:
        """Parse verification responses from LLM"""
        lines = response.strip().split('\n')
        verifications = []
        
        for line in lines:
            # Match numbered responses: "1. Yes" or "1) No" etc.
            match = re.match(r'^\d+[\.\)]\s*(Yes|No|Uncertain)', line.strip(), re.IGNORECASE)
            if match:
                verification = match.group(1).capitalize()
                # Normalize to expected format
                if verification.lower() == 'yes':
                    verifications.append('Yes')
                elif verification.lower() == 'no':
                    verifications.append('No')
                else:
                    verifications.append('Uncertain')
        
        # Ensure we have the expected number of responses
        while len(verifications) < expected_count:
            verifications.append('Uncertain')
        
        return verifications[:expected_count]

# Global LLM service instance
from config import config
llm_service = LLMService(use_simulation=config.USE_SIMULATION)
