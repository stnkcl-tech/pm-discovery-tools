/**
 * Product Discovery Manager - Frontend
 * Handles chat UI, session management, and API communication with Flask backend.
 */

// ── State ──────────────────────────────────────────────────────────────────

let currentSessionId = null;
let isLoading = false;
let sessions = [];

const PHASES = [
    { id: 1, name: "Problem Elicitation" },
    { id: 2, name: "JTBD Analysis" },
    { id: 3, name: "Competitive Landscape" },
    { id: 4, name: "Success Metrics" },
    { id: 5, name: "User Journey Mapping" },
];

// ── DOM Elements ───────────────────────────────────────────────────────────

const landingState = document.getElementById('landing-state');
const chatMessages = document.getElementById('chat-messages');
const chatInputArea = document.getElementById('chat-input-area');
const loadingIndicator = document.getElementById('loading-indicator');
const problemInput = document.getElementById('problem-input');
const chatInput = document.getElementById('chat-input');
const startBtn = document.getElementById('start-btn');
const sendBtn = document.getElementById('send-btn');
const exportBtn = document.getElementById('export-btn');
const clearBtn = document.getElementById('clear-btn');
const sessionSelect = document.getElementById('session-select');
const currentPhaseBadge = document.getElementById('current-phase-badge');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toast-message');

// ── Helpers ────────────────────────────────────────────────────────────────

function showToast(message, duration = 3000) {
    toastMessage.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), duration);
}

function setLoading(loading) {
    isLoading = loading;
    if (loading) {
        loadingIndicator.classList.remove('hidden');
        sendBtn.disabled = true;
        startBtn.disabled = true;
    } else {
        loadingIndicator.classList.add('hidden');
        sendBtn.disabled = false;
        startBtn.disabled = false;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Simple Markdown to HTML converter
function markdownToHtml(markdown) {
    let html = escapeHtml(markdown);

    // Code blocks
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Blockquote
    html = html.replace(/^&gt; (.*$)/gim, '<blockquote>$1</blockquote>');

    // Horizontal rule
    html = html.replace(/^---$/gim, '<hr>');

    // Tables (simple parser)
    const tableRegex = /((?:\|[^\n]*\|\n?)+)/g;
    html = html.replace(tableRegex, (match) => {
        const rows = match.trim().split('\n').filter(r => r.trim());
        if (rows.length < 2) return match;
        let tableHtml = '<table>';
        rows.forEach((row, i) => {
            const cells = row.split('|').filter(c => c.trim() !== '');
            if (cells.length === 0) return;
            // Skip separator rows (|---|...)
            if (cells.every(c => c.trim().replace(/-/g, '') === '')) return;
            const tag = i === 0 ? 'th' : 'td';
            tableHtml += '<tr>' + cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>';
        });
        tableHtml += '</table>';
        return tableHtml;
    });

    // Lists
    html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');

    // Wrap consecutive li elements in ul
    html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
        return '<ul>' + match + '</ul>';
    });

    // Paragraphs
    html = html.replace(/\n\n/g, '</p><p>');
    html = '<p>' + html + '</p>';

    // Clean up empty paragraphs
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<(?:h[1-6]|ul|ol|pre|blockquote|hr|table)[^>]*>)/g, '$1');
    html = html.replace(/(<\/(?:h[1-6]|ul|ol|pre|blockquote|hr|table)>)<\/p>/g, '$1');

    return html;
}

function updatePhaseTracker(phaseId) {
    currentPhaseBadge.textContent = `Phase ${phaseId}`;

    document.querySelectorAll('.phase-item').forEach(item => {
        const itemPhase = parseInt(item.dataset.phase);
        item.classList.remove('active', 'completed');

        if (itemPhase === phaseId) {
            item.classList.add('active');
        } else if (itemPhase < phaseId) {
            item.classList.add('completed');
        }
    });
}

function addMessage(role, content, phase = 1) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.dataset.phase = phase;

    const avatar = role === 'user' ? '🧑' : '🤖';
    const sender = role === 'user' ? 'You' : 'Product Discovery Manager';
    const htmlContent = markdownToHtml(content);

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-sender">${sender}</div>
            <div class="message-text">${htmlContent}</div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showChatInterface() {
    landingState.classList.add('hidden');
    chatMessages.classList.remove('hidden');
    chatInputArea.classList.remove('hidden');
    exportBtn.disabled = false;
}

