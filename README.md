# Hallucination Detection System

A sophisticated web application that detects potential hallucinations in Large Language Model (LLM) responses using multi-model verification and graph-based analysis.

## 🧠 Overview

This system analyzes LLM responses by:
1. Extracting factual claims from the response
2. Verifying each claim using multiple LLM models (Claude and Gemini)
3. Building a verification graph showing agreement/disagreement
4. Ranking claims by hallucination risk level

## 🏗️ Architecture

```
HallucinationDetector/
├── backend/                 # FastAPI backend
│   ├── app.py              # Main FastAPI application
│   ├── models.py           # Data models and risk calculation
│   ├── chatgpt_stub.py     # Simulated ChatGPT responses
│   ├── claim_verifier_stub.py # Simulated Claude & Gemini verifiers
│   ├── claim_extractor.py  # NLP-based claim extraction
│   ├── graph_builder.py    # NetworkX graph construction
│   └── requirements.txt    # Python dependencies
├── frontend/               # Web UI
│   ├── index.html         # Main interface
│   ├── style.css          # Responsive styling
│   └── script.js          # Interactive functionality
└── start.bat             # Windows startup script
```

## 🚀 Quick Start

### Windows
1. Double-click `start.bat` to automatically install dependencies and start the server
2. The application will open in your browser at `http://localhost:8000/static/index.html`

### Manual Start
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Start the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Open browser to: http://localhost:8000/static/index.html
```

## 🎯 Features

### Core Functionality
- **Multi-LLM Verification**: Uses simulated Claude and Gemini responses to verify claims
- **Smart Claim Extraction**: NLP-based extraction of factual statements
- **Risk Assessment**: Three-tier risk classification (High/Medium/Low)
- **Interactive Graph**: Visual representation of claim verification relationships
- **Real-time Analysis**: Instant processing of user queries

### User Interface
- **Three-Panel Layout**: 
  - Left: Input and ChatGPT response
  - Center: Detailed claim analysis
  - Right: Interactive verification graph
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Keyboard Shortcuts**: Ctrl+Enter to analyze, Ctrl+R to reset graph
- **Export Functionality**: Save analysis results as JSON

### Risk Calculation Algorithm
```python
def get_risk_level(claim):
    claude = claim.claude_verification.lower()
    gemini = claim.gemini_verification.lower()
    
    # Both disagree = High risk
    if claude == "no" and gemini == "no":
        return "high"
    
    # Mixed responses = Medium risk  
    if "uncertain" in [claude, gemini] or (claude != gemini):
        return "medium"
    
    # Both agree = Low risk
    if claude == "yes" and gemini == "yes":
        return "low"
```

## 📊 Sample Analysis

**Input**: "Tell me about Isaac Newton"

**ChatGPT Response**: "Isaac Newton was born in 1643. He discovered gravity in 1687. He was born in Berlin."

**Extracted Claims**:
- C1: "Newton was born in 1643" → Claude: Yes, Gemini: Yes → ✅ Low Risk
- C2: "He discovered gravity in 1687" → Claude: Yes, Gemini: Uncertain → ⚠️ Medium Risk  
- C3: "He was born in Berlin" → Claude: No, Gemini: No → ❌ High Risk

## 🔧 Technical Details

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Data Models**: Pydantic for type validation
- **Graph Processing**: NetworkX for relationship analysis
- **CORS**: Enabled for frontend communication

### Frontend (Vanilla JS)
- **Visualization**: Vis.js for interactive graphs
- **Styling**: Modern CSS with gradients and animations
- **Responsiveness**: CSS Grid and Flexbox
- **Accessibility**: ARIA labels and keyboard navigation

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
py -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
http://localhost:8000/static/index.html