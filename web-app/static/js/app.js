/**
 * Product Discovery Manager + Solution Architect - Frontend
 * Handles chat UI, session management, skill switching, and API communication.
 */

// ── State ──────────────────────────────────────────────────────────────────

let currentSessionId = null;
let isLoading = false;
let sessions = [];
let currentSkill = "discovery"; // "discovery" | "solution"

const PHASES_DISCOVERY = [
    { id: 1, name: "Problem Elicitation", desc: "Validate the problem statement" },
    { id: 2, name: "JTBD Analysis", desc: "Identify core and related jobs" },
    { id: 3, name: "Competitive Landscape", desc: "Map solutions and gaps" },
    { id: 4, name: "Success Metrics", desc: "Define measurable outcomes" },
    { id: 5, name: "User Journey Mapping", desc: "Visualize the experience" },
];

const PHASES_SOLUTION = [
    { id: 1, name: "Discovery Input", desc: "Retrieve and synthesize discovery findings" },
    { id: 2, name: "Barrier Analysis", desc: "Identify what prevents job completion" },
    { id: 3, name: "Opportunity Exploration", desc: "Explore low-tech solutions first" },
    { id: 4, name: "Opportunity Solution Tree", desc: "Visualize barriers and opportunities" },
    { id: 5, name: "T-Shirt Sizing", desc: "Estimate relative effort" },
    { id: 6, name: "RICE Prioritization", desc: "Score by Reach, Impact, Confidence, Effort" },
    { id: 7, name: "Solution Recommendation", desc: "Recommend next easiest high-impact step" },
    { id: 8, name: "Validation Plan", desc: "Define how to test with real users" },
];

const SKILL_CONFIG = {
    discovery: {
        phases: PHASES_DISCOVERY,
        logo: "🔍",
        title: "Product Discovery Manager",
        subtitle: "Structured customer discovery powered by JTBD",
        sidebarTitle: "Discovery Phases",
        landingIcon: "🎯",
        landingHeading: "What problem are you trying to solve?",
        landingDesc: "Describe your customer problem or product idea. The Product Discovery Manager will guide you through a structured discovery process.",
        startBtnText: "Start Discovery",
        senderName: "Product Discovery Manager",
        welcomeMsg: `<p>Hello! I'm your Product Discovery Manager. I'll guide you through a structured discovery process grounded in Cagan's product model principles and the Jobs-to-be-Done framework.</p><p>Let's start by understanding your problem. Please describe the customer problem or need you're exploring, and I'll begin Phase 1: Problem Elicitation.</p>`,
        saveEndpoint: "/api/save-discovery",
        listEndpoint: "/api/discoveries",
        reportEndpointPrefix: "/api/generate-report",
        reportUrlPrefix: "/Discovery/discoveries",
        browseTitle: "📂 Discovery Reports",
        emptyMsg: "No discoveries yet. Start a discovery session and save it!",
        hint: "Kimi triggers the product-discovery-manager skill automatically",
    },
    solution: {
        phases: PHASES_SOLUTION,
        logo: "🛠️",
        title: "Solution Architect",
        subtitle: "Low-friction solutions for non-tech-savvy users",
        sidebarTitle: "Solution Phases",
        landingIcon: "💡",
        landingHeading: "What discovery output are we solutioning for?",
        landingDesc: "Paste your discovery summary or describe the problem space. The Solution Architect will find the quickest, lowest-friction path to validate a solution — starting from free tools and no-code before proposing custom builds.",
        startBtnText: "Start Solutioning",
        senderName: "Solution Architect",
        welcomeMsg: `<p>Hello! I'm your Solution Architect. I'll help you find the quickest, easiest way to solve the problems identified in your discovery — starting from process fixes and free tools, through no/low-code platforms, before ever proposing a custom build.</p><p>Share your discovery summary or describe the problem, and I'll begin Phase 1: Discovery Input.</p>`,
        saveEndpoint: "/api/save-solution",
        listEndpoint: "/api/solutions",
        reportEndpointPrefix: "/api/generate-solution-report",
        reportUrlPrefix: "/Solutions/solutions",
        browseTitle: "📂 Solution Reports",
        emptyMsg: "No solutions yet. Start a solution session and save it!",
        hint: "Kimi triggers the solution-architect skill automatically based on your messages",
    },
};

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
const skillSelect = document.getElementById('skill-select');
const currentPhaseBadge = document.getElementById('current-phase-badge');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toast-message');
const saveBtn = document.getElementById('save-btn');
const generateReportBtn = document.getElementById('generate-report-btn');
const browseBtn = document.getElementById('browse-btn');
const browseModal = document.getElementById('browse-modal');
const closeModalBtn = document.getElementById('close-modal');
const browseList = document.getElementById('browse-list');

