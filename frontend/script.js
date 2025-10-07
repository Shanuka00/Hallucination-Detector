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
        displayConfidenceAnalysis(result.confidence_analysis);
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

function displayConfidenceAnalysis(confidenceData) {
    const container = document.getElementById('confidence-analysis');
    if (!container) return;

    if (!confidenceData || (confidenceData.total_claims ?? 0) === 0) {
        container.innerHTML = `
            <div class="placeholder-confidence">
                <p>🎯 No claims to analyze for confidence scoring</p>
            </div>
        `;
        return;
    }

    const overallConfidence = confidenceData.overall_confidence ?? 0;
    const weights = confidenceData.weights_config ?? { alpha: 0.4, beta: 0.4, gamma: 0.2 };

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

    const claimDetailsHtml = (confidenceData.claim_details || []).map((claim) => {
        const confidence = claim.confidence ?? 0;
        const components = claim.components ?? { cross_model_score: 0, external_score: 0, context_score: 0 };

        let confidenceClass = 'low-conf';
        if (confidence >= 0.7) confidenceClass = 'high-conf';
        else if (confidence >= 0.5) confidenceClass = 'medium-conf';

        return `
            <div class="claim-confidence-item ${confidenceClass}">
                <div class="claim-text">${claim.claim_id || 'Claim'}: ${claim.claim_text || ''}</div>
                <div class="confidence-scores">
                    <div class="score-item">
                        <span class="score-label">Cross-Model</span>
                        <span class="score-value">${(components.cross_model_score ?? 0).toFixed(3)}</span>
                    </div>
                    <div class="score-item">
                        <span class="score-label">External</span>
                        <span class="score-value">${(components.external_score ?? 0).toFixed(3)}</span>
                    </div>
                    <div class="score-item">
                        <span class="score-label">Context</span>
                        <span class="score-value">${(components.context_score ?? 0).toFixed(3)}</span>
                    </div>
                    <div class="score-item">
                        <span class="score-label">Final</span>
                        <span class="score-value">${confidence.toFixed(3)}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `
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
            ${claimDetailsHtml || '<p>No per-claim confidence details available.</p>'}
        </div>
        <div class="final-confidence">
            Overall Confidence = Σ(Confidenceᵢ × Weightᵢ) / Σ(Weightᵢ) = ${overallConfidence.toFixed(3)}
        </div>
    `;
}

function displaySummaryStats(summary) {
    const safeSummary = summary || {};
    const totalClaims = safeSummary.total_claims ?? (safeSummary.high || 0) + (safeSummary.medium || 0) + (safeSummary.low || 0);

    const updateStat = (id, value, fallback = '0') => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value ?? fallback;
        }
    };

    updateStat('total-claims', totalClaims, '0');
    updateStat('high-risk', safeSummary.high ?? 0, '0');
    updateStat('medium-risk', safeSummary.medium ?? 0, '0');
    updateStat('low-risk', safeSummary.low ?? 0, '0');

    if (typeof safeSummary.wikipedia_checks === 'number') {
        let externalStats = document.getElementById('external-stats');
        if (!externalStats) {
            const statsContainer = document.querySelector('.stats-grid');
            if (statsContainer) {
                externalStats = document.createElement('div');
                externalStats.id = 'external-stats';
                externalStats.className = 'stat-card';
                statsContainer.appendChild(externalStats);
            }
        }
        if (externalStats) {
            externalStats.innerHTML = `
                <span class="stat-number">${safeSummary.wikipedia_checks}</span>
                <span class="stat-label">External Checks</span>
            `;
        }
    }
}

function displayClaims(claims) {
    const container = document.getElementById('claims-table');
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
        const llm1 = (claim.llm1_verification || 'Uncertain');
        const llm2 = (claim.llm2_verification || 'Uncertain');
        const llm3 = claim.llm3_verification;
        const votingUsed = Boolean(claim.voting_used);
        const isExternalChecked = Boolean(claim.is_wikipedia_checked);
        const externalStatus = (claim.wikipedia_status || 'unclear').toLowerCase();

        // Format LLM names
        const llm1Name = (claim.llm1_name || 'LLM1').toUpperCase();
        const llm2Name = (claim.llm2_name || 'LLM2').toUpperCase();
        const llm3Name = claim.llm3_name ? claim.llm3_name.toUpperCase() : null;

        // Determine verdict badge
        let verdictBadge = '';
        if (finalVerdict === 'Yes') {
            verdictBadge = '<span class="verdict-badge verified">✓ Verified</span>';
        } else if (finalVerdict === 'No') {
            verdictBadge = '<span class="verdict-badge rejected">✗ Rejected</span>';
        } else {
            verdictBadge = '<span class="verdict-badge uncertain">? Uncertain</span>';
        }

        return `
            <div class="claim-item ${verdictClass}" data-claim-id="${claim.id}">
                <div class="claim-header">
                    <span class="claim-id">${claim.id || 'Claim'}</span>
                    ${verdictBadge}
                    ${votingUsed ? '<span class="voting-badge" title="3-way voting used">🗳️ Voted</span>' : ''}
                    ${isExternalChecked ? '<span class="external-badge" title="Verified with External Sources">🌐 Ext</span>' : ''}
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
                    ${isExternalChecked ? `
                    <div class="verifier-response external ${externalStatus}">
                        <strong>External:</strong> ${claim.wikipedia_status || 'Unclear'}
                        ${claim.wikipedia_summary ? `<div class="external-summary">${claim.wikipedia_summary}</div>` : ''}
                    </div>
                    ` : ''}
                </div>
                <div class="final-verdict-row">
                    <strong>Final Verdict:</strong> <span class="verdict-text ${verdictClass}">${finalVerdict}</span>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = claimsHtml;
}

function getRiskLevel(claim) {
    if (claim.final_risk_level) {
        const normalized = claim.final_risk_level.toLowerCase();
        if (normalized === 'low') return 'Low Risk';
        if (normalized === 'medium') return 'Medium Risk';
        if (normalized === 'high') return 'High Risk';
    }

    const llm1 = (claim.llm1_verification || 'uncertain').toLowerCase();
    const llm2 = (claim.llm2_verification || 'uncertain').toLowerCase();
    let baseRisk = 'medium';

    if (llm1 === 'no' && llm2 === 'no') {
        baseRisk = 'high';
    } else if (llm1 === 'yes' && llm2 === 'yes') {
        baseRisk = 'low';
    }

    if (claim.is_wikipedia_checked) {
        const wikiStatus = (claim.wikipedia_status || 'unclear').toLowerCase();
        if (wikiStatus === 'supports' && baseRisk === 'medium') {
            baseRisk = 'low';
        } else if (wikiStatus === 'contradicts') {
            baseRisk = 'high';
        }
    }

    if (baseRisk === 'low') return 'Low Risk';
    if (baseRisk === 'high') return 'High Risk';
    return 'Medium Risk';
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
