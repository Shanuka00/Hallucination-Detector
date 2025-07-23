# Enhanced Hallucination Detection System

A sophisticated web application that detects potential hallucinations in Large Language Model (LLM) responses using **multi-model verification**, **LLM-based claim extraction**, **Wikipedia fact-checking**, and **graph-based analysis**.

## 🧠 Overview

This enhanced system analyzes LLM responses by:
1. **LLM-Based Claim Extraction**: Using Claude/Gemini to extract factual claims (replaces regex-based extraction)
2. **Batch Verification**: Verifying multiple claims in single API calls to reduce cost
3. **Wikipedia Integration**: Cross-referencing medium-risk claims with Wikipedia for external validation
4. **Enhanced Risk Calculation**: Three-tier risk assessment with Wikipedia-adjusted scoring
5. **Interactive Visualization**: Updated graph showing LLM + Wikipedia verification status

## 🔄 What's New in Version 2.0

### ✨ Major Enhancements

- **🤖 LLM-Powered Claim Extraction**: 
  - Replaces rule-based regex with Claude/Gemini for more accurate claim identification
  - Handles complex sentences and context-dependent facts
  - Prompt: *"Extract each factual claim in the following paragraph. Return them as a numbered list."*

- **⚡ Batch Verification**:
  - Processes multiple claims in single API calls (cost reduction)
  - Parallel verification with Claude and Gemini
  - Prompt: *"Please verify the following claims. For each one, respond with 'Yes', 'No', or 'Uncertain' only."*

- **📖 Wikipedia Integration**:
  - Automatic fact-checking for medium-risk claims
  - Cross-references with Wikipedia summaries
  - Supports/Contradicts/Unclear/NotFound status
  - Risk adjustment based on external evidence

- **🎯 Enhanced Risk Assessment**:
  - ✅ **Low Risk**: Both LLMs agree (Yes) OR Wikipedia supports medium-risk claim
  - ⚠️ **Medium Risk**: Mixed LLM responses OR uncertain evidence
  - ❌ **High Risk**: Both LLMs disagree (No) OR Wikipedia contradicts claim

- **📊 Upgraded Visualization**:
  - Wikipedia verification badges on claims
  - Three-verifier graph (Claude + Gemini + Wikipedia)
  - Enhanced risk coloring and confidence scoring

## 🏗️ Architecture

```
EnhancedHallucinationDetector/
├── backend/                    # FastAPI backend with new LLM services
│   ├── app.py                 # Main FastAPI application (enhanced)
│   ├── models.py              # Data models with Wikipedia fields
│   ├── llm_services.py        # 🆕 LLM-based extraction & batch verification
│   ├── wikipedia_service.py   # 🆕 Wikipedia integration service
│   ├── config.py              # 🆕 Configuration management
│   ├── enhanced_demo.py       # 🆕 Comprehensive demo script
│   ├── graph_builder.py       # Updated graph with Wikipedia nodes
│   ├── chatgpt_stub.py        # Legacy ChatGPT simulator (kept for compatibility)
│   ├── claim_extractor.py     # Legacy regex extractor (fallback)
│   ├── claim_verifier_stub.py # Legacy verifiers (kept for comparison)
│   └── requirements.txt       # Updated dependencies
├── frontend/                  # Enhanced web UI
│   ├── index.html            # Main interface
│   ├── style.css             # Updated styles with Wikipedia badges
│   └── script.js             # Enhanced functionality
└── start.bat                 # Windows startup script
```

## 🚀 Quick Start

### Automated Setup
```bash
# Clone and navigate to project
cd backend

# Run setup script to configure everything
python setup.py

# Start the server (if setup succeeds)
py -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Manual Setup

#### 1. Environment Configuration
```bash
# Copy environment template
cp .env.template .env

# Edit .env file and add your API keys (optional for simulation mode)
# USE_SIMULATION=true (keeps simulation mode)
# USE_SIMULATION=false (requires real API keys)
```

#### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 3. Start the Server
```bash
py -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Open the Application
Open your browser to: `http://localhost:8000/static/index.html`

### Quick Demo
```bash
# Test the enhanced system
cd backend
python enhanced_demo.py
```

## 🔐 Environment Variables

The system uses environment variables for secure configuration. All sensitive data should be stored in a `.env` file (automatically ignored by git).

### Required Variables (for real API usage)
```bash
# API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here  
GOOGLE_API_KEY=your_google_key_here

# Mode Settings
USE_SIMULATION=false  # Set to true for demo mode
WIKIPEDIA_USE_SIMULATION=false
```

### Optional Variables
```bash
# Performance Settings
REQUEST_TIMEOUT=30
MAX_RETRIES=3
MAX_CLAIMS_PER_BATCH=10

# Debug Settings
DEBUG_MODE=true
LOG_LEVEL=INFO
```

