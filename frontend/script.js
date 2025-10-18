/**
 * Hallucination Detection System - Frontend Logic
 * Handles UI interactions, API calls, and result rendering without graph visuals
 */

const API_BASE_URL = 'http://localhost:8001';
let currentAnalysisData = null;

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadSampleData();
});

function setupEventListeners() {
    const questionField = document.getElementById('user-question');
    const analyzeButton = document.getElementById('analyze-btn');

    if (questionField) {
        questionField.addEventListener('keydown', (event) => {
            if (event.ctrlKey && event.key === 'Enter') {
                event.preventDefault();
                analyzeQuery();
            }
        });

        questionField.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = `${this.scrollHeight}px`;
        });
    }

    if (analyzeButton) {
        analyzeButton.addEventListener('click', analyzeQuery);
    }

    document.addEventListener('keydown', (event) => {
        if (!event.ctrlKey) return;

        if (event.key === 'Enter') {
            event.preventDefault();
            analyzeQuery();
        } else if (event.key.toLowerCase() === 's') {
            event.preventDefault();
            exportAnalysis();
        }
    });
}

function loadSampleData() {
    const samples = [
        'Tell me about Isaac Newton',
        'What do you know about Albert Einstein?',
        'Explain World War 2',
        'Describe Python programming language',
        'What is climate change?'
    ];

    const questionField = document.getElementById('user-question');
    if (!questionField) return;

    const randomSample = samples[Math.floor(Math.random() * samples.length)];
    questionField.placeholder = `e.g., ${randomSample}`;
}

async function analyzeQuery() {
    const questionField = document.getElementById('user-question');
    const targetField = document.getElementById('target-llm');

    if (!questionField) return;

    const question = questionField.value.trim();
    const targetLLM = targetField ? targetField.value : 'mistral';

    if (!question) {
        showError('Please enter a question to analyze.');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question,
                target_llm: targetLLM
            })
        });

        if (!response.ok) {
            throw new Error(`${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        currentAnalysisData = result;

        displayLLMResponse(result.llm_response || 'No response received from target model.');
        displayVerifierLLMs(result.claims || []);
        displaySummaryStats(result.summary || {});
        displayClaims(result.claims || []);
    } catch (error) {
        console.error('Analysis error:', error);
        showError(`Failed to analyze query: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function displayLLMResponse(response) {
    const responseElement = document.getElementById('llm-response');
    if (!responseElement) return;
    responseElement.classList.remove('placeholder');
    responseElement.innerHTML = `<p>${response}</p>`;
}

function displayVerifierLLMs(claims) {
    const verifierInfoSection = document.getElementById('verifier-info');
    const verifierDisplay = document.getElementById('verifier-llms');
    
    if (!verifierInfoSection || !verifierDisplay || !claims || claims.length === 0) {
        if (verifierInfoSection) verifierInfoSection.style.display = 'none';
        return;
    }

    // Extract unique verifier LLM names from claims
    const verifierLLMs = new Set();
    claims.forEach(claim => {
        if (claim.llm1_name) verifierLLMs.add(claim.llm1_name);
        if (claim.llm2_name) verifierLLMs.add(claim.llm2_name);
        if (claim.llm3_name) verifierLLMs.add(claim.llm3_name);
    });

    const llmArray = Array.from(verifierLLMs);
    
    if (llmArray.length > 0) {
        verifierInfoSection.style.display = 'block';
        verifierDisplay.innerHTML = `
            <div class="verifier-badges">
                ${llmArray.map((llm, index) => `
                    <div class="verifier-badge">
                        <span class="verifier-number">${index + 1}</span>
                        <span class="verifier-name">${llm.toUpperCase()}</span>
                        <span class="verifier-role">${index < 2 ? 'Primary Verifier' : 'Tiebreaker'}</span>
                    </div>
                `).join('')}
            </div>
            <p class="verifier-note">
                ${llmArray.length === 2 ? 
                    '✓ Primary verifiers agreed on all claims' : 
                    '⚖️ Tiebreaker LLM used for contradicted claims'}
            </p>
        `;
    } else {
        verifierInfoSection.style.display = 'none';
    }
}

function displaySummaryStats(summary) {
    const safeSummary = summary || {};

    const updateStat = (id, value, fallback = '0') => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value ?? fallback;
        }
    };

    updateStat('total-claims', safeSummary.total_claims ?? 0, '0');
    updateStat('verified-claims', safeSummary.verified ?? 0, '0');
    updateStat('refuted-claims', safeSummary.refuted ?? 0, '0');
    updateStat('uncertain-claims', safeSummary.uncertain ?? 0, '0');
}

