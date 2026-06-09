/* ===== ShifaBot Chatbot Interface ===== */

let conversationHistory = [];
let isReadyForDiagnosis = false;

// Auto-resize textarea
const chatInput = document.getElementById('chatInput');
if (chatInput) {
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function addMessage(content, isUser) {
    const messagesDiv = document.getElementById('chatMessages');
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'} fade-in`;
    messageDiv.innerHTML = `
        <div class="bubble">${content}</div>
        <span class="timestamp">${timeStr}</span>
    `;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showTyping() {
    const indicator = document.getElementById('typingIndicator');
    indicator.style.display = 'block';
    const messagesDiv = document.getElementById('chatMessages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function hideTyping() {
    document.getElementById('typingIndicator').style.display = 'none';
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, true);
    conversationHistory.push({ role: 'user', content: message });

    // Clear input
    input.value = '';
    input.style.height = 'auto';

    // Disable send
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;

    // Show typing indicator
    showTyping();

    try {
        const { data } = await apiCall('/api/diagnosis/chat', 'POST', {
            message: message,
            history: conversationHistory.slice(0, -1) // Send history without current message
        });

        hideTyping();

        if (data.success) {
            addMessage(data.reply, false);
            conversationHistory.push({ role: 'assistant', content: data.reply });

            // Check if ready for diagnosis
            if (data.ready_for_diagnosis) {
                isReadyForDiagnosis = true;
                document.getElementById('finalizeSection').style.display = 'block';
            }
        } else {
            addMessage("I'm sorry, I encountered an issue. Please try again.", false);
        }
    } catch (err) {
        hideTyping();
        addMessage("I'm sorry, I couldn't connect. Please check your internet connection and try again.", false);
    }

    sendBtn.disabled = false;
    input.focus();
}

async function finalizeDiagnosis() {
    const btn = document.getElementById('finalizeBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating diagnosis...';

    showSpinner('Generating your complete AI diagnosis...');

    try {
        const { data } = await apiCall('/api/diagnosis/chat/finalize', 'POST', {
            history: conversationHistory
        });

        hideSpinner();

        if (data.success) {
            const consultationId = data.consultation_id;
            const analysis = data.result;

            // Build a rich summary message with recommendations
            let summaryHTML = `<strong>Diagnosis Complete!</strong><br><br>`;

            // Possible conditions
            if (analysis.possible_conditions && analysis.possible_conditions.length > 0) {
                summaryHTML += `<strong>Possible Conditions:</strong><ul>`;
                analysis.possible_conditions.forEach(c => { summaryHTML += `<li>${c}</li>`; });
                summaryHTML += `</ul>`;
            }

            // Medication recommendations
            const meds = analysis.medication_recommendations;
            if (meds && (Array.isArray(meds) ? meds.length > 0 : meds)) {
                summaryHTML += `<strong>Medication Recommendations:</strong><ul>`;
                const medItems = Array.isArray(meds) ? meds : [meds];
                medItems.forEach(m => { summaryHTML += `<li>${m}</li>`; });
                summaryHTML += `</ul>`;
            }

            // Food recommendations
            const foods = analysis.food_recommendations;
            if (foods && (Array.isArray(foods) ? foods.length > 0 : foods)) {
                summaryHTML += `<strong>Food & Diet Recommendations:</strong><ul>`;
                const foodItems = Array.isArray(foods) ? foods : [foods];
                foodItems.forEach(f => { summaryHTML += `<li>${f}</li>`; });
                summaryHTML += `</ul>`;
            }

            // Disclaimer
            if (analysis.disclaimer) {
                summaryHTML += `<br><em style="font-size:0.85rem; color: #856404;">${analysis.disclaimer}</em>`;
            }

            // Report link
            summaryHTML += `<br><br><a href="/reports/${consultationId}" target="_blank" class="text-primary fw-bold">` +
                `<i class="bi bi-file-earmark-medical me-1"></i>View Full Report & Download PDF</a>`;

            addMessage(summaryHTML, false);
            showToast('Diagnosis report generated successfully!');
        } else {
            addMessage("I wasn't able to generate a full diagnosis. Please make sure you've described your symptoms, age, and gender clearly.", false);
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-clipboard2-check me-2"></i>Generate Full Diagnosis Report';
        }
    } catch (err) {
        hideSpinner();
        showToast('An error occurred. Please try again.', true);
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-clipboard2-check me-2"></i>Generate Full Diagnosis Report';
    }
}

function resetChat() {
    if (!confirm('Are you sure you want to reset this conversation?')) return;

    conversationHistory = [];
    isReadyForDiagnosis = false;

    const messagesDiv = document.getElementById('chatMessages');
    messagesDiv.innerHTML = `
        <div class="message bot fade-in">
            <div class="bubble">
                Hello! I'm <strong>ShifaBot</strong>, your AI medical assistant. I'm here to help you understand your symptoms and provide health recommendations.<br><br>
                To get started, please tell me: <strong>What symptoms are you experiencing?</strong>
            </div>
            <span class="timestamp">Just now</span>
        </div>
    `;

    document.getElementById('finalizeSection').style.display = 'none';
    const btn = document.getElementById('finalizeBtn');
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-clipboard2-check me-2"></i>Generate Full Diagnosis Report';
}
