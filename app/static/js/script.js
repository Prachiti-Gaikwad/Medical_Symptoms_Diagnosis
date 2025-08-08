// Global variables
let currentLanguage = 'en';
let currentDiagnoses = []; // Store current diagnoses for modal access
let isRecording = false;
let recognition = null;
let currentMode = 'symptoms'; // Current mode: 'symptoms' or 'chatbot'
let chatSessionId = null; // Chat session identifier
let selectedImageFile = null; // Selected image file for upload

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application initialized');
    setupEventListeners();
    initializeSpeechRecognition(); // Initialize speech recognition
});

// Event Listeners Setup
function setupEventListeners() {
    // Analyze button
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            const symptoms = document.getElementById('symptomsInput').value.trim();
            if (symptoms) {
                analyzeSymptoms(symptoms);
            } else {
                showError('Please enter your symptoms');
            }
        });
    }

    // Enter key in symptoms input
    const symptomsInput = document.getElementById('symptomsInput');
    if (symptomsInput) {
        symptomsInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const symptoms = this.value.trim();
                if (symptoms) {
                    analyzeSymptoms(symptoms);
                }
            }
        });
    }

    // Language selector
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.addEventListener('change', function() {
            currentLanguage = this.value;
            console.log('Language changed to:', currentLanguage);
        });
    }

    // Clear button
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            const symptomsInput = document.getElementById('symptomsInput');
            if (symptomsInput) {
                symptomsInput.value = '';
                hideError();
                const resultsSection = document.getElementById('resultsSection');
                if (resultsSection) {
                    resultsSection.style.display = 'none';
                }
            }
        });
    }

    // Voice input button
    const voiceBtn = document.getElementById('voiceInputBtn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', toggleVoiceRecording);
    }
}

// Initialize speech recognition
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            console.log('Voice recognition started');
            updateVoiceButton(true);
            showVoiceStatus(true);
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('symptomsInput').value = transcript;
            console.log('Voice input:', transcript);
            showNotification('Voice input received: ' + transcript, 'success');
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            updateVoiceButton(false);
            showVoiceStatus(false);
            showNotification('Voice recognition error: ' + event.error, 'error');
        };
        
        recognition.onend = function() {
            console.log('Voice recognition ended');
            updateVoiceButton(false);
            showVoiceStatus(false);
        };
    } else {
        console.warn('Speech recognition not supported');
        hideVoiceButton();
    }
}

// Update voice button appearance
function updateVoiceButton(recording) {
    const voiceBtn = document.getElementById('voiceInputBtn');
    const voiceIcon = voiceBtn ? voiceBtn.querySelector('i') : null;
    
    if (voiceBtn) {
        if (recording) {
            voiceBtn.classList.add('recording');
            voiceIcon.className = 'fas fa-stop';
            voiceBtn.title = 'Stop recording';
        } else {
            voiceBtn.classList.remove('recording');
            voiceIcon.className = 'fas fa-microphone';
            voiceBtn.title = 'Voice input';
        }
    }
}

// Show/hide voice status
function showVoiceStatus(show) {
    const voiceStatus = document.getElementById('voiceStatus');
    const voiceStatusText = document.getElementById('voiceStatusText');
    const voiceVisualizer = document.getElementById('voiceVisualizer');
    
    if (voiceStatus) {
        voiceStatus.style.display = show ? 'flex' : 'none';
    }
    
    if (voiceStatusText) {
        voiceStatusText.textContent = show ? 'Listening...' : '';
    }
    
    if (voiceVisualizer) {
        voiceVisualizer.style.display = show ? 'flex' : 'none';
    }
}

// Hide voice button if not supported
function hideVoiceButton() {
    const voiceBtn = document.getElementById('voiceInputBtn');
    if (voiceBtn) {
        voiceBtn.style.display = 'none';
    }
}

// Toggle voice recording
function toggleVoiceRecording() {
    if (!recognition) {
        showNotification('Voice recognition not supported in this browser', 'error');
        return;
    }
    
    if (isRecording) {
        recognition.stop();
        isRecording = false;
    } else {
        recognition.start();
        isRecording = true;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Main Analysis Function
async function analyzeSymptoms(symptoms) {
    if (!symptoms.trim()) {
        showError('Please enter your symptoms');
        return;
    }

    showLoading();
    hideError();

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symptoms: symptoms,
                language: currentLanguage
            })
        });

        const data = await response.json();
        hideLoading();
        
        console.log('Response data:', data);
        
        if (data.success && data.data) {
            // Store diagnoses globally for modal access
            currentDiagnoses = data.data.potential_diagnoses || [];
            displayResults(data.data);
        } else {
            showError(data.error || 'Analysis failed. Please try again.');
        }
        
    } catch (error) {
        console.error('Error during analysis:', error);
        hideLoading();
        showError('An error occurred during analysis. Please try again.');
    }
}