### Getting API Keys
- **OpenAI**: [OpenAI API Keys](https://platform.openai.com/api-keys)
- **Anthropic**: [Anthropic Console](https://console.anthropic.com/)
- **Google**: [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🔒 Security Best Practices

### Environment Variables
- ✅ **Store API keys in `.env` file** (automatically ignored by git)
- ✅ **Use `.env.template` for sharing configuration structure**
- ✅ **Never commit `.env` files to version control**
- ✅ **Use different `.env` files for different environments**

### API Key Management
```bash
# Development (simulation mode)
USE_SIMULATION=true  # No API keys needed

# Production (real APIs)
USE_SIMULATION=false
OPENAI_API_KEY=your_actual_key_here
# Never share or commit these keys!
```

### File Security
The following files are automatically ignored by git:
- `.env` - Your actual API keys
- `.env.local`, `.env.production` - Environment-specific configs
- `__pycache__/` - Python cache files
- `*.log` - Log files that might contain sensitive data

### Production Deployment
When deploying to production:
1. Set environment variables on your server
2. Use `USE_SIMULATION=false`
3. Monitor API usage and costs
4. Implement rate limiting if needed
5. Use HTTPS for all communications

## 🎯 Enhanced Features

### Core Functionality
- **LLM-Based Claim Extraction**: Advanced claim identification using Claude/Gemini
- **Batch Verification**: Cost-efficient multi-claim verification in single requests
- **Wikipedia Cross-Referencing**: External fact-checking for uncertain claims
- **Enhanced Risk Assessment**: Four-tier classification with external validation
- **Smart Fallback Logic**: Wikipedia check only for medium-risk claims
- **Real-time Analysis**: Instant processing with improved accuracy

### User Interface Enhancements
- **Four-Panel Layout**: 
  - Left: Input and ChatGPT response
  - Center: Detailed claim analysis with Wikipedia status
  - Right: Interactive verification graph with Wikipedia nodes
  - Bottom: Enhanced statistics with Wikipedia check counts
- **Wikipedia Badges**: Visual indicators for externally verified claims
- **Enhanced Graph**: Shows three verification sources (Claude + Gemini + Wikipedia)
- **Responsive Design**: Improved mobile and tablet experience

### Enhanced Risk Calculation Algorithm
```python
def get_risk_level(claim):
    claude = claim.claude_verification.lower()
    gemini = claim.gemini_verification.lower()
    
    # Base risk assessment from LLM verifiers
    if claude == "no" and gemini == "no":
        base_risk = "high"
    elif claude == "yes" and gemini == "yes":
        base_risk = "low"
    else:
        base_risk = "medium"
    
    # Wikipedia adjustment (only for checked claims)
    if claim.is_wikipedia_checked:
        if claim.wikipedia_status == "Supports" and base_risk == "medium":
            return "low"  # Wikipedia evidence lowers risk
        elif claim.wikipedia_status == "Contradicts":
            return "high"  # Wikipedia contradiction = high risk
    
    return base_risk
```

## 📊 Enhanced Sample Analysis

**Input**: "Tell me about Isaac Newton"

**ChatGPT Response**: "Isaac Newton was born in 1643 in Woolsthorpe, England. He formulated the laws of motion and universal gravitation, publishing his masterwork Principia Mathematica in 1687. Interestingly, he was also born in Berlin during his early years."

**LLM-Extracted Claims**:
- C1: "Newton was born in 1643 in Woolsthorpe, England"
- C2: "He formulated the laws of motion and universal gravitation"  
- C3: "He published Principia Mathematica in 1687"
- C4: "He was also born in Berlin during his early years"

**Enhanced Verification Results**:
- **C1**: Claude: Yes, Gemini: Yes → ✅ **Low Risk**
- **C2**: Claude: Yes, Gemini: Yes → ✅ **Low Risk**  
- **C3**: Claude: Yes, Gemini: Uncertain → ⚠️ **Medium Risk** → Wikipedia: Supports → ✅ **Low Risk**
- **C4**: Claude: No, Gemini: No → ❌ **High Risk**

**Final Assessment**: 3 Low Risk, 0 Medium Risk, 1 High Risk (1 Wikipedia check performed)

## 🔧 Enhanced Technical Details

### Backend (FastAPI)
- **Framework**: FastAPI with async support and enhanced error handling
- **LLM Integration**: Modular service architecture supporting real APIs + simulation
- **Data Models**: Enhanced Pydantic models with Wikipedia fields
- **Batch Processing**: Efficient multi-claim verification in single requests  
- **External APIs**: Wikipedia REST API integration with fallback handling
- **Configuration**: Centralized config system for easy API/simulation switching

### Frontend (Enhanced Vanilla JS)
- **Visualization**: Vis.js with Wikipedia nodes and enhanced styling
- **UI Components**: Wikipedia badges, enhanced claim cards, statistics panel
- **Responsiveness**: Improved CSS Grid and Flexbox layouts
- **Accessibility**: Enhanced ARIA labels and keyboard navigation
- **Real-time Updates**: Dynamic UI updates based on verification results

### New Service Architecture
The enhanced system uses a modular service approach:

```python
# LLM Services (llm_services.py)
- get_target_response()           # ChatGPT simulation/real
- extract_claims_with_llm()       # Claude/Gemini claim extraction  
- verify_batch_with_llm()         # Batch verification with any LLM

# Wikipedia Service (wikipedia_service.py)  
- get_summary_from_wikipedia()    # Fetch Wikipedia summaries
- verify_claim_with_wikipedia()   # Cross-reference claims
- supports/contradicts analysis   # Intelligent fact matching

# Configuration (config.py)
- USE_SIMULATION toggle          # Switch between real/simulated APIs
- API key management            # Secure credential handling
- Service settings              # Timeouts, retry logic, etc.
```

### Simulated Models
The system uses hardcoded responses to simulate real LLM APIs:

```python
# ChatGPT responses with intentional errors
responses = {
    "isaac newton": "Newton was born in 1643. He discovered gravity in 1687. He was born in Berlin.",
    "albert einstein": "Einstein was born in 1879 in Munich. He won Nobel in 1922 for quantum mechanics."
}

# Claude verification (more conservative)
def verify_with_claude(claim):
    if "berlin" in claim.lower() and "newton" in claim.lower():
        return "No"  # Newton wasn't born in Berlin
    
# Gemini verification (sometimes differs from Claude)
def verify_with_gemini(claim):
    if "1687" in claim and "gravity" in claim.lower():
        return "Uncertain"  # More cautious about the apple story
```

## 🔬 Research Applications

This system demonstrates several important concepts:

1. **Hallucination Detection**: External verification without model internals
2. **Multi-Model Consensus**: Using agreement between models as truth signal
3. **Graph-Based Analysis**: Visualizing factual claim relationships
4. **Risk Quantification**: Systematic scoring of hallucination likelihood

## 🛠️ Extension Points

The modular design allows easy extension:

### Real API Integration
```python
# Replace stubs with real API calls
import openai
import anthropic

def get_chatgpt_response(prompt):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

### Enhanced Claim Extraction
- Named Entity Recognition (NER)
- Dependency parsing for complex sentences
- Temporal expression extraction
- Fact-checking database integration

### Advanced Graph Analysis
- Community detection algorithms
- Centrality measures for important claims
- Temporal claim tracking
- Cross-reference verification

## 📋 API Endpoints

### `POST /analyze`
Analyze a user query for hallucinations.

**Request**:
```json
{
  "question": "Tell me about Isaac Newton"
}
```

**Response**:
```json
{
  "original_question": "Tell me about Isaac Newton",
  "llm_response": "Isaac Newton was born in 1643...",
  "claims": [
    {
      "id": "C1",
      "claim": "Newton was born in 1643.",
      "claude_verification": "Yes",
      "gemini_verification": "Yes"
    }
  ],
  "graph_data": {
    "nodes": [...],
    "edges": [...],
    "metrics": {...}
  },
  "summary": {
    "high": 1,
    "medium": 1, 
    "low": 1
  }
}
```

### `GET /health`
Health check endpoint.

## 🔍 Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Change port in app.py or kill existing process
   uvicorn app:app --port 8001
   ```

2. **Frontend can't connect to backend**
   - Check CORS settings in `app.py`
   - Verify API_BASE_URL in `script.js`

3. **Graph not displaying**
   - Check browser console for vis.js errors
   - Ensure network data is properly formatted

### Performance Optimization

- **Claim Extraction**: Cache regex patterns
- **Graph Rendering**: Limit nodes for large responses  
- **API Calls**: Implement request batching for real APIs

## 📈 Future Enhancements

### Planned Features
- [ ] Real-time collaboration and sharing
- [ ] Historical analysis comparison
- [ ] Custom verifier model integration
- [ ] Automated fact-checking database queries
- [ ] Machine learning-based claim importance scoring
- [ ] Multi-language support
- [ ] Advanced graph layout algorithms

### Research Directions
- [ ] Confidence calibration across different model types
- [ ] Temporal consistency checking for evolving facts
- [ ] Domain-specific hallucination patterns
- [ ] Human-in-the-loop verification workflows

## 📄 License

This is a research project for academic purposes. Feel free to use and modify for educational and research applications.

## 👥 Contributing

This is an educational project, but suggestions and improvements are welcome! Please feel free to:
- Report bugs or suggest features
- Improve the claim extraction algorithms
- Enhance the graph visualization
- Add support for more LLM APIs

---

**Built for**: INTE 43216 - Research Project 2025  
**Technologies**: FastAPI, NetworkX, Vis.js, Modern Web Standards

# to run
- first navigate to backend
- then run below one in terminal

py setup.py
py -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
http://localhost:8000/static/index.html