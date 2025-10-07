# Prioritized LLM Voting System - Implementation Guide

## Overview
This system implements a hierarchical LLM voting mechanism for hallucination detection based on research-backed factuality rankings.

## System Architecture

### 1. Claim Extraction
- **Primary Model**: OpenAI GPT-4o-mini
- **Purpose**: Extract factual claims from target LLM responses
- **Why**: Research shows OpenAI performs best for factual extraction

### 2. Prioritized Verification Order
Based on factuality research, LLMs are ranked as:
1. **OpenAI** (GPT-4o-mini) - Highest factuality
2. **Anthropic** (Claude 3.5 Sonnet) - Second best
3. **Google Gemini** (1.5 Flash) - Third
4. **DeepSeek** (deepseek-chat) - Fourth

### 3. Voting Algorithm

#### Step 1: Initial Verification
- Send claims to first two prioritized LLMs (excluding target if it's one of them)
- Each LLM responds: "Yes", "No", or "Uncertain"

#### Step 2: Agreement Check
- **If both agree** (Yes/Yes, No/No, Uncertain/Uncertain):
  - ✓ Use that result as final verdict
  - No need for third LLM

#### Step 3: Conflict Resolution
- **If they contradict** (Yes/No, Yes/Uncertain, No/Uncertain):
  - Send claim to next priority LLM for tiebreaker
  - Apply 3-way voting logic

#### Step 4: Final Verdict Logic
With 3 LLM responses:
- **2 or more agree**: Use majority verdict
- **All 3 different**: Mark as "Uncertain"

### 4. Target LLM Exclusion
The system automatically excludes the target LLM from verification to avoid bias:
- If target is OpenAI → Use Anthropic, Gemini, (DeepSeek if needed)
- If target is Gemini → Use OpenAI, Anthropic, (DeepSeek if needed)
- If target is Mistral → Use OpenAI, Anthropic, (Gemini if needed)

## Frontend Display

### Claim Cards Show:
- **Claim ID**: Unique identifier
- **Verdict Badge**: ✓ Verified / ✗ Rejected / ? Uncertain
- **Voting Badge**: 🗳️ Voted (if 3-way voting was used)
- **External Badge**: 🌐 Ext (if Wikipedia verification performed)
- **LLM Responses**: Shows each verifier's response with LLM name
- **Tiebreaker**: Highlighted when third LLM was used
- **Final Verdict**: Clear display of consensus result

## Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here

EXTRACTION_MODEL=gpt-4o-mini
CLAIM_EXTRACTION_API=openai
```

### Priority Order (hardcoded in prioritized_voting.py)
```python
LLM_PRIORITY_ORDER = ["openai", "anthropic", "gemini", "deepseek"]
```

## API Response Format

```json
{
  "original_question": "string",
  "llm_response": "string",
  "claims": [
    {
      "id": "C1",
      "claim": "factual claim text",
      "llm1_name": "openai",
      "llm1_verification": "Yes",
      "llm2_name": "anthropic",
      "llm2_verification": "Yes",
      "llm3_name": null,
      "llm3_verification": null,
      "voting_used": false,
      "final_verdict": "Yes",
      "wikipedia_status": "NotChecked",
      "is_wikipedia_checked": false
    }
  ],
  "summary": {
    "total_claims": 5,
    "high": 1,
    "medium": 2,
    "low": 2,
    "extraction_model": "openai-gpt-4o-mini",
    "verifier_llms": ["openai", "anthropic"],
    "target_model": "mistral-small",
    "voting_enabled": true
  }
}
```

## Usage Example

1. **User submits query**: "Tell me about Isaac Newton"
2. **Target LLM** (e.g., Mistral) generates response
3. **OpenAI extracts claims** from the response
4. **First two verifiers** (OpenAI + Anthropic, excluding target):
   - Verify each claim
   - Agree → Final verdict set
   - Disagree → Proceed to step 5
5. **Third verifier** (Gemini) resolves conflicts
6. **Frontend displays** results with badges and verdict

## Benefits

1. **Research-backed**: Uses proven factuality rankings
2. **Efficient**: Only calls third LLM when needed
3. **Unbiased**: Excludes target from verification
4. **Transparent**: Shows all LLM responses and voting
5. **Robust**: Handles disagreements systematically

## Testing

Run backend:
```bash
cd backend
uvicorn app:app --reload --port 8001
```

Open frontend:
```
http://localhost:8001/static/index.html
```

## Files Modified

### Backend
- `backend/real_llm_services.py` - Added Anthropic API support
- `backend/prioritized_voting.py` - New voting system logic
- `backend/models.py` - Updated ClaimVerification model
- `backend/app.py` - Integrated voting system
- `backend/requirements.txt` - Added API client dependencies

### Frontend
- `frontend/script.js` - Updated claim display logic
- `frontend/style.css` - Added voting badge styles
- `frontend/index.html` - No changes needed

### Configuration
- `backend/.env` - Updated API keys and model config