// Dynamic UI elements
const headerLogo = document.getElementById('header-logo');
const headerTitle = document.getElementById('header-title');
const headerSubtitle = document.getElementById('header-subtitle');
const sidebarTitle = document.getElementById('sidebar-title');
const phasesList = document.getElementById('phases-list');
const sidebarHint = document.getElementById('sidebar-hint');
const landingIcon = document.getElementById('landing-icon');
const landingHeading = document.getElementById('landing-heading');
const landingDesc = document.getElementById('landing-desc');
const startBtnText = document.getElementById('start-btn-text');
const welcomeSender = document.getElementById('welcome-sender');
const welcomeText = document.getElementById('welcome-text');
const browseModalTitle = document.getElementById('browse-modal-title');

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

function getCurrentPhases() {
    return SKILL_CONFIG[currentSkill].phases;
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

function renderPhases() {
    const phases = getCurrentPhases();
    phasesList.innerHTML = phases.map((phase, index) => `
        <div class="phase-item ${index === 0 ? 'active' : ''}" data-phase="${phase.id}">
            <div class="phase-number">${phase.id}</div>
            <div class="phase-info">
                <div class="phase-name">${phase.name}</div>
                <div class="phase-desc">${phase.desc}</div>
            </div>
        </div>
    `).join('');
}

function applySkillUI() {
    const cfg = SKILL_CONFIG[currentSkill];

    // Header
    headerLogo.textContent = cfg.logo;
    headerTitle.textContent = cfg.title;
    headerSubtitle.textContent = cfg.subtitle;

    // Sidebar
    sidebarTitle.textContent = cfg.sidebarTitle;
    sidebarHint.innerHTML = `Kimi triggers the <code>${currentSkill === 'discovery' ? 'product-discovery-manager' : 'solution-architect'}</code> skill automatically`;
    renderPhases();

    // Landing
    landingIcon.textContent = cfg.landingIcon;
    landingHeading.textContent = cfg.landingHeading;
    landingDesc.textContent = cfg.landingDesc;
    startBtnText.textContent = cfg.startBtnText;

    // Welcome message
    welcomeSender.textContent = cfg.senderName;
    welcomeText.innerHTML = cfg.welcomeMsg;

    // Browse modal
    browseModalTitle.textContent = cfg.browseTitle;
}

function switchSkill(skill) {
    currentSkill = skill;
    skillSelect.value = skill;
    applySkillUI();
    showLandingInterface();
    loadSessions();
}

function addMessage(role, content, phase = 1) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.dataset.phase = phase;

    const avatar = role === 'user' ? '🧑' : '🤖';
    const sender = role === 'user' ? 'You' : SKILL_CONFIG[currentSkill].senderName;
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
    saveBtn.disabled = false;
    generateReportBtn.disabled = false;
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

    // Reset chat messages to welcome only
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-sender">${SKILL_CONFIG[currentSkill].senderName}</div>
                <div class="message-text">${SKILL_CONFIG[currentSkill].welcomeMsg}</div>
            </div>
        </div>
    `;
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
            body: JSON.stringify({ message, session_id: currentSessionId, skill: currentSkill }),
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
            // Only show sessions for current skill
            if (session.skill !== currentSkill) return;
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

        // If session skill differs from current, switch
        if (session.skill && session.skill !== currentSkill) {
            switchSkill(session.skill);
        }

        // Clear and rebuild chat
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <div class="message-sender">${SKILL_CONFIG[currentSkill].senderName}</div>
                    <div class="message-text">
                        <p>Resuming session <strong>${session.id}</strong>. Current phase: <strong>${getCurrentPhases().find(p => p.id === session.current_phase)?.name || 'Unknown'}</strong>.</p>
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

async function saveOutput() {
    if (!currentSessionId) return;

    const cfg = SKILL_CONFIG[currentSkill];
    const session = sessions.find(s => s.id === currentSessionId);
    let problemName = currentSkill === 'discovery' ? 'untitled-discovery' : 'untitled-solution';
    if (session) {
        const firstUserMsg = session.messages?.find(m => m.role === 'user');
        if (firstUserMsg) {
            problemName = firstUserMsg.content.slice(0, 50).replace(/[^\w\s]/g, '');
        }
    }

    try {
        saveBtn.disabled = true;
        saveBtn.textContent = '💾 Saving...';

        const response = await fetch(cfg.saveEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId, problem_name: problemName }),
        });

        const data = await response.json();
        if (data.error) {
            showToast(`Error: ${data.error}`);
        } else {
            showToast(`${currentSkill === 'discovery' ? 'Discovery' : 'Solution'} saved: ${data.folder}`);
        }
    } catch (err) {
        showToast(`Failed to save: ${err.message}`);
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = '💾 Save';
    }
}

async function generateReport() {
    if (!currentSessionId) return;

    const cfg = SKILL_CONFIG[currentSkill];

    // First save
    await saveOutput();

    // Get the most recent folder
    try {
        generateReportBtn.disabled = true;
        generateReportBtn.textContent = '📄 Generating...';

        const outputs = await fetch(cfg.listEndpoint).then(r => r.json());
        if (!outputs.length) {
            showToast('No saved outputs found to generate report');
            return;
        }

        const latest = outputs[0];
        const response = await fetch(`${cfg.reportEndpointPrefix}/${latest.name}`, {
            method: 'POST',
        });

        const data = await response.json();
        if (data.error) {
            showToast(`Error: ${data.error}`);
        } else {
            showToast('Report generated! Opening...');
            window.open(data.report_url, '_blank');
        }
    } catch (err) {
        showToast(`Failed to generate report: ${err.message}`);
    } finally {
        generateReportBtn.disabled = false;
        generateReportBtn.textContent = '📄 Report';
    }
}

async function loadOutputs() {
    const cfg = SKILL_CONFIG[currentSkill];
    try {
        const response = await fetch(cfg.listEndpoint);
        const data = await response.json();

        if (!data.length) {
            browseList.innerHTML = `<p class="empty-state">${cfg.emptyMsg}</p>`;
            return;
        }

        browseList.innerHTML = data.map(d => `
            <div class="discovery-item" data-folder="${d.name}">
                <div class="discovery-info">
                    <div class="discovery-name">${d.problem_name}</div>
                    <div class="discovery-meta">${d.formatted_date} · ${d.md_files} files ${d.has_report ? '· ✅ Report' : ''}</div>
                </div>
                <div class="discovery-actions">
                    ${d.has_report ? `<a href="${cfg.reportUrlPrefix}/${d.name}/index.html" target="_blank" class="btn btn-primary">View</a>` : ''}
                    <button class="btn btn-secondary btn-generate" data-folder="${d.name}">Generate</button>
                </div>
            </div>
        `).join('');

        // Add event listeners to generate buttons
        browseList.querySelectorAll('.btn-generate').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const folder = btn.dataset.folder;
                btn.textContent = '...';
                btn.disabled = true;
                try {
                    const res = await fetch(`${cfg.reportEndpointPrefix}/${folder}`, { method: 'POST' });
                    const result = await res.json();
                    if (result.success) {
                        showToast('Report generated!');
                        loadOutputs();
                        window.open(result.report_url, '_blank');
                    } else {
                        showToast(`Error: ${result.error}`);
                    }
                } catch (err) {
                    showToast(`Failed: ${err.message}`);
                }
            });
        });
    } catch (err) {
        console.error('Failed to load outputs:', err);
        browseList.innerHTML = '<p class="empty-state">Failed to load saved outputs</p>';
    }
}

function openBrowseModal() {
    browseModal.classList.remove('hidden');
    loadOutputs();
}

function closeBrowseModal() {
    browseModal.classList.add('hidden');
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

saveBtn.addEventListener('click', saveOutput);

generateReportBtn.addEventListener('click', generateReport);

browseBtn.addEventListener('click', openBrowseModal);

closeModalBtn.addEventListener('click', closeBrowseModal);

browseModal.querySelector('.modal-overlay').addEventListener('click', closeBrowseModal);

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

skillSelect.addEventListener('change', () => {
    switchSkill(skillSelect.value);
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
    applySkillUI();
    await loadSessions();
    problemInput.focus();
    console.log('Product Discovery Manager + Solution Architect loaded');
}

init();