function translateVerdict(backendVerdict) {
    const verdictMap = {
        'Yes': 'Verified',
        'No': 'Risky Hallucination',
        'Uncertain': 'Potential Hallucination'
    };
    return verdictMap[backendVerdict] || backendVerdict;
}

function displayClaims(claims) {
    displayDetailedClaims(claims);
    displaySummaryTable(claims);
}

function displayDetailedClaims(claims) {
    const container = document.getElementById('claims-details');
    if (!container) return;

    if (!claims || claims.length === 0) {
        container.innerHTML = `
            <div class="placeholder-claims">
                <p>No factual claims detected in the response.</p>
            </div>
        `;
        return;
    }

    const claimsHtml = claims.map((claim) => {
        const finalVerdict = (claim.final_verdict || 'Uncertain');
        const verdictClass = finalVerdict.toLowerCase();
        const llm1 = (claim.llm1_verification || claim.llm1_result || 'Uncertain');
        const llm2 = (claim.llm2_verification || claim.llm2_result || 'Uncertain');
        const llm3 = claim.llm3_verification || claim.llm3_result;
        const votingUsed = Boolean(claim.voting_used);

        const llm1Name = (claim.llm1_name || 'LLM1').toUpperCase();
        const llm2Name = (claim.llm2_name || 'LLM2').toUpperCase();
        const llm3Name = claim.llm3_name ? claim.llm3_name.toUpperCase() : null;

        let verdictBadge = '';
        if (finalVerdict === 'Yes') {
            verdictBadge = '<span class="verdict-badge verified">✓ Verified</span>';
        } else if (finalVerdict === 'No') {
            verdictBadge = '<span class="verdict-badge rejected">✗ Risky Hallucination</span>';
        } else {
            verdictBadge = '<span class="verdict-badge uncertain">? Potential Hallucination</span>';
        }

        return `
            <div class="claim-item ${verdictClass}" data-claim-id="${claim.id}">
                <div class="claim-header">
                    <span class="claim-id">${claim.id || 'Claim'}</span>
                    ${verdictBadge}
                    ${votingUsed ? '<span class="voting-badge" title="3-way voting used">🗳️ Voted</span>' : ''}
                </div>
                <div class="claim-text">${claim.claim || ''}</div>
                <div class="verification-grid">
                    <div class="verifier-response ${llm1.toLowerCase()}">
                        <strong>${llm1Name}:</strong> ${llm1}
                    </div>
                    <div class="verifier-response ${llm2.toLowerCase()}">
                        <strong>${llm2Name}:</strong> ${llm2}
                    </div>
                    ${votingUsed && llm3 ? `
                    <div class="verifier-response ${llm3.toLowerCase()} voting">
                        <strong>${llm3Name} (Tiebreaker):</strong> ${llm3}
                    </div>
                    ` : ''}
                </div>
                <div class="final-verdict-row">
                    <strong>Final Verdict:</strong> <span class="verdict-text ${verdictClass}">${translateVerdict(finalVerdict)}</span>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = claimsHtml;
}

function displaySummaryTable(claims) {
    const tableSection = document.getElementById('summary-table-section');
    const tableContainer = document.getElementById('claims-summary-table');
    
    if (!tableSection || !tableContainer) return;

    if (!claims || claims.length === 0) {
        tableSection.style.display = 'none';
        return;
    }

    // Show the section
    tableSection.style.display = 'block';

    // Create summary table with annotation column
    const tableHtml = `
        <table class="claims-summary-table">
            <thead>
                <tr>
                    <th>Claim ID</th>
                    <th>Claim</th>
                    <th>Final Verdict</th>
                    <th>Manual Annotation</th>
                </tr>
            </thead>
            <tbody>
                ${claims.map((claim, index) => {
                    const finalVerdict = (claim.final_verdict || 'Uncertain');
                    let verdictClass = '';
                    let verdictIcon = '';
                    
                    if (finalVerdict === 'Yes') {
                        verdictClass = 'verified';
                        verdictIcon = '✅';
                    } else if (finalVerdict === 'No') {
                        verdictClass = 'refuted';
                        verdictIcon = '❌';
                    } else {
                        verdictClass = 'uncertain';
                        verdictIcon = '❓';
                    }

                    return `
                        <tr data-claim-id="${claim.id}" data-claim-index="${index}">
                            <td class="claim-id-cell">${claim.id || 'Claim'}</td>
                            <td class="claim-text-cell">${claim.claim || ''}</td>
                            <td class="verdict-cell">
                                <span class="verdict-badge ${verdictClass}">${verdictIcon} ${translateVerdict(finalVerdict)}</span>
                            </td>
                            <td class="annotation-cell">
                                <button class="annotation-btn-small correct" 
                                        onclick="annotateClaimInTable('${claim.id}', 'correct', ${index})"
                                        data-annotation="correct">
                                    ✓
                                </button>
                                <button class="annotation-btn-small incorrect" 
                                        onclick="annotateClaimInTable('${claim.id}', 'incorrect', ${index})"
                                        data-annotation="incorrect">
                                    ✗
                                </button>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
        <div class="annotation-controls">
            <div class="annotation-progress">
                <span id="annotation-count">0</span> / <span id="total-claims">${claims.length}</span> annotated
            </div>
            <button id="calculate-metrics-btn-simple" class="btn btn-success" disabled onclick="calculateMetricsSimple()">
                📊 Calculate Metrics
            </button>
            <button id="clear-annotations-btn-simple" class="btn btn-secondary" onclick="clearAnnotationsSimple()">
                🔄 Clear All
            </button>
        </div>
        <div id="metrics-results-simple" class="metrics-results-simple" style="display: none;">
            <h3>📈 Evaluation Results</h3>
            <div class="metrics-grid-simple">
                <div class="metric-card-simple">
                    <div class="metric-label-simple">Precision</div>
                    <div class="metric-value-simple" id="precision-simple">-</div>
                </div>
                <div class="metric-card-simple">
                    <div class="metric-label-simple">Recall</div>
                    <div class="metric-value-simple" id="recall-simple">-</div>
                </div>
                <div class="metric-card-simple">
                    <div class="metric-label-simple">F1-Score</div>
                    <div class="metric-value-simple" id="f1-simple">-</div>
                </div>
                <div class="metric-card-simple">
                    <div class="metric-label-simple">Accuracy</div>
                    <div class="metric-value-simple" id="accuracy-simple">-</div>
                </div>
            </div>
            <div class="confusion-matrix-simple">
                <h4>Confusion Matrix</h4>
                <div class="cm-row">
                    <div class="cm-item">TP: <strong id="tp-simple">0</strong></div>
                    <div class="cm-item">FP: <strong id="fp-simple">0</strong></div>
                    <div class="cm-item">TN: <strong id="tn-simple">0</strong></div>
                    <div class="cm-item">FN: <strong id="fn-simple">0</strong></div>
                </div>
            </div>
        </div>
    `;

    tableContainer.innerHTML = tableHtml;
    
    // Store claims for annotation
    currentClaims = claims;
    currentAnnotations = {};
}



function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    const button = document.getElementById('analyze-btn');

    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
    }

    if (button) {
        button.disabled = show;
        button.textContent = show ? '🔄 Analyzing...' : '🔍 Analyze Hallucinations';
    }
}

function showError(message) {
    const modal = document.getElementById('error-modal');
    const messageElement = document.getElementById('error-message');

    if (messageElement) {
        messageElement.textContent = message;
    }

    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeErrorModal() {
    const modal = document.getElementById('error-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function exportAnalysis() {
    if (!currentAnalysisData) {
        showError('No analysis data to export.');
        return;
    }

    const payload = {
        timestamp: new Date().toISOString(),
        question: currentAnalysisData.original_question,
        analysis: currentAnalysisData
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `hallucination-analysis-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// ============================================================================
// Manual Annotation System for TruthfulQA Evaluation
// ============================================================================

// Global state for annotations
let currentAnnotations = {};
let currentQuestionId = null;
let currentTargetModel = null;
let currentClaims = [];

/**
 * Display annotation UI after analysis completes
 * Call this function after displayClaims() to enable annotation
 */
function enableAnnotationMode(claims, questionId, targetModel) {
    currentQuestionId = questionId;
    currentTargetModel = targetModel;
    currentClaims = claims;
    currentAnnotations = {};
    
    // Show annotation section
    const annotationSection = document.getElementById('annotation-section');
    annotationSection.style.display = 'block';
    
    // Update question info
    document.getElementById('question-info').style.display = 'grid';
    document.getElementById('current-question-id').textContent = questionId;
    document.getElementById('current-target-model').textContent = targetModel.toUpperCase();
    document.getElementById('total-claims-count').textContent = claims.length;
    
    // Populate annotation table
    const tbody = document.getElementById('annotation-tbody');
    tbody.innerHTML = '';
    
    claims.forEach((claim, index) => {
        const row = document.createElement('tr');
        row.setAttribute('data-claim-id', claim.id);
        
        const verdictClass = claim.final_verdict.toLowerCase();
        
        row.innerHTML = `
            <td><strong>C${index + 1}</strong></td>
            <td class="claim-text">${claim.claim}</td>
            <td>
                <span class="verdict-badge ${verdictClass}">
                    ${translateVerdict(claim.final_verdict)}
                </span>
            </td>
            <td>
                <div class="annotation-buttons">
                    <button class="annotation-btn correct" 
                            data-claim-id="${claim.id}"
                            onclick="annotateClaim('${claim.id}', 'correct', event)">
                        ✓ Correct
                    </button>
                    <button class="annotation-btn incorrect" 
                            data-claim-id="${claim.id}"
                            onclick="annotateClaim('${claim.id}', 'incorrect', event)">
                        ✗ Incorrect
                    </button>
                </div>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    
    // Reset buttons
    updateSaveButtonState();
    document.getElementById('calculate-metrics-btn').disabled = true;
    document.getElementById('eval-results').style.display = 'none';
    
    // Save predictions for later comparison
    savePredictions(claims, questionId, targetModel);
    
    // Scroll to annotation section
    setTimeout(() => {
        annotationSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
}

/**
 * Handle claim annotation
 */
function annotateClaim(claimId, annotation, event) {
    currentAnnotations[claimId] = annotation;
    
    // Visual feedback - update button states
    const row = event.target.closest('tr');
    const buttons = row.querySelectorAll('.annotation-btn');
    buttons.forEach(btn => btn.classList.remove('selected'));
    event.target.classList.add('selected');
    
    // Mark row as annotated
    row.classList.add('annotated');
    
    // Update save button state
    updateSaveButtonState();
}

/**
 * Update save button state based on annotation progress
 */
function updateSaveButtonState() {
    const totalClaims = currentClaims.length;
    const annotatedClaims = Object.keys(currentAnnotations).length;
    
    const saveBtn = document.getElementById('save-annotations-btn');
    saveBtn.textContent = `💾 Save Annotations (${annotatedClaims}/${totalClaims})`;
    saveBtn.disabled = annotatedClaims < totalClaims;
    
    // Update progress indication
    if (annotatedClaims === totalClaims) {
        saveBtn.style.background = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
        showNotification(`All ${totalClaims} claims annotated! Ready to save.`, 'success');
    }
}

/**
 * Save predictions to backend for later comparison
 */
async function savePredictions(claims, questionId, targetModel) {
    try {
        const predictions = {};
        claims.forEach(claim => {
            predictions[claim.id] = {
                claim: claim.claim,
                final_verdict: claim.final_verdict,
                llm1_response: claim.llm1_verification || claim.llm1_result,
                llm2_response: claim.llm2_verification || claim.llm2_result,
                llm3_response: claim.llm3_verification || claim.llm3_result
            };
        });
        
        const response = await fetch(`${API_BASE_URL}/api/save-predictions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: questionId,
                target_model: targetModel,
                predictions: predictions
            })
        });
        
        const result = await response.json();
        console.log('Predictions saved:', result);
        
    } catch (error) {
        console.error('Error saving predictions:', error);
    }
}

/**
 * Save manual annotations
 */
async function saveAnnotations() {
    if (!currentQuestionId || !currentTargetModel) {
        showNotification('No question data available', 'error');
        return;
    }
    
    const totalClaims = currentClaims.length;
    const annotatedClaims = Object.keys(currentAnnotations).length;
    
    if (annotatedClaims < totalClaims) {
        showNotification(`Please annotate all ${totalClaims} claims before saving`, 'error');
        return;
    }
    
    try {
        showNotification('Saving annotations...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/api/save-annotation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: currentQuestionId,
                target_model: currentTargetModel,
                annotations: currentAnnotations,
                timestamp: new Date().toISOString()
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showNotification('✓ Annotations saved successfully!', 'success');
            document.getElementById('calculate-metrics-btn').disabled = false;
            document.getElementById('save-annotations-btn').style.background = 
                'linear-gradient(135deg, #718096 0%, #4a5568 100%)';
        } else {
            showNotification('Failed to save annotations', 'error');
        }
        
    } catch (error) {
        console.error('Error saving annotations:', error);
        showNotification('✗ Error saving annotations', 'error');
    }
}

/**
 * Calculate metrics for current question
 */
async function calculateMetrics() {
    if (!currentQuestionId || !currentTargetModel) {
        showNotification('No question data available', 'error');
        return;
    }
    
    try {
        showNotification('Calculating metrics...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/api/calculate-metrics`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: currentQuestionId,
                target_model: currentTargetModel
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            const metrics = result.metrics;
            
            // Display metrics
            document.getElementById('precision-value').textContent = 
                (metrics.precision * 100).toFixed(1) + '%';
            document.getElementById('recall-value').textContent = 
                (metrics.recall * 100).toFixed(1) + '%';
            document.getElementById('f1-value').textContent = 
                (metrics.f1_score * 100).toFixed(1) + '%';
            document.getElementById('accuracy-value').textContent = 
                (metrics.accuracy * 100).toFixed(1) + '%';
            
            // Display confusion matrix
            const cm = metrics.confusion_matrix;
            document.getElementById('cm-tp').textContent = cm.tp;
            document.getElementById('cm-fp').textContent = cm.fp;
            document.getElementById('cm-tn').textContent = cm.tn;
            document.getElementById('cm-fn').textContent = cm.fn;
            
            document.getElementById('eval-results').style.display = 'block';
            
            showNotification('✓ Metrics calculated and saved!', 'success');
            
            // Scroll to results
            setTimeout(() => {
                document.getElementById('eval-results').scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'nearest' 
                });
            }, 300);
            
        } else {
            showNotification('Failed to calculate metrics', 'error');
        }
        
    } catch (error) {
        console.error('Error calculating metrics:', error);
        showNotification('✗ Error calculating metrics', 'error');
    }
}

/**
 * Clear all annotations
 */
function clearAnnotations() {
    if (!confirm('Are you sure you want to clear all annotations for this question?')) {
        return;
    }
    
    currentAnnotations = {};
    
    // Reset UI
    const rows = document.querySelectorAll('#annotation-tbody tr');
    rows.forEach(row => {
        row.classList.remove('annotated');
        const buttons = row.querySelectorAll('.annotation-btn');
        buttons.forEach(btn => btn.classList.remove('selected'));
    });
    
    updateSaveButtonState();
    document.getElementById('calculate-metrics-btn').disabled = true;
    document.getElementById('eval-results').style.display = 'none';
    
    showNotification('Annotations cleared', 'info');
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add keyframe for slideOutRight
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Setup event listeners for annotation buttons
document.addEventListener('DOMContentLoaded', () => {
    const saveBtn = document.getElementById('save-annotations-btn');
    const calcBtn = document.getElementById('calculate-metrics-btn');
    const clearBtn = document.getElementById('clear-annotations-btn');
    
    if (saveBtn) {
        saveBtn.addEventListener('click', saveAnnotations);
    }
    
    if (calcBtn) {
        calcBtn.addEventListener('click', calculateMetrics);
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAnnotations);
    }
});

// ===========================================
// ANNOTATION FUNCTIONS (Simple In-Table)
// ===========================================

function annotateClaimInTable(claimId, annotation, claimIndex) {
    // Store annotation
    currentAnnotations[claimId] = annotation;
    
    // Update button states
    const row = document.querySelector(`tr[data-claim-index="${claimIndex}"]`);
    if (!row) return;
    
    const correctBtn = row.querySelector('.annotation-btn-small.correct');
    const incorrectBtn = row.querySelector('.annotation-btn-small.incorrect');
    
    if (annotation === 'correct') {
        correctBtn.classList.add('selected');
        incorrectBtn.classList.remove('selected');
    } else {
        incorrectBtn.classList.add('selected');
        correctBtn.classList.remove('selected');
    }
    
    // Update progress
    updateAnnotationProgress();
}

function updateAnnotationProgress() {
    const annotatedCount = Object.keys(currentAnnotations).length;
    const totalClaims = currentClaims.length;
    
    const countSpan = document.getElementById('annotation-count');
    const totalSpan = document.getElementById('total-claims');
    const calculateBtn = document.getElementById('calculate-metrics-btn-simple');
    
    if (countSpan) countSpan.textContent = annotatedCount;
    if (totalSpan) totalSpan.textContent = totalClaims;
    
    // Enable calculate button if all claims are annotated
    if (calculateBtn) {
        calculateBtn.disabled = annotatedCount < totalClaims;
    }
}

function clearAnnotationsSimple() {
    currentAnnotations = {};
    
    // Clear all button selections
    document.querySelectorAll('.annotation-btn-small').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Hide results
    const resultsDiv = document.getElementById('metrics-results-simple');
    if (resultsDiv) resultsDiv.style.display = 'none';
    
    updateAnnotationProgress();
}

async function calculateMetricsSimple() {
    if (currentClaims.length === 0) {
        alert('No claims to evaluate!');
        return;
    }
    
    if (Object.keys(currentAnnotations).length < currentClaims.length) {
        alert('Please annotate all claims before calculating metrics.');
        return;
    }
    
    // Calculate metrics - System Verdict Correctness Evaluation
    // User annotates: ✓ = "System verdict is CORRECT", ✗ = "System verdict is WRONG"
    // 
    // TP: System said "Verified" ✅ + Verdict is CORRECT ✓ → System correctly verified
    // FP: System said "Verified" ✅ + Verdict is WRONG ✗ → System wrongly verified
    // TN: System said "Risky/Uncertain" ❌ + Verdict is CORRECT ✓ → System correctly rejected
    // FN: System said "Risky/Uncertain" ❌ + Verdict is WRONG ✗ → System wrongly rejected
    
    let tp = 0, fp = 0, tn = 0, fn = 0;
    
    currentClaims.forEach(claim => {
        const systemVerdict = claim.final_verdict.toLowerCase();
        const userAnnotation = currentAnnotations[claim.id];
        
        // Map system verdict to binary: "verified" (Yes) vs "risky/uncertain" (No/Uncertain)
        // Backend sends: "Yes", "No", or "Uncertain"
        const systemSaidVerified = (systemVerdict === 'yes');
        const verdictIsCorrect = (userAnnotation === 'correct');
        
        if (systemSaidVerified && verdictIsCorrect) {
            tp++; // System said "Verified" + Verdict is correct → TP ✅
        } else if (systemSaidVerified && !verdictIsCorrect) {
            fp++; // System said "Verified" + Verdict is wrong → FP ❌
        } else if (!systemSaidVerified && verdictIsCorrect) {
            tn++; // System said "Risky" + Verdict is correct → TN ✅
        } else if (!systemSaidVerified && !verdictIsCorrect) {
            fn++; // System said "Risky" + Verdict is wrong → FN ❌
        }
    });
    
    const totalClaims = currentClaims.length;
    
    // Calculate metrics using traditional formulas
    const precision = (tp + fp) > 0 ? tp / (tp + fp) : 0;
    const recall = (tp + fn) > 0 ? tp / (tp + fn) : 0;
    const f1 = (precision + recall) > 0 ? 2 * (precision * recall) / (precision + recall) : 0;
    const accuracy = (tp + tn) / totalClaims;
    
    // Display results
    displayMetricsSimple({
        precision,
        recall,
        f1_score: f1,
        accuracy,
        confusion_matrix: { tp, fp, tn, fn }
    });
    
    // Optional: Save to backend for tracking
    try {
        const targetModel = document.getElementById('target-model').value;
        await fetch(`${API_BASE_URL}/api/save-annotation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: `Q_${Date.now()}`,
                target_model: targetModel,
                claims: currentClaims.map(claim => ({
                    claim_id: claim.id,
                    claim_text: claim.claim,
                    system_verdict: claim.final_verdict,
                    user_annotation: currentAnnotations[claim.id]
                }))
            })
        });
    } catch (error) {
        console.log('Could not save to backend (optional):', error);
    }
}

function displayMetricsSimple(metrics) {
    const resultsDiv = document.getElementById('metrics-results-simple');
    if (!resultsDiv) return;
    
    resultsDiv.style.display = 'block';
    
    // Update metric values (show as decimals, not percentages)
    document.getElementById('precision-simple').textContent = metrics.precision.toFixed(4);
    document.getElementById('recall-simple').textContent = metrics.recall.toFixed(4);
    document.getElementById('f1-simple').textContent = metrics.f1_score.toFixed(4);
    document.getElementById('accuracy-simple').textContent = metrics.accuracy.toFixed(4);
    
    // Update confusion matrix with all four values
    const cm = metrics.confusion_matrix;
    document.getElementById('tp-simple').textContent = cm.tp + ' (Verified ✅ + Verdict Correct ✓)';
    document.getElementById('fp-simple').textContent = cm.fp + ' (Verified ✅ + Verdict Wrong ✗)';
    document.getElementById('tn-simple').textContent = cm.tn + ' (Risky ❌ + Verdict Correct ✓)';
    document.getElementById('fn-simple').textContent = cm.fn + ' (Risky ❌ + Verdict Wrong ✗)';
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}