// UI Functions
function showLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) {
        loadingSpinner.style.display = 'block';
    }
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    }
    
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.style.display = 'block';
    }
}

function hideLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) {
        loadingSpinner.style.display = 'none';
    }
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Symptoms';
    }
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    if (errorMessage) {
        errorMessage.style.display = 'block';
    }
    if (errorText) {
        errorText.textContent = message;
    }
    
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.style.display = 'block';
    }
}

function hideError() {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.style.display = 'none';
    }
}

// Display Results Function
function displayResults(data) {
    try {
        const resultsContainer = document.getElementById('analysisResults');
        if (!resultsContainer) {
            console.error('Results container not found');
            return;
        }

        // Clear previous results
        resultsContainer.innerHTML = '';

        if (data.potential_diagnoses && data.potential_diagnoses.length > 0) {
            // Sort diagnoses by confidence (highest first)
            const sortedDiagnoses = [...data.potential_diagnoses].sort((a, b) => b.confidence - a.confidence);
            
            let resultsHtml = `
                <div class="analysis-header">
                    <h3><i class="fas fa-stethoscope"></i> Medical Analysis Results</h3>
                    <p class="analysis-method">Analysis Method: ${data.analysis_method || 'AI-Powered Analysis'}</p>
                    
                    ${data.corrected_symptoms ? `
                        <div class="symptom-correction">
                            <h4><i class="fas fa-spell-check"></i> Symptom Correction</h4>
                            <div class="correction-details">
                                <p><strong>Original:</strong> <span class="original-text">${data.symptom_corrections?.original || 'N/A'}</span></p>
                                <p><strong>Corrected:</strong> <span class="corrected-text">${data.corrected_symptoms}</span></p>
                                ${data.symptom_corrections?.interpretations && data.symptom_corrections.interpretations.length > 0 ? `
                                    <p><strong>Interpretations:</strong> <span class="interpretations">${data.symptom_corrections.interpretations.join(', ')}</span></p>
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="diagnosis-summary">
                        <span class="diagnosis-count"><i class="fas fa-list"></i> ${sortedDiagnoses.length} Potential Diagnosis${sortedDiagnoses.length > 1 ? 'es' : ''}</span>
                        <span class="best-match"><i class="fas fa-star"></i> Best Match: ${sortedDiagnoses[0].condition} (${sortedDiagnoses[0].confidence}%)</span>
                    </div>
                </div>
                
                <div class="diagnosis-options">
                    <h4><i class="fas fa-arrow-down"></i> Diagnosis Options (Ranked by Confidence)</h4>
                </div>
            `;

            // Display each diagnosis with ranking
            sortedDiagnoses.forEach((diagnosis, index) => {
                const severityClass = getSeverityClass(diagnosis.severity);
                const confidenceClass = getConfidenceClass(diagnosis.confidence);
                const isTopMatch = index === 0;
                
                resultsHtml += `
                    <div class="diagnosis-card ${isTopMatch ? 'top-match' : ''}" onclick="showDiseaseDetails(${index})">
                        <div class="diagnosis-header">
                            <div class="diagnosis-rank">
                                <span class="rank-number">${index + 1}</span>
                                ${isTopMatch ? '<i class="fas fa-crown top-match-icon"></i>' : ''}
                            </div>
                            <div class="diagnosis-title">
                                <h4>${diagnosis.condition}</h4>
                                ${isTopMatch ? '<span class="best-match-badge">Best Match</span>' : ''}
                            </div>
                            <div class="diagnosis-meta">
                                <span class="confidence ${confidenceClass}">
                                    <i class="fas fa-percentage"></i> ${diagnosis.confidence}% Confidence
                                </span>
                                <span class="severity ${severityClass}">
                                    <i class="fas fa-exclamation-triangle"></i> ${diagnosis.severity} Severity
                                </span>
                            </div>
                        </div>
                        
                        <div class="diagnosis-content">
                            <p class="diagnosis-description"><strong>Description:</strong> ${diagnosis.description}</p>
                            
                            <div class="diagnosis-preview">
                                ${diagnosis.immediate_actions ? `
                                    <div class="preview-section">
                                        <strong><i class="fas fa-exclamation"></i> Immediate Actions:</strong>
                                        <p>${diagnosis.immediate_actions.slice(0, 2).join(', ')}${diagnosis.immediate_actions.length > 2 ? '...' : ''}</p>
                                    </div>
                                ` : ''}
                                
                                ${diagnosis.medicine_recommendations ? `
                                    <div class="preview-section medicine-preview">
                                        <strong><i class="fas fa-pills"></i> Medicine Recommendations:</strong>
                                        <div class="medicine-summary">
                                            ${diagnosis.medicine_recommendations.otc_medicines && diagnosis.medicine_recommendations.otc_medicines.length > 0 ? 
                                                `<span class="medicine-type otc"><i class="fas fa-pills"></i> ${diagnosis.medicine_recommendations.otc_medicines.length} OTC</span>` : ''}
                                            ${diagnosis.medicine_recommendations.prescription_medicines && diagnosis.medicine_recommendations.prescription_medicines.length > 0 ? 
                                                `<span class="medicine-type prescription"><i class="fas fa-syringe"></i> ${diagnosis.medicine_recommendations.prescription_medicines.length} Prescription</span>` : ''}
                                            ${diagnosis.medicine_recommendations.natural_remedies && diagnosis.medicine_recommendations.natural_remedies.length > 0 ? 
                                                `<span class="medicine-type natural"><i class="fas fa-leaf"></i> ${diagnosis.medicine_recommendations.natural_remedies.length} Natural</span>` : ''}
                                            ${diagnosis.medicine_recommendations.medical_literature && diagnosis.medicine_recommendations.medical_literature.length > 0 ? 
                                                `<span class="medicine-type literature"><i class="fas fa-book-medical"></i> ${diagnosis.medicine_recommendations.medical_literature.length} Research</span>` : ''}
                                        </div>
                                        <div class="medicine-preview-list">
                                            ${diagnosis.medicine_recommendations.otc_medicines && diagnosis.medicine_recommendations.otc_medicines.length > 0 ? 
                                                `<div class="preview-item"><strong>💊 OTC:</strong> ${diagnosis.medicine_recommendations.otc_medicines.slice(0, 2).map(med => med.name).join(', ')}${diagnosis.medicine_recommendations.otc_medicines.length > 2 ? '...' : ''}</div>` : ''}
                                            ${diagnosis.medicine_recommendations.prescription_medicines && diagnosis.medicine_recommendations.prescription_medicines.length > 0 ? 
                                                `<div class="preview-item"><strong>💉 Prescription:</strong> ${diagnosis.medicine_recommendations.prescription_medicines.slice(0, 2).map(med => med.name).join(', ')}${diagnosis.medicine_recommendations.prescription_medicines.length > 2 ? '...' : ''}</div>` : ''}
                                            ${diagnosis.medicine_recommendations.natural_remedies && diagnosis.medicine_recommendations.natural_remedies.length > 0 ? 
                                                `<div class="preview-item"><strong>🌿 Natural:</strong> ${diagnosis.medicine_recommendations.natural_remedies.slice(0, 2).map(remedy => remedy.name).join(', ')}${diagnosis.medicine_recommendations.natural_remedies.length > 2 ? '...' : ''}</div>` : ''}
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                            
                            <div class="click-hint">
                                <i class="fas fa-hand-pointer"></i> Click for detailed information
                            </div>
                        </div>
                    </div>
                `;
            });

            // Add recommendations if available
            if (data.recommendations && data.recommendations.length > 0) {
                resultsHtml += `
                    <div class="recommendations-card">
                        <h4><i class="fas fa-lightbulb"></i> General Recommendations</h4>
                        <ul>
                            ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            // Add warnings if available
            if (data.warnings && data.warnings.length > 0) {
                resultsHtml += `
                    <div class="warnings-card">
                        <h4><i class="fas fa-exclamation-triangle"></i> Important Warnings</h4>
                        <ul>
                            ${data.warnings.map(warning => `<li>${warning}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            resultsContainer.innerHTML = resultsHtml;
            resultsContainer.style.display = 'block';
        } else {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <h4><i class="fas fa-search"></i> No Specific Diagnosis Found</h4>
                    <p>Based on the symptoms provided, no specific medical condition was identified. Please consider:</p>
                    <ul>
                        <li>Providing more detailed symptom descriptions</li>
                        <li>Including duration and severity of symptoms</li>
                        <li>Consulting with a healthcare professional for proper diagnosis</li>
                    </ul>
                </div>
            `;
            resultsContainer.style.display = 'block';
        }

        // Show results section and scroll to results
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
        resultsContainer.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Error displaying results:', error);
        showError('Error displaying results. Please try again.');
    }
}

// Utility Functions
function getSeverityClass(severity) {
    const severityMap = {
        'low': 'severity-low',
        'moderate': 'severity-moderate',
        'high': 'severity-high',
        'critical': 'severity-critical'
    };
    return severityMap[severity?.toLowerCase()] || 'severity-unknown';
}

function getConfidenceClass(confidence) {
    if (confidence >= 80) return 'confidence-high';
    if (confidence >= 60) return 'confidence-medium';
    return 'confidence-low';
}

// Function to show detailed disease information in a modal
function showDiseaseDetails(diagnosisIndex) {
    try {
        console.log('showDiseaseDetails called with index:', diagnosisIndex);
        
        if (!currentDiagnoses || !currentDiagnoses[diagnosisIndex]) {
            console.error('Diagnosis not found at index:', diagnosisIndex);
            alert('Diagnosis information not found. Please try again.');
            return;
        }
        
        const diagnosis = currentDiagnoses[diagnosisIndex];
        console.log('Selected diagnosis:', diagnosis);
        
        // Remove any existing modal first
        const existingModal = document.getElementById('diseaseModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Create simple modal with inline styles
        const modalHtml = `
            <div id="diseaseModal" style="
                display: block; 
                position: fixed; 
                z-index: 9999; 
                left: 0; 
                top: 0; 
                width: 100%; 
                height: 100%; 
                background-color: rgba(0,0,0,0.5);
                overflow: auto;
            ">
                <div style="
                    background-color: white; 
                    margin: 5% auto; 
                    padding: 20px; 
                    border-radius: 8px; 
                    width: 90%; 
                    max-width: 600px; 
                    max-height: 80vh; 
                    overflow-y: auto;
                    position: relative;
                ">
                    <div style="
                        display: flex; 
                        justify-content: space-between; 
                        align-items: center; 
                        border-bottom: 1px solid #ddd; 
                        padding-bottom: 10px; 
                        margin-bottom: 20px;
                    ">
                        <h2 style="margin: 0; color: #333;">${diagnosis.condition}</h2>
                        <span onclick="closeDiseaseModal()" style="
                            font-size: 24px; 
                            cursor: pointer; 
                            color: #999;
                            font-weight: bold;
                        ">&times;</span>
                    </div>
                    
                    <div>
                        <div style="margin-bottom: 20px;">
                            <h3 style="color: #333; margin-bottom: 10px;">Description</h3>
                            <p style="color: #666; line-height: 1.6;">${diagnosis.description}</p>
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <h3 style="color: #333; margin-bottom: 10px;">Confidence & Severity</h3>
                            <p style="color: #666;"><strong>Confidence:</strong> ${diagnosis.confidence}% | <strong>Severity:</strong> ${diagnosis.severity}</p>
                        </div>
                        
                        ${diagnosis.immediate_actions ? `
                            <div style="margin-bottom: 20px;">
                                <h3 style="color: #333; margin-bottom: 10px;">Immediate Actions</h3>
                                <ul style="color: #666; padding-left: 20px;">
                                    ${diagnosis.immediate_actions.map(action => `<li style="margin-bottom: 5px;">${action}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${diagnosis.when_to_seek_help ? `
                            <div style="margin-bottom: 20px;">
                                <h3 style="color: #333; margin-bottom: 10px;">When to Seek Medical Help</h3>
                                <p style="color: #666; line-height: 1.6;">${diagnosis.when_to_seek_help}</p>
                            </div>
                        ` : ''}
                        
                        ${diagnosis.medicine_recommendations && (diagnosis.medicine_recommendations.otc_medicines || diagnosis.medicine_recommendations.natural_remedies || diagnosis.medicine_recommendations.prescription_medicines || diagnosis.medicine_recommendations.medical_literature) ? `
                            <div style="margin-bottom: 20px;">
                                <h3 style="color: #333; margin-bottom: 10px;">Medicine Recommendations</h3>
                                
                                ${diagnosis.medicine_recommendations.otc_medicines && diagnosis.medicine_recommendations.otc_medicines.length > 0 ? `
                                    <div style="margin-bottom: 15px;">
                                        <h4 style="color: #007bff; margin-bottom: 8px;">💊 Over-the-Counter Medications</h4>
                                        ${diagnosis.medicine_recommendations.otc_medicines.map(med => `
                                            <div style="
                                                background: #f8f9fa; 
                                                border: 1px solid #e9ecef; 
                                                border-radius: 6px; 
                                                padding: 15px; 
                                                margin: 10px 0;
                                            ">
                                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                                    <h5 style="margin: 0; color: #333;">${med.name || med.brand_name || 'Unknown'}</h5>
                                                    <span style="
                                                        background: ${med.source === 'FDA Database' ? '#28a745' : '#ffc107'}; 
                                                        color: white; 
                                                        padding: 2px 8px; 
                                                        border-radius: 12px; 
                                                        font-size: 12px; 
                                                        font-weight: bold;
                                                    ">${med.source || 'Local Database'}</span>
                                                </div>
                                                ${med.brand_name && med.brand_name !== med.name ? `<p style="margin: 5px 0; color: #666;"><strong>Brand:</strong> ${med.brand_name}</p>` : ''}
                                                ${med.dosage ? `<p style="margin: 5px 0; color: #666;"><strong>Dosage:</strong> ${med.dosage}</p>` : ''}
                                                ${med.warnings ? `<p style="margin: 5px 0; color: #dc3545;"><strong>⚠️ Warnings:</strong> ${med.warnings}</p>` : ''}
                                                ${med.side_effects ? `<p style="margin: 5px 0; color: #fd7e14;"><strong>💊 Side Effects:</strong> ${med.side_effects}</p>` : ''}
                                                ${med.indications ? `<p style="margin: 5px 0; color: #666;"><strong>Indications:</strong> ${med.indications}</p>` : ''}
                                            </div>
                                        `).join('')}
                                    </div>
                                ` : ''}
                                
                                ${diagnosis.medicine_recommendations.prescription_medicines && diagnosis.medicine_recommendations.prescription_medicines.length > 0 ? `
                                    <div style="margin-bottom: 15px;">
                                        <h4 style="color: #dc3545; margin-bottom: 8px;">💉 Prescription Medications</h4>
                                        ${diagnosis.medicine_recommendations.prescription_medicines.map(med => `
                                            <div style="
                                                background: #fff5f5; 
                                                border: 1px solid #feb2b2; 
                                                border-radius: 6px; 
                                                padding: 15px; 
                                                margin: 10px 0;
                                            ">
                                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                                    <h5 style="margin: 0; color: #333;">${med.name || med.brand_name || 'Unknown'}</h5>
                                                    <span style="
                                                        background: ${med.source === 'FDA Database' ? '#28a745' : '#ffc107'}; 
                                                        color: white; 
                                                        padding: 2px 8px; 
                                                        border-radius: 12px; 
                                                        font-size: 12px; 
                                                        font-weight: bold;
                                                    ">${med.source || 'Local Database'}</span>
                                                </div>
                                                ${med.brand_name && med.brand_name !== med.name ? `<p style="margin: 5px 0; color: #666;"><strong>Brand:</strong> ${med.brand_name}</p>` : ''}
                                                ${med.dosage ? `<p style="margin: 5px 0; color: #666;"><strong>Dosage:</strong> ${med.dosage}</p>` : ''}
                                                ${med.warnings ? `<p style="margin: 5px 0; color: #dc3545;"><strong>⚠️ Warnings:</strong> ${med.warnings}</p>` : ''}
                                                ${med.side_effects ? `<p style="margin: 5px 0; color: #fd7e14;"><strong>💊 Side Effects:</strong> ${med.side_effects}</p>` : ''}
                                                ${med.indications ? `<p style="margin: 5px 0; color: #666;"><strong>Indications:</strong> ${med.indications}</p>` : ''}
                                            </div>
                                        `).join('')}
                                    </div>
                                ` : ''}
                                
                                ${diagnosis.medicine_recommendations.natural_remedies && diagnosis.medicine_recommendations.natural_remedies.length > 0 ? `
                                    <div style="margin-bottom: 15px;">
                                        <h4 style="color: #28a745; margin-bottom: 8px;">🌿 Natural Remedies</h4>
                                        ${diagnosis.medicine_recommendations.natural_remedies.map(remedy => `
                                            <div style="
                                                background: #f0fff4; 
                                                border: 1px solid #9ae6b4; 
                                                border-radius: 6px; 
                                                padding: 15px; 
                                                margin: 10px 0;
                                            ">
                                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                                    <h5 style="margin: 0; color: #333;">${remedy.name || 'Natural Remedy'}</h5>
                                                    <span style="
                                                        background: ${remedy.source && remedy.source.includes('Research') ? '#28a745' : '#ffc107'}; 
                                                        color: white; 
                                                        padding: 2px 8px; 
                                                        border-radius: 12px; 
                                                        font-size: 12px; 
                                                        font-weight: bold;
                                                    ">${remedy.source || 'Local Database'}</span>
                                                </div>
                                                ${remedy.description ? `<p style="margin: 5px 0; color: #666;"><strong>Description:</strong> ${remedy.description}</p>` : ''}
                                                ${remedy.usage ? `<p style="margin: 5px 0; color: #28a745;"><strong>🌱 Usage:</strong> ${remedy.usage}</p>` : ''}
                                                ${remedy.effectiveness ? `<p style="margin: 5px 0; color: #17a2b8;"><strong>📊 Effectiveness:</strong> ${remedy.effectiveness}</p>` : ''}
                                            </div>
                                        `).join('')}
                                    </div>
                                ` : ''}
                                
                                ${diagnosis.medicine_recommendations.medical_literature && diagnosis.medicine_recommendations.medical_literature.length > 0 ? `
                                    <div style="margin-bottom: 15px;">
                                        <h4 style="color: #6f42c1; margin-bottom: 8px;">📚 Medical Literature</h4>
                                        ${diagnosis.medicine_recommendations.medical_literature.map(literature => `
                                            <div style="
                                                background: #f8f9ff; 
                                                border: 1px solid #c3dafe; 
                                                border-radius: 6px; 
                                                padding: 15px; 
                                                margin: 10px 0;
                                            ">
                                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                                    <h5 style="margin: 0; color: #333;">${literature.title || 'Research Article'}</h5>
                                                    <span style="
                                                        background: #6f42c1; 
                                                        color: white; 
                                                        padding: 2px 8px; 
                                                        border-radius: 12px; 
                                                        font-size: 12px; 
                                                        font-weight: bold;
                                                    ">PubMed</span>
                                                </div>
                                                ${literature.authors ? `<p style="margin: 5px 0; color: #666;"><strong>Authors:</strong> ${Array.isArray(literature.authors) ? literature.authors.map(author => author.name || author.authtype || 'Unknown Author').join(', ') : literature.authors}</p>` : ''}
                                                ${literature.abstract ? `<p style="margin: 5px 0; color: #666;"><strong>Abstract:</strong> ${literature.abstract}</p>` : ''}
                                                ${literature.pub_date ? `<p style="margin: 5px 0; color: #666;"><strong>Published:</strong> ${literature.pub_date}</p>` : ''}
                                            </div>
                                        `).join('')}
                                    </div>
                                ` : ''}
                                
                                ${diagnosis.medicine_recommendations.api_sources ? `
                                    <div style="
                                        background: #e3f2fd; 
                                        border: 1px solid #90caf9; 
                                        border-radius: 6px; 
                                        padding: 10px; 
                                        margin-top: 15px;
                                    ">
                                        <h5 style="margin: 0 0 8px 0; color: #1976d2;">📡 Data Sources</h5>
                                        <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                                            ${diagnosis.medicine_recommendations.api_sources.map(source => `
                                                <span style="
                                                    background: #1976d2; 
                                                    color: white; 
                                                    padding: 2px 8px; 
                                                    border-radius: 12px; 
                                                    font-size: 11px; 
                                                    font-weight: bold;
                                                ">${source}</span>
                                            `).join('')}
                                        </div>
                                        ${diagnosis.medicine_recommendations.last_updated ? `
                                            <p style="margin: 5px 0 0 0; color: #666; font-size: 12px;">
                                                <strong>Last Updated:</strong> ${new Date(diagnosis.medicine_recommendations.last_updated).toLocaleString()}
                                            </p>
                                        ` : ''}
                                    </div>
                                ` : ''}
                            </div>
                        ` : '<p style="color: #666;"><strong>No medicine recommendations available for this condition.</strong></p>'}
                        
                        <div style="
                            border-top: 1px solid #ddd; 
                            padding-top: 15px; 
                            margin-top: 20px;
                            text-align: center;
                        ">
                            <p style="color: #666; font-size: 14px; margin-bottom: 15px;"><strong>⚠️ Important:</strong> This information is for educational purposes only. Always consult with a healthcare professional before taking any medication.</p>
                            <button onclick="closeDiseaseModal()" style="
                                background: #007bff; 
                                color: white; 
                                border: none; 
                                padding: 10px 20px; 
                                border-radius: 5px; 
                                cursor: pointer;
                                font-size: 16px;
                            ">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Close modal when clicking outside
        const modal = document.getElementById('diseaseModal');
        if (modal) {
            modal.onclick = function(event) {
                if (event.target === modal) {
                    closeDiseaseModal();
                }
            };
            
            console.log('Modal created and displayed successfully');
        } else {
            console.error('Modal element not found after creation');
        }
        
    } catch (error) {
        console.error('Error in showDiseaseDetails:', error);
        alert('Error displaying disease details. Please try again.');
    }
}

// Function to close disease modal
function closeDiseaseModal() {
    const modal = document.getElementById('diseaseModal');
    if (modal) {
        modal.remove();
    }
}

// ===== CHATBOT FUNCTIONS =====

// Switch between symptoms analysis and chatbot modes
function switchMode(mode) {
    currentMode = mode;
    
    // Update mode buttons
    const symptomsBtn = document.getElementById('symptomsModeBtn');
    const chatbotBtn = document.getElementById('chatbotModeBtn');
    
    if (symptomsBtn && chatbotBtn) {
        symptomsBtn.classList.remove('active');
        chatbotBtn.classList.remove('active');
        
        if (mode === 'symptoms') {
            symptomsBtn.classList.add('active');
        } else {
            chatbotBtn.classList.add('active');
        }
    }
    
    // Show/hide interfaces
    const symptomsInterface = document.getElementById('symptomsInterface');
    const chatbotInterface = document.getElementById('chatbotInterface');
    
    if (symptomsInterface && chatbotInterface) {
        if (mode === 'symptoms') {
            symptomsInterface.style.display = 'block';
            chatbotInterface.style.display = 'none';
        } else {
            symptomsInterface.style.display = 'none';
            chatbotInterface.style.display = 'block';
            initializeChatbot();
        }
    }
}

// Initialize chatbot
function initializeChatbot() {
    if (!chatSessionId) {
        chatSessionId = Date.now().toString();
    }
    
    // Clear previous messages
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.innerHTML = '';
    }
    
    // Add welcome message
    addChatMessage('doctor', 'Hello! I\'m Dr. AI, your virtual medical assistant. How can I help you today? Feel free to describe your symptoms or ask any health-related questions.');
    
    // Setup chatbot event listeners
    setupChatbotEventListeners();
}

// Setup chatbot event listeners
function setupChatbotEventListeners() {
    // Send button
    const sendBtn = document.getElementById('sendChatBtn');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendChatMessage);
    }
    
    // Enter key in chat input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
    
    // Voice chat button
    const voiceChatBtn = document.getElementById('voiceChatBtn');
    if (voiceChatBtn) {
        voiceChatBtn.addEventListener('click', startVoiceChat);
    }
    
    // Image upload button
    const imageUploadBtn = document.getElementById('imageUploadBtn');
    if (imageUploadBtn) {
        imageUploadBtn.addEventListener('click', function() {
            document.getElementById('imageFileInput').click();
        });
    }
    
    // File input change
    const imageFileInput = document.getElementById('imageFileInput');
    if (imageFileInput) {
        imageFileInput.addEventListener('change', handleImageSelection);
    }
    
    // Remove image button
    const removeImageBtn = document.getElementById('removeImageBtn');
    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', removeSelectedImage);
    }
    
    // Analyze image button
    const analyzeImageBtn = document.getElementById('analyzeImageBtn');
    if (analyzeImageBtn) {
        analyzeImageBtn.addEventListener('click', analyzeSelectedImage);
    }
}

// Send chat message
async function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage('user', message);
    chatInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch('/chat_with_doctor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: chatSessionId
            })
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        if (data.success) {
            // Add doctor response to chat
            addChatMessage('doctor', data.response);
            
            // Update session ID if provided
            if (data.session_id) {
                chatSessionId = data.session_id;
            }
            
            // Log language detection if available
            if (data.detected_language) {
                console.log(`🌍 Language detected: ${data.detected_language}`);
                updateLanguageIndicator(data.detected_language);
            }
        } else {
            // Add error message to chat
            addChatMessage('doctor', data.response || 'I apologize, but I\'m having trouble processing your request. Please try again.');
        }
        
    } catch (error) {
        console.error('Chat error:', error);
        hideTypingIndicator();
        addChatMessage('doctor', 'I apologize, but I\'m experiencing technical difficulties. Please try again later.');
    }
}

