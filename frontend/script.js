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

    // Create simplified table
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
                                <span class="verdict-badge ${verdictClass}">${verdictIcon} ${finalVerdict}</span>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = tableHtml;
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