function showLandingInterface() {
    landingState.classList.remove('hidden');
    chatMessages.classList.add('hidden');
    chatInputArea.classList.add('hidden');
    exportBtn.disabled = true;
    problemInput.value = '';
    chatInput.value = '';
    currentSessionId = null;
    updatePhaseTracker(1);
}

// ── API Communication ──────────────────────────────────────────────────────

async function sendMessage(message) {
    if (!message.trim() || isLoading) return;

    setLoading(true);
    addMessage('user', message);
    chatInput.value = '';
    chatInput.style.height = 'auto';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: currentSessionId }),
        });

        const data = await response.json();

        if (data.error) {
            addMessage('assistant', `**Error:** ${data.error}`);
        } else {
            currentSessionId = data.session_id;
            addMessage('assistant', data.response, data.current_phase);
            updatePhaseTracker(data.current_phase);
            await loadSessions();
        }
    } catch (err) {
        addMessage('assistant', `**Connection Error:** ${err.message}\n\nPlease make sure the Flask server is running (\`python3 app.py\`).`);
    } finally {
        setLoading(false);
        chatInput.focus();
    }
}

async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        sessions = data;

        // Rebuild session dropdown
        const currentVal = sessionSelect.value;
        sessionSelect.innerHTML = '<option value="">New Session</option>';

        data.forEach(session => {
            const option = document.createElement('option');
            option.value = session.id;
            const date = new Date(session.created_at).toLocaleString();
            option.textContent = `Session ${session.id} — ${session.phase_name} (${session.message_count} msgs)`;
            if (session.id === currentVal) option.selected = true;
            sessionSelect.appendChild(option);
        });
    } catch (err) {
        console.error('Failed to load sessions:', err);
    }
}

async function loadSession(sessionId) {
    if (!sessionId) return;

    try {
        const response = await fetch(`/api/session/${sessionId}`);
        const session = await response.json();

        if (session.error) {
            showToast(session.error);
            return;
        }

        // Clear and rebuild chat
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-sender">Product Discovery Manager</div>
                    <div class="message-text">
                        <p>Resuming session <strong>${session.id}</strong>. Current phase: <strong>${PHASES.find(p => p.id === session.current_phase)?.name || 'Unknown'}</strong>.</p>
                    </div>
                </div>
            </div>
        `;

        session.messages.forEach(msg => {
            addMessage(msg.role, msg.content, msg.phase);
        });

        currentSessionId = session.id;
        updatePhaseTracker(session.current_phase);
        showChatInterface();
    } catch (err) {
        showToast(`Failed to load session: ${err.message}`);
    }
}

async function exportSession() {
    if (!currentSessionId) return;
    window.open(`/api/export/${currentSessionId}`, '_blank');
}

async function deleteSession(sessionId) {
    if (!sessionId) return;
    try {
        const response = await fetch(`/api/delete/${sessionId}`, { method: 'DELETE' });
        const data = await response.json();
        if (data.success) {
            showToast('Session deleted');
            await loadSessions();
            if (currentSessionId === sessionId) {
                showLandingInterface();
            }
        }
    } catch (err) {
        showToast(`Failed to delete: ${err.message}`);
    }
}

// ── Event Listeners ────────────────────────────────────────────────────────

startBtn.addEventListener('click', () => {
    const problem = problemInput.value.trim();
    if (!problem) {
        showToast('Please describe your problem first');
        problemInput.focus();
        return;
    }

    showChatInterface();
    sendMessage(problem);
});

sendBtn.addEventListener('click', () => {
    sendMessage(chatInput.value);
});

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(chatInput.value);
    }
});

chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + 'px';
});

problemInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        startBtn.click();
    }
});

exportBtn.addEventListener('click', exportSession);

clearBtn.addEventListener('click', () => {
    if (currentSessionId && confirm('Delete this session?')) {
        deleteSession(currentSessionId);
    } else if (!currentSessionId) {
        showLandingInterface();
    }
});

sessionSelect.addEventListener('change', () => {
    const sessionId = sessionSelect.value;
    if (sessionId) {
        loadSession(sessionId);
    } else {
        showLandingInterface();
    }
});

// Example chips
document.querySelectorAll('.example-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        problemInput.value = chip.dataset.example;
        problemInput.focus();
    });
});

// ── Init ───────────────────────────────────────────────────────────────────

async function init() {
    await loadSessions();
    problemInput.focus();
    console.log('Product Discovery Manager loaded');
}

init();