// Add message to chat
function addChatMessage(sender, message) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${sender}`;
    avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-user-md"></i>';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = message;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString();
    
    bubble.appendChild(time);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message doctor typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar doctor';
    avatar.innerHTML = '<i class="fas fa-user-md"></i>';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(bubble);
    chatMessages.appendChild(typingDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Start voice chat
function startVoiceChat() {
    if (!recognition) {
        showNotification('Voice recognition not available in this browser', 'error');
        return;
    }
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.value = transcript;
        }
        showNotification('Voice input received: ' + transcript, 'success');
    };
    
    recognition.start();
    showNotification('Voice chat activated - speak now', 'info');
}

// Image handling functions
function handleImageSelection(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showNotification('Please select a valid image file (JPEG, PNG, BMP, TIFF, or WebP)', 'error');
        return;
    }
    
    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showNotification('Image file is too large. Please select an image smaller than 10MB', 'error');
        return;
    }
    
    selectedImageFile = file;
    displayImagePreview(file);
    showNotification('Image selected successfully', 'success');
}

function displayImagePreview(file) {
    const preview = document.getElementById('imagePreview');
    const previewImage = document.getElementById('previewImage');
    
    if (!preview || !previewImage) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImage.src = e.target.result;
        preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function removeSelectedImage() {
    selectedImageFile = null;
    const preview = document.getElementById('imagePreview');
    const fileInput = document.getElementById('imageFileInput');
    
    if (preview) {
        preview.style.display = 'none';
    }
    if (fileInput) {
        fileInput.value = '';
    }
    
    showNotification('Image removed', 'info');
}

async function analyzeSelectedImage() {
    if (!selectedImageFile) {
        showNotification('Please select an image first', 'error');
        return;
    }
    
    const description = document.getElementById('imageDescription')?.value || '';
    
    // Show loading state
    const analyzeBtn = document.getElementById('analyzeImageBtn');
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing Image...';
    }
    
    // Show typing indicator in chat
    showTypingIndicator();
    
    try {
        const formData = new FormData();
        formData.append('image', selectedImageFile);
        formData.append('description', description);
        formData.append('session_id', chatSessionId || '');
        
        const response = await fetch('/analyze_image', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        if (data.success) {
            // Create user message based on what they uploaded
            let userMessage = '[Image Upload]';
            if (description.trim()) {
                userMessage += ` ${description}`;
            } else {
                userMessage += ' Medical image uploaded for analysis';
            }
            
            // Add image upload message to chat
            addChatMessage('user', userMessage);
            
            // Add analysis response to chat
            addChatMessage('doctor', data.chat_response);
            
            // Update session ID if provided
            if (data.session_id) {
                chatSessionId = data.session_id;
            }
            
            // Log language detection if available
            if (data.detected_language) {
                console.log(`🌍 Language detected for image analysis: ${data.detected_language}`);
                updateLanguageIndicator(data.detected_language);
            }
            
            // Clear the image selection
            removeSelectedImage();
            
            showNotification('Image analysis completed successfully!', 'success');
        } else {
            addChatMessage('doctor', `Image analysis failed: ${data.error || 'Unknown error'}`);
            showNotification('Image analysis failed', 'error');
        }
        
    } catch (error) {
        console.error('Image analysis error:', error);
        hideTypingIndicator();
        addChatMessage('doctor', 'I apologize, but I\'m having trouble analyzing the image. Please try again or describe your symptoms in text.');
        showNotification('Image analysis failed', 'error');
    } finally {
        // Reset button state
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Image & Answer Query';
        }
    }
} 

       function updateLanguageIndicator(language) {
           const languageIndicator = document.getElementById('languageIndicator');
           const detectedLanguageSpan = document.getElementById('detectedLanguage');

           if (languageIndicator && detectedLanguageSpan) {
               // Enhanced language name mapping for Indian languages
               const languageNames = {
                   'en': 'English',
                   'es': 'Spanish',
                   'fr': 'French',
                   'de': 'German',
                   'hi': 'Hindi',
                   'bn': 'Bengali',
                   'te': 'Telugu',
                   'ta': 'Tamil',
                   'mr': 'Marathi',
                   'gu': 'Gujarati',
                   'kn': 'Kannada',
                   'ml': 'Malayalam',
                   'pa': 'Punjabi',
                   'ur': 'Urdu',
                   'zh': 'Chinese',
                   'ja': 'Japanese',
                   'ar': 'Arabic',
                   'pt': 'Portuguese',
                   'ru': 'Russian'
               };

               const languageName = languageNames[language] || language.toUpperCase();
               detectedLanguageSpan.textContent = languageName;
               languageIndicator.style.display = 'flex';

               // Hide indicator after 5 seconds
               setTimeout(() => {
                   languageIndicator.style.display = 'none';
               }, 5000);
           }
       } 