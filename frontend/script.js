/**
 * Hallucination Detection System - Frontend JavaScript
 * Handles UI interactions, API calls, and graph visualization
 */

// Global variables
let networkInstance = null;
let currentAnalysis = null;
let physicsEnabled = true;

// API configuration
const API_BASE_URL = 'http://localhost:8001';

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Hallucination Detection System initialized');
    setupEventListeners();
    loadSampleData();
});

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Enter key in textarea triggers analysis
    document.getElementById('user-question').addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            analyzeQuery();
        }
    });
    
    // Auto-resize textarea
    const textarea = document.getElementById('user-question');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
}

/**
 * Load sample data for demonstration
 */
function loadSampleData() {
    const sampleQuestions = [
        "Tell me about Isaac Newton",
        "What do you know about Albert Einstein?",
        "Explain World War 2",
        "Describe Python programming language",
        "What is climate change?"
    ];
    
    const questionField = document.getElementById('user-question');
    const randomQuestion = sampleQuestions[Math.floor(Math.random() * sampleQuestions.length)];
    questionField.placeholder = `e.g., ${randomQuestion}`;
}

/**
 * Main function to analyze user query for hallucinations
 */
async function analyzeQuery() {
    const question = document.getElementById('user-question').value.trim();
    
    if (!question) {
        showError('Please enter a question to analyze.');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });
        
        if (!response.ok) {
            throw new Error(`Analysis failed: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        currentAnalysis = result;
        
        // Update UI with results
        displayLLMResponse(result.llm_response);
        displayConfidenceAnalysis(result.confidence_analysis);
        displaySummaryStats(result.summary);
        displayClaims(result.claims);
        displayGraph(result.graph_data);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(`Failed to analyze query: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

/**
 * Display the LLM response
 */
function displayLLMResponse(response) {
    const responseElement = document.getElementById('llm-response');
    responseElement.innerHTML = `<p>${response}</p>`;
    responseElement.classList.remove('placeholder');
}

/**
 * Display confidence analysis
 */
function displayConfidenceAnalysis(confidenceData) {
    const confidenceElement = document.getElementById('confidence-analysis');
    
    if (!confidenceData || confidenceData.total_claims === 0) {
        confidenceElement.innerHTML = `
            <div class="placeholder-confidence">
                <p>🎯 No claims to analyze for confidence scoring</p>
            </div>
        `;
        return;
    }
    
    const overallConfidence = confidenceData.overall_confidence;
    const weights = confidenceData.weights_config;
    
    // Determine assessment level
    let assessmentClass = 'low';
    let assessmentText = '🔴 LOW CONFIDENCE - Response likely contains significant hallucinations';
    
    if (overallConfidence >= 0.8) {
        assessmentClass = 'high';
        assessmentText = '🟢 HIGH CONFIDENCE - Response appears highly reliable';
    } else if (overallConfidence >= 0.6) {
        assessmentClass = 'medium';
        assessmentText = '🟡 MEDIUM CONFIDENCE - Response has moderate reliability';
    } else if (overallConfidence >= 0.4) {
        assessmentClass = 'low-medium';
        assessmentText = '🟠 LOW-MEDIUM CONFIDENCE - Response has concerning elements';
    }
    
    let claimDetailsHtml = '';
    if (confidenceData.claim_details && confidenceData.claim_details.length > 0) {
        claimDetailsHtml = confidenceData.claim_details.map(claim => {
            const confidence = claim.confidence;
            let confClass = 'low-conf';
            if (confidence >= 0.7) confClass = 'high-conf';
            else if (confidence >= 0.5) confClass = 'medium-conf';
            
            const components = claim.components;
            
            return `
                <div class="claim-confidence-item ${confClass}">
                    <div class="claim-text">${claim.claim_id}: ${claim.claim_text}</div>
                    <div class="confidence-scores">
                        <div class="score-item">
                            <span class="score-label">Cross-Model</span>
                            <span class="score-value">${components.cross_model_score.toFixed(3)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">External</span>
                            <span class="score-value">${components.external_score.toFixed(3)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">Context</span>
                            <span class="score-value">${components.context_score.toFixed(3)}</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">Final</span>
                            <span class="score-value">${confidence.toFixed(3)}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    confidenceElement.innerHTML = `
        <div class="confidence-header">
            <div>
                <span class="confidence-score">${overallConfidence.toFixed(3)}</span>
                <div class="confidence-assessment ${assessmentClass}">${assessmentText}</div>
            </div>
        </div>
        
        <div class="confidence-config">
            <div class="config-item">
                <div class="config-label">α (Cross-Model)</div>
                <div class="config-value">${weights.alpha}</div>
            </div>
            <div class="config-item">
                <div class="config-label">β (External)</div>
                <div class="config-value">${weights.beta}</div>
            </div>
            <div class="config-item">
                <div class="config-label">γ (Context)</div>
                <div class="config-value">${weights.gamma}</div>
            </div>
        </div>
        
        <div class="claim-confidence-list">
            ${claimDetailsHtml}
        </div>
        
        <div class="final-confidence">
            Overall Confidence = Σ(Confidence_i × Weight_i) / Σ(Weight_i) = ${overallConfidence.toFixed(3)}
        </div>
    `;
}

/**
 * Display summary statistics
 */
function displaySummaryStats(summary) {
    document.getElementById('total-claims').textContent = summary.total_claims || (summary.high + summary.medium + summary.low);
    document.getElementById('high-risk').textContent = summary.high;
    document.getElementById('medium-risk').textContent = summary.medium;
    document.getElementById('low-risk').textContent = summary.low;
    
    // Add ClaimLLM statistics if available
    if (summary.claimllm_model !== undefined) {
        let claimllmStats = document.getElementById('claimllm-stats');
        if (!claimllmStats) {
            const statsContainer = document.querySelector('.stats-grid');
            claimllmStats = document.createElement('div');
            claimllmStats.id = 'claimllm-stats';
            claimllmStats.className = 'stat-card claimllm-info';
            statsContainer.appendChild(claimllmStats);
        }
        claimllmStats.innerHTML = `
            <div class="claimllm-header">
                <span class="stat-label">🤖 ClaimLLM Service</span>
            </div>
            <div class="claimllm-details">
                <small>Model: ${summary.claimllm_model}</small><br>
                <small>Processing: ${summary.claimllm_processing_time}ms</small><br>
                <small>Confidence: ${(summary.claimllm_confidence * 100).toFixed(1)}%</small>
            </div>
        `;
    }
    
    // Add Wikipedia statistics if available
    if (summary.wikipedia_checks !== undefined) {
        // Update or create Wikipedia stats display
        let wikipediaStats = document.getElementById('wikipedia-stats');
        if (!wikipediaStats) {
            const statsContainer = document.querySelector('.stats-grid');
            wikipediaStats = document.createElement('div');
            wikipediaStats.id = 'wikipedia-stats';
            wikipediaStats.className = 'stat-card';
            statsContainer.appendChild(wikipediaStats);
        }
        wikipediaStats.innerHTML = `
            <span class="stat-number">${summary.wikipedia_checks}</span>
            <span class="stat-label">Wikipedia Checks</span>
        `;
    }
}

/**
 * Display claims analysis
 */
function displayClaims(claims) {
    const container = document.getElementById('claims-table');
    
    if (claims.length === 0) {
        container.innerHTML = `
            <div class="placeholder-claims">
                <p>No factual claims detected in the response.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    claims.forEach(claim => {
        const riskLevel = getRiskLevel(claim) || 'Medium Risk';
        const riskClass = riskLevel.toLowerCase().replace(' ', '-');
        
        html += `
            <div class="claim-item ${riskClass}" data-claim-id="${claim.id}">
                <div class="claim-header">
                    <span class="claim-id">${claim.id}</span>
                    <span class="risk-badge ${riskClass.split('-')[0]}">${riskLevel}</span>
                    ${claim.is_wikipedia_checked ? '<span class="wikipedia-badge" title="Verified with Wikipedia">📖 Wiki</span>' : ''}
                </div>
                <div class="claim-text">${claim.claim}</div>
                <div class="verification-grid">
                    <div class="verifier-response ${(claim.llm1_verification || 'uncertain').toLowerCase()}">
                        <strong>LLM1:</strong> ${claim.llm1_verification || 'Uncertain'}
                    </div>
                    <div class="verifier-response ${(claim.llm2_verification || 'uncertain').toLowerCase()}">
                        <strong>LLM2:</strong> ${claim.llm2_verification || 'Uncertain'}
                    </div>
                    ${claim.is_wikipedia_checked ? `
                    <div class="verifier-response wikipedia ${claim.wikipedia_status ? claim.wikipedia_status.toLowerCase() : 'unclear'}">
                        <strong>Wikipedia:</strong> ${claim.wikipedia_status || 'Unclear'}
                        ${claim.wikipedia_summary ? `<div class="wikipedia-summary">${claim.wikipedia_summary}</div>` : ''}
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Add click handlers for claim items
    document.querySelectorAll('.claim-item').forEach(item => {
        item.addEventListener('click', function() {
            const claimId = this.dataset.claimId;
            highlightClaimInGraph(claimId);
        });
    });
}

/**
 * Get risk level from claim verification
 * Now uses the backend's risk calculation which includes Wikipedia
 */
function getRiskLevel(claim) {
    // Add debugging to see what's in the claim
    console.log('getRiskLevel called with claim:', claim);
    
    // If the backend provides a risk level, use it (includes Wikipedia adjustment)
    if (claim.final_risk_level && claim.final_risk_level !== null && claim.final_risk_level !== '') {
        const riskMap = {
            'low': 'Low Risk',
            'medium': 'Medium Risk', 
            'high': 'High Risk'
        };
        return riskMap[claim.final_risk_level] || 'Medium Risk';
    }
    
    // Fallback to original logic for backward compatibility
    console.log('Using fallback logic for claim:', claim.id);
    
    // Safety checks for verification fields
    if (!claim.llm1_verification || !claim.llm2_verification) {
        console.warn('Missing verification fields in claim:', claim);
        return 'Medium Risk'; // Safe fallback
    }
    
    const llm1 = (claim.llm1_verification || 'uncertain').toLowerCase();
    const llm2 = (claim.llm2_verification || 'uncertain').toLowerCase();
    
    // Base risk assessment
    let baseRisk;
    if (llm1 === 'no' && llm2 === 'no') {
        baseRisk = 'high';
    } else if (llm1 === 'yes' && llm2 === 'yes') {
        baseRisk = 'low';
    } else {
        baseRisk = 'medium';
    }
    
    // Adjust for Wikipedia if checked
    if (claim.is_wikipedia_checked && claim.wikipedia_status) {
        const wikiStatus = (claim.wikipedia_status || 'unclear').toLowerCase();
        if (wikiStatus === 'supports' && baseRisk === 'medium') {
            baseRisk = 'low';
        } else if (wikiStatus === 'contradicts') {
            baseRisk = 'high';
        }
    }
    
    const riskMap = {
        'low': 'Low Risk',
        'medium': 'Medium Risk',
        'high': 'High Risk'
    };
    
    return riskMap[baseRisk] || 'Medium Risk';
}

/**
 * Display the verification graph
 */
function displayGraph(graphData) {
    console.log('Graph data received:', graphData);
    const container = document.getElementById('network-graph');
    
    // Clear any existing placeholder
    container.innerHTML = '';
    
    if (!graphData.nodes || graphData.nodes.length === 0) {
        console.log('No graph nodes available');
        container.innerHTML = `
            <div class="graph-placeholder">
                <p>🕸️ No graph data available</p>
                <small>Claims will be visualized here when available</small>
            </div>
        `;
        return;
    }
    
    // Prepare data for vis.js
    const nodes = new vis.DataSet(graphData.nodes.map(node => ({
        id: node.id,
        label: node.label,
        title: node.title || node.label,
        color: {
            background: node.color,
            border: darkenColor(node.color),
            highlight: {
                background: lightenColor(node.color),
                border: node.color
            }
        },
        size: node.size || 20,
        shape: node.shape || 'dot',
        font: node.font || { color: '#333', size: 12 }
    })));
    
    const edges = new vis.DataSet(graphData.edges.map(edge => ({
        from: edge.from,
        to: edge.to,
        color: edge.color || '#848484',
        width: edge.width || 2,
        dashes: edge.dashes || false,
        title: edge.title || ''
    })));
    
    const data = { nodes, edges };
    
    const options = {
        physics: {
            enabled: physicsEnabled,
            stabilization: { 
                iterations: 200,
                updateInterval: 50
            },
            barnesHut: {
                gravitationalConstant: -2000,
                springConstant: 0.001,
                springLength: 200,
                damping: 0.9
            },
            maxVelocity: 20,
            minVelocity: 0.1,
            timestep: 0.3
        },
        layout: {
            improvedLayout: true
        },
        nodes: {
            borderWidth: 2,
            shadow: true,
            font: {
                size: 12,
                color: '#333'
            }
        },
        edges: {
            shadow: true,
            smooth: {
                type: 'continuous'
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            hideEdgesOnDrag: true
        }
    };
    
    // Create network
    networkInstance = new vis.Network(container, data, options);
    
    // Stop physics after stabilization to prevent infinite animation
    networkInstance.once('stabilizationIterationsDone', function() {
        networkInstance.setOptions({ physics: false });
    });
    
    // Add event listeners
    networkInstance.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            highlightClaim(nodeId);
        }
    });
    
    networkInstance.on('hoverNode', function(params) {
        container.style.cursor = 'pointer';
    });
    
    networkInstance.on('blurNode', function(params) {
        container.style.cursor = 'default';
    });
}

/**
 * Highlight a claim in the graph
 */
function highlightClaimInGraph(claimId) {
    if (networkInstance) {
        networkInstance.selectNodes([claimId]);
        networkInstance.focus(claimId, {
            scale: 1.2,
            animation: {
                duration: 1000,
                easingFunction: 'easeInOutQuad'
            }
        });
    }
}

/**
 * Highlight a claim in the claims list
 */
function highlightClaim(claimId) {
    // Remove existing highlights
    document.querySelectorAll('.claim-item').forEach(item => {
        item.style.boxShadow = '';
        item.style.transform = '';
    });
    
    // Highlight the selected claim
    const claimElement = document.querySelector(`[data-claim-id="${claimId}"]`);
    if (claimElement) {
        claimElement.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.4)';
        claimElement.style.transform = 'scale(1.02)';
        claimElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Reset graph view
 */
function resetGraphView() {
    if (networkInstance) {
        networkInstance.fit({
            animation: {
                duration: 1000,
                easingFunction: 'easeInOutQuad'
            }
        });
    }
}

/**
 * Toggle physics simulation
 */
function togglePhysics() {
    physicsEnabled = !physicsEnabled;
    if (networkInstance) {
        networkInstance.setOptions({ physics: { enabled: physicsEnabled } });
    }
}

/**
 * Change graph layout
 */
function changeLayout() {
    const layout = document.getElementById('layout-select').value;
    
    if (!networkInstance) return;
    
    const layoutOptions = {
        'force-directed': {
            physics: { enabled: true },
            layout: { improvedLayout: true }
        },
        'hierarchical': {
            physics: { enabled: false },
            layout: {
                hierarchical: {
                    direction: 'UD',
                    sortMethod: 'directed',
                    nodeSpacing: 150,
                    levelSeparation: 200
                }
            }
        },
        'circular': {
            physics: { enabled: false },
            layout: {
                hierarchical: false
            }
        }
    };
    
    const options = layoutOptions[layout] || layoutOptions['force-directed'];
    networkInstance.setOptions(options);
    
    // Arrange in circle for circular layout
    if (layout === 'circular' && currentAnalysis) {
        const nodeIds = currentAnalysis.claims.map(claim => claim.id);
        const positions = {};
        const angleStep = (2 * Math.PI) / nodeIds.length;
        const radius = 200;
        
        nodeIds.forEach((nodeId, index) => {
            positions[nodeId] = {
                x: radius * Math.cos(index * angleStep),
                y: radius * Math.sin(index * angleStep)
            };
        });
        
        networkInstance.setPositions(positions);
    }
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = show ? 'flex' : 'none';
    
    // Disable/enable the analyze button
    const button = document.getElementById('analyze-btn');
    button.disabled = show;
    button.textContent = show ? '🔄 Analyzing...' : '🔍 Analyze Hallucinations';
}

/**
 * Show error modal
 */
function showError(message) {
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-modal').style.display = 'flex';
}

/**
 * Close error modal
 */
function closeErrorModal() {
    document.getElementById('error-modal').style.display = 'none';
}

/**
 * Color utility functions
 */
function darkenColor(color) {
    // Simple darkening by reducing brightness
    const hex = color.replace('#', '');
    const r = Math.max(0, parseInt(hex.substr(0, 2), 16) - 30);
    const g = Math.max(0, parseInt(hex.substr(2, 2), 16) - 30);
    const b = Math.max(0, parseInt(hex.substr(4, 2), 16) - 30);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

function lightenColor(color) {
    // Simple lightening by increasing brightness
    const hex = color.replace('#', '');
    const r = Math.min(255, parseInt(hex.substr(0, 2), 16) + 30);
    const g = Math.min(255, parseInt(hex.substr(2, 2), 16) + 30);
    const b = Math.min(255, parseInt(hex.substr(4, 2), 16) + 30);
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

/**
 * Export current analysis data
 */
function exportAnalysis() {
    if (!currentAnalysis) {
        showError('No analysis data to export.');
        return;
    }
    
    const data = {
        timestamp: new Date().toISOString(),
        question: currentAnalysis.original_question,
        analysis: currentAnalysis
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hallucination-analysis-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey) {
        switch(e.key) {
            case 'Enter':
                e.preventDefault();
                analyzeQuery();
                break;
            case 'r':
                e.preventDefault();
                resetGraphView();
                break;
            case 's':
                e.preventDefault();
                exportAnalysis();
                break;
        }
    }
});

// Add keyboard shortcuts info to the UI
setTimeout(() => {
    console.log('Keyboard shortcuts:');
    console.log('Ctrl+Enter: Analyze query');
    console.log('Ctrl+R: Reset graph view');
    console.log('Ctrl+S: Export analysis');
}, 1000);
