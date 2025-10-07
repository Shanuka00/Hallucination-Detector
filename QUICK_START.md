# Quick Start Guide - Prioritized LLM Voting System

## ⚡ Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure API Keys
Edit `backend/.env` and add your API keys:
```bash
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-key-here
DEEPSEEK_API_KEY=your-key-here
MISTRAL_API_KEY=your-key-here
```

### Step 3: Start Server
```bash
cd backend
python -m uvicorn app:app --reload --port 8001
```

### Step 4: Open Frontend
Open browser: `http://localhost:8001/static/index.html`

---

## 🎯 How It Works

### System Flow
```
User Question
    ↓
Target LLM Response
    ↓
OpenAI Extracts Claims
    ↓
First 2 Priority LLMs Verify
    ↓
  Agree? → Done ✓
    ↓ No
Third LLM Tiebreaker
    ↓
Majority Vote → Final Verdict
```

### Priority Order
1. OpenAI (best factuality)
2. Anthropic Claude
3. Google Gemini
4. DeepSeek

**Target LLM is automatically excluded from verification**

---

## 🖥️ Using the Interface

### 1. Select Target LLM
- Dropdown menu: Mistral / OpenAI / Gemini / DeepSeek
- This is the LLM you want to test for hallucinations

### 2. Enter Your Question
Example questions:
- "Tell me about Isaac Newton"
- "What happened in World War 2?"
- "Explain quantum mechanics"

### 3. Click "Analyze Hallucinations"
System will:
- Get response from target LLM
- Extract claims
- Verify with 2-3 prioritized LLMs
- Show results

### 4. Review Results

#### For Each Claim You'll See:
- **Claim ID**: C1, C2, C3, etc.
- **Verdict Badge**: 
  - ✓ Verified (Yes)
  - ✗ Rejected (No)
  - ? Uncertain
- **Voting Badge**: 🗳️ Voted (if 3-way voting used)
- **LLM Responses**: What each verifier said
- **Final Verdict**: Consensus result

---

## 📊 Reading the Results

### Verdict Meanings

#### ✓ Verified (Yes)
- 2+ LLMs agree the claim is factually correct
- Low hallucination risk
- Green background

#### ✗ Rejected (No)
- 2+ LLMs agree the claim is factually incorrect
- High hallucination risk
- Red background

#### ? Uncertain
- LLMs disagree OR all 3 give different answers
- Medium hallucination risk
- Yellow background

### Voting Badge 🗳️
- Appears when 2 LLMs contradicted
- Shows 3rd LLM was called as tiebreaker
- More thorough verification

---

## 💡 Examples

### Example 1: Agreement (2 LLMs)
```
Claim: "Isaac Newton was born in 1642"
OPENAI: Yes
ANTHROPIC: Yes
Final Verdict: ✓ Yes (Verified)
```
No need for 3rd LLM - they agreed!

### Example 2: Contradiction (3 LLMs needed)
```
Claim: "Newton discovered gravity in 1665"
OPENAI: Yes
ANTHROPIC: Uncertain
GEMINI (Tiebreaker): Yes
Final Verdict: ✓ Yes (2/3 agree)
🗳️ Voted badge shown
```

### Example 3: All Different
```
Claim: "Newton lived in London"
OPENAI: Yes
ANTHROPIC: No
GEMINI: Uncertain
Final Verdict: ? Uncertain (no majority)
🗳️ Voted badge shown
```

---

## 🔍 Summary Statistics

At the top you'll see:
- **Total Claims**: Number of claims extracted
- **High Risk**: Claims marked as "No" (likely hallucinations)
- **Medium Risk**: Claims marked as "Uncertain"
- **Low Risk**: Claims marked as "Yes" (verified)

---

## ⚙️ Target LLM Selection

### When to Use Each:

**Mistral** (Default)
- Fast and efficient
- Good for testing the system
- Budget-friendly

**OpenAI**
- High accuracy target
- Excluded from verification (uses Anthropic + Gemini)
- Good baseline

**Gemini**
- Google's model
- Excluded from verification (uses OpenAI + Anthropic)
- Free tier available

**DeepSeek**
- Alternative model
- Usually last in priority
- Useful for comparison

---

## 🎨 Visual Guide

### Color Coding
- **Green**: Verified / Low Risk / Yes
- **Red**: Rejected / High Risk / No
- **Yellow**: Uncertain / Medium Risk
- **Blue**: External verification (Wikipedia)
- **Purple**: Tiebreaker LLM (3rd voter)

### Badges
- ✓ = Verified
- ✗ = Rejected
- ? = Uncertain
- 🗳️ = Voting Used
- 🌐 = External Check

---

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
netstat -ano | findstr :8001
# Kill process if needed
taskkill /PID <process_id> /F
```

### "API Key Invalid" Error
- Check `.env` file has correct keys
- No quotes around keys
- No extra spaces

### "Import Error"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Not Loading
- Make sure server is running on port 8001
- Check: `http://127.0.0.1:8001/static/index.html`
- Try clearing browser cache

---

## 📚 More Information

For detailed technical documentation:
- `VOTING_SYSTEM_GUIDE.md` - System architecture
- `IMPLEMENTATION_COMPLETE.md` - Full implementation details
- `README.md` - Project overview

---

## 🚀 You're Ready!

The system is now configured and ready to detect hallucinations using research-backed prioritized LLM voting. Start with a simple question and explore the results!

**Tip**: Try the same question with different target LLMs to see how results vary!
