"""
Real LLM Service implementations using actual APIs
- Target LLM: Mistral (mistral-small)
- LLM1: OpenAI (o1-preview) for extraction and verification
- LLM2: Google Gemini (gemini-1.5-flash) for verification
"""

import os
import json
import re
import time
from typing import List, Dict, Literal, Optional
from config import Config

# Import API clients
import openai
import google.generativeai as genai
from mistralai import Mistral
from anthropic import Anthropic


class RealLLMService:
    """Real LLM service using actual APIs"""
    
    def __init__(self):
        # Initialize API clients
        self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        # Use the correct Gemini model name
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        self.mistral_client = Mistral(api_key=Config.MISTRAL_API_KEY)
        
        # Initialize Anthropic Claude client
        self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        
        # Initialize DeepSeek client (OpenAI-compatible)
        self.deepseek_client = openai.OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
    def get_target_response(self, prompt: str, target: str = "mistral") -> str:
        """Get response from the selected target LLM with graceful fallback."""
        target_key = (target or "mistral").lower()

        if target_key == "openai":
            try:
                response = self.openai_client.chat.completions.create(
                    model=Config.LLM1_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as exc:
                print(f"OpenAI target error: {exc}")
                target_key = "mistral"
        elif target_key == "gemini":
            try:
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=500,
                    )
                )
                return response.text
            except Exception as exc:
                print(f"Gemini target error: {exc}")
                target_key = "mistral"
        elif target_key == "deepseek":
            try:
                response = self.deepseek_client.chat.completions.create(
                    model=Config.LLM2_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as exc:
                print(f"DeepSeek target error: {exc}")
                target_key = "mistral"

        try:
            response = self.mistral_client.chat.complete(
                model=Config.TARGET_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as exc:
            print(f"Mistral fallback error: {exc}")
            return f"Error getting response from target LLM: {exc}"
    
    def extract_claims_with_gemini(self, text: str) -> List[str]:
        """Extract claims using Google Gemini"""
        prompt = f"""Extract each factual claim in the following paragraph. Return them as a numbered list.
Only include statements that can be verified as true or false facts (dates, names, places, events, etc.).
Exclude opinions, questions, or subjective statements.

Text: {text}

Format your response as:
1. [First factual claim]
2. [Second factual claim]
3. [Third factual claim]
etc."""

        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=400,
                )
            )
            
            claims_text = response.text
            return self._parse_numbered_list(claims_text)
            
        except Exception as e:
            print(f"Gemini extraction error: {e}")
            return ["Error extracting claims"]
    
    def extract_claims_with_mistral(self, text: str) -> List[str]:
        """Extract claims using Mistral API"""
        prompt = f"""Extract each factual claim in the following paragraph. Return them as a numbered list.
Only include statements that can be verified as true or false facts (dates, names, places, events, etc.).
Exclude opinions, questions, or subjective statements.

Text: {text}

Format your response as:
1. [First factual claim]
2. [Second factual claim]
3. [Third factual claim]
etc."""

        try:
            response = self.mistral_client.chat.complete(
                model=Config.TARGET_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=400
            )
            
            claims_text = response.choices[0].message.content
            return self._parse_numbered_list(claims_text)
            
        except Exception as e:
            print(f"Mistral extraction error: {e}")
            return ["Error extracting claims"]
    
    def extract_claims_with_openai(self, text: str) -> List[str]:
        """Extract claims using OpenAI"""
        prompt = f"""Extract each factual claim in the following paragraph. Return them as a numbered list.
Only include statements that can be verified as true or false facts (dates, names, places, events, etc.).
Exclude opinions, questions, or subjective statements.

Text: {text}

Format your response as:
1. [First factual claim]
2. [Second factual claim]
3. [Third factual claim]
etc."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4o-mini for extraction as it's efficient and accurate
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=400
            )
            
            claims_text = response.choices[0].message.content
            return self._parse_numbered_list(claims_text)
            
        except Exception as e:
            print(f"OpenAI extraction error: {e}")
            return ["Error extracting claims"]
    
    def verify_claims_with_openai(self, claims: List[str]) -> List[str]:
        """Verify claims using OpenAI o1-preview"""
        claims_text = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(claims)])
        
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

        try:
            response = self.openai_client.chat.completions.create(
                model=Config.LLM1_MODEL,  # o1-preview
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            verification_text = response.choices[0].message.content
            return self._parse_verification_responses(verification_text, len(claims))
            
        except Exception as e:
            print(f"OpenAI verification error: {e}")
            return ["Uncertain"] * len(claims)
    
    def verify_claims_with_gemini(self, claims: List[str]) -> List[str]:
        """Verify claims using Google Gemini (LLM1)"""
        claims_text = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(claims)])
        
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

        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=200,
                )
            )
            
            verification_text = response.text
            return self._parse_verification_responses(verification_text, len(claims))
            
        except Exception as e:
            print(f"Gemini verification error: {e}")
            return ["Uncertain"] * len(claims)
    
    def verify_claims_with_deepseek(self, claims: List[str]) -> List[str]:
        """Verify claims using deepseek-chat"""
        claims_text = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(claims)])
        
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

        try:
            response = self.deepseek_client.chat.completions.create(
                model=Config.LLM2_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            verification_text = response.choices[0].message.content
            return self._parse_verification_responses(verification_text, len(claims))
            
        except Exception as e:
            print(f"DeepSeek verification error: {e}")
            return ["Uncertain"] * len(claims)
    
    def verify_claims_with_anthropic(self, claims: List[str]) -> List[str]:
        """Verify claims using Anthropic Claude"""
        claims_text = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(claims)])
        
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

        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            verification_text = response.content[0].text
            return self._parse_verification_responses(verification_text, len(claims))
            
        except Exception as e:
            print(f"Anthropic verification error: {e}")
            return ["Uncertain"] * len(claims)
    
    def _parse_numbered_list(self, text: str) -> List[str]:
        """Parse numbered list from LLM response"""
        claims = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Match patterns like "1. claim", "1) claim", "1 claim"
            match = re.match(r'^\d+[\.\)\s]+(.+)', line)
            if match:
                claim = match.group(1).strip()
                if claim and not claim.startswith('[') and not claim.startswith('('):
                    claims.append(claim)
        
        return claims if claims else [text.strip()]
    
    def _parse_verification_responses(self, text: str, expected_count: int) -> List[str]:
        """Parse verification responses from LLM"""
        verifications = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Match patterns like "1. Yes", "1) No", "1 Uncertain"
            match = re.match(r'^\d+[\.\)\s]+(\w+)', line)
            if match:
                response = match.group(1).strip()
                # Normalize responses
                if response.lower() in ['yes', 'true', 'correct', 'supported']:
                    verifications.append('Yes')
                elif response.lower() in ['no', 'false', 'incorrect', 'contradicted']:
                    verifications.append('No')
                else:
                    verifications.append('Uncertain')
        
        # Ensure we have the right number of responses
        while len(verifications) < expected_count:
            verifications.append('Uncertain')
        
        return verifications[:expected_count]


# Global instance
real_llm_service = RealLLMService()


# Legacy compatibility functions
def get_target_response(prompt: str, target: str = "mistral") -> str:
    """Get target LLM response for the requested provider."""
    return real_llm_service.get_target_response(prompt, target)


def extract_claims_with_llm(text: str, provider: str = "openai") -> List[str]:
    """Extract claims using OpenAI (best performing for claim extraction)"""
    return real_llm_service.extract_claims_with_openai(text)


def verify_batch_with_llm1(claims: List[str]) -> List[str]:
    """Verify claims with LLM1 (Gemini)"""
    return real_llm_service.verify_claims_with_gemini(claims)


def verify_batch_with_gemini(claims: List[str]) -> List[str]:
    """Verify claims with Gemini (LLM1)"""
    return real_llm_service.verify_claims_with_gemini(claims)


def verify_batch_with_openai(claims: List[str]) -> List[str]:
    """Verify claims with OpenAI (LLM1)"""
    return real_llm_service.verify_claims_with_openai(claims)


def verify_batch_with_deepseek(claims: List[str]) -> List[str]:
    """Verify claims with LLM2 (DeepSeek)"""
    return real_llm_service.verify_claims_with_deepseek(claims)


def verify_batch_with_anthropic(claims: List[str]) -> List[str]:
    """Verify claims with Anthropic Claude"""
    return real_llm_service.verify_claims_with_anthropic(claims)


def verify_batch_with_llm(claims: List[str], provider: str = "openai") -> List[str]:
    """Generic batch verification function"""
    provider_lower = provider.lower()
    if provider_lower == "gemini":
        return verify_batch_with_gemini(claims)
    elif provider_lower == "anthropic":
        return verify_batch_with_anthropic(claims)
    elif provider_lower == "deepseek":
        return verify_batch_with_deepseek(claims)
    else:
        return verify_batch_with_openai(claims)