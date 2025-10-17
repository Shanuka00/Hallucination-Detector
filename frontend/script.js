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

    // Create summary table
    const tableHtml = `
        <table class="claims-summary-table">
            <thead>
                <tr>
                    <th>Claim ID</th>
                    <th>Claim</th>
                    <th>Final Verdict</th>
                </tr>
            </thead>
            <tbody>
                ${claims.map((claim) => {
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
                        <tr>
                            <td class="claim-id-cell">${claim.id || 'Claim'}</td>
                            <td class="claim-text-cell">${claim.claim || ''}</td>
                            <td class="verdict-cell">
                                <span class="verdict-badge ${verdictClass}">${verdictIcon} ${translateVerdict(finalVerdict)}</span>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;

    tableContainer.innerHTML = tableHtml;
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
