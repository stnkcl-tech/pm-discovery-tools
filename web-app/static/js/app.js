/**
 * Product Discovery Manager + Solution Architect - Frontend
 * Clean, minimal interface with journey sidebar and step header.
 */

// ── State ──────────────────────────────────────────────────────────────────

let currentSessionId = null;
let isLoading = false;
let sessions = [];
let currentSkill = "discovery";
let currentCheckpoint = 1;

const PHASES_DISCOVERY = [
    { id: 1, name: "Problem Elicitation", desc: "Understand the core problem" },
    { id: 2, name: "JTBD Analysis", desc: "Identify jobs to be done" },
    { id: 3, name: "Competitive Landscape", desc: "Map existing solutions" },
    { id: 4, name: "Success Metrics", desc: "Define measurable outcomes" },
    { id: 5, name: "User Journey Mapping", desc: "Visualize the experience" },
];

const CHECKPOINT_NAMES = {
    1: "Ask Probing Questions",
    2: "Synthesize Problem Statement",
    3: "JTBD Analysis",
    4: "Competitive Landscape",
    5: "Success Metrics",
    6: "User Journey Mapping",
    7: "Discovery Summary",
};

const PHASES_SOLUTION = [
    { id: 1, name: "Discovery Input", desc: "Synthesize discovery findings" },
    { id: 2, name: "Barrier Analysis", desc: "Identify what prevents completion" },
    { id: 3, name: "Opportunity Exploration", desc: "Explore low-tech solutions" },
    { id: 4, name: "Opportunity Solution Tree", desc: "Visualize opportunities" },
    { id: 5, name: "T-Shirt Sizing", desc: "Estimate relative effort" },
    { id: 6, name: "RICE Prioritization", desc: "Score by RICE framework" },
    { id: 7, name: "Solution Recommendation", desc: "Recommend next best step" },
    { id: 8, name: "Validation Plan", desc: "Define testing approach" },
];

const SKILL_CONFIG = {
    discovery: {
        phases: PHASES_DISCOVERY,
        brandName: "Discovery",
        stepLabel: "Product Discovery",
        stepTitle: "What problem are you trying to solve today?",
        landingEyebrow: "Step 1 of 5",
        landingHeadline: "What problem are you trying to solve today?",
        landingSubtitle: "Describe the customer problem or product idea you're exploring. Be as specific as you can — we'll refine it together.",
        startBtnText: "Start Discovery",
        senderName: "Product Discovery Manager",
        welcomeMsg: `<p>Hello! I'm your Product Discovery Manager. I'll guide you through a structured discovery process grounded in Jobs-to-be-Done and Marty Cagan's product model principles.</p><p>We'll work through 5 phases together — stopping at each checkpoint for your input before continuing.</p>`,
        saveEndpoint: "/api/save-discovery",
        listEndpoint: "/api/discoveries",
        reportEndpointPrefix: "/api/generate-report",
        reportUrlPrefix: "/Discovery/_result",
        browseTitle: "Saved Discoveries",
        emptyMsg: "No discoveries yet. Start a discovery session and save it!",
        solutionToggleText: "Help me explore solutions",
    },
    solution: {
        phases: PHASES_SOLUTION,
        brandName: "Solution",
        stepLabel: "Solution Architect",
        stepTitle: "What discovery output are we solutioning for?",
        landingEyebrow: "Step 1 of 8",
        landingHeadline: "What discovery output are we solutioning for?",
        landingSubtitle: "Paste your discovery summary or describe the problem space. We'll find the quickest, lowest-friction path — starting from free tools and no-code before proposing custom builds.",
        startBtnText: "Start Solutioning",
        senderName: "Solution Architect",
        welcomeMsg: `<p>Hello! I'm your Solution Architect. I'll help you find the quickest, easiest way to solve the problems identified in your discovery.</p><p>We'll explore solutions from process fixes and free tools, through no/low-code platforms, before ever proposing a custom build.</p>`,
        saveEndpoint: "/api/save-solution",
        listEndpoint: "/api/solutions",
        reportEndpointPrefix: "/api/generate-solution-report",
        reportUrlPrefix: "/Solutions/_result",
        browseTitle: "Saved Solutions",
        emptyMsg: "No solutions yet. Start a solution session and save it!",
        solutionToggleText: "Switch to discovery mode",
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
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toast-message');
const saveBtn = document.getElementById('save-btn');
const browseBtn = document.getElementById('browse-btn');
const browseModal = document.getElementById('browse-modal');
const closeModalBtn = document.getElementById('close-modal');
const browseList = document.getElementById('browse-list');

// Dynamic UI elements
const journeyNav = document.getElementById('journey-nav');
const stepLabel = document.getElementById('step-label');
const stepTitle = document.getElementById('step-title');
const brandName = document.querySelector('.brand-name');
const landingEyebrow = document.querySelector('.landing-eyebrow');
const landingHeadline = document.querySelector('.landing-headline');
const landingSubtitle = document.querySelector('.landing-subtitle');
const startBtnSpan = startBtn.querySelector('span');
const welcomeSender = document.getElementById('welcome-sender');
const welcomeText = document.getElementById('welcome-text');
const browseModalTitle = document.getElementById('browse-modal-title');
const solutionToggle = document.getElementById('solution-toggle');
const solutionToggleText = document.getElementById('solution-toggle-text');
const checkpointBadge = document.getElementById('checkpoint-badge');
const checkpointNum = document.getElementById('checkpoint-num');

// PDF upload elements
const pdfUploadZone = document.getElementById('pdf-upload-zone');
const pdfInput = document.getElementById('pdf-input');
const pdfTarget = document.getElementById('pdf-target');
const pdfFileInfo = document.getElementById('pdf-file-info');
const pdfFileName = document.getElementById('pdf-file-name');
const pdfRemoveBtn = document.getElementById('pdf-remove-btn');
const inputToggle = document.getElementById('input-toggle');
const textInputWrapper = document.getElementById('text-input-wrapper');
const startBtnLabel = document.getElementById('start-btn-label');

// Progress bar elements
const progressFill = document.getElementById('progress-fill');
const loadingText = document.getElementById('loading-text');
const progressPercent = document.getElementById('progress-percent');

// Validation UI elements
const validationUi = document.getElementById('validation-ui');
const problemStatementDisplay = document.getElementById('problem-statement-display');
const problemStatementEdit = document.getElementById('problem-statement-edit');
const problemStatementEditor = document.getElementById('problem-statement-editor');
const validationActionsView = document.getElementById('validation-actions-view');
const validationActionsEdit = document.getElementById('validation-actions-edit');
const btnEditStatement = document.getElementById('btn-edit-statement');
const btnConfirmStatement = document.getElementById('btn-confirm-statement');
const btnCancelEdit = document.getElementById('btn-cancel-edit');
const btnSaveEdit = document.getElementById('btn-save-edit');
const btnAddContext = document.getElementById('btn-add-context');

// Onboarding elements
const onboardingScreen = document.getElementById('onboarding-screen');
const onboardingFill = document.getElementById('onboarding-fill');
const onboardingHint = document.getElementById('onboarding-hint');
const onboardingTitle = document.querySelector('.onboarding-title');
const onboardingSubtitle = document.querySelector('.onboarding-subtitle');

// PDF state
let selectedPdfFile = null;
let solutionInputMode = 'pdf'; // 'pdf' | 'text'
let progressInterval = null;
let currentProblemStatement = '';

// ── Helpers ────────────────────────────────────────────────────────────────

function showToast(message, duration = 3000) {
    toastMessage.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), duration);
}

function setLoading(loading, text = 'Analyzing your problem...') {
    isLoading = loading;
    if (loading) {
        loadingIndicator.classList.remove('hidden');
        chatInputArea.classList.add('hidden');
        loadingText.textContent = text;
        startProgressBar();
        sendBtn.disabled = true;
        startBtn.disabled = true;
    } else {
        finishProgressBar();
        // Only restore chat input if we're in chat mode and validation UI is hidden
        if (landingState.classList.contains('hidden') && validationUi.classList.contains('hidden')) {
            chatInputArea.classList.remove('hidden');
        }
        sendBtn.disabled = false;
        startBtn.disabled = false;
    }
}

function startProgressBar() {
    let progress = 0;
    let messageIndex = 0;
    const loadingMessages = [
        'Analyzing your problem...',
        'Synthesizing insights...',
        'Connecting the dots...',
        'Still working...',
        'Almost there...',
    ];
    progressFill.style.width = '0%';
    progressPercent.textContent = '0.00%';
    if (progressInterval) clearInterval(progressInterval);
    if (window.messageInterval) clearInterval(window.messageInterval);
    progressInterval = setInterval(() => {
        if (progress < 30) {
            // Fast start so quick responses don't feel like they jump from single digits
            progress += Math.random() * 4;
            if (progress > 30) progress = 30;
        } else if (progress < 60) {
            progress += Math.random() * 2.5;
            if (progress > 60) progress = 60;
        } else if (progress < 85) {
            progress += Math.random() * 1.5;
            if (progress > 85) progress = 85;
        } else {
            // Fast finish from 85% to 99.99% so it doesn't stall at 100%
            progress += Math.random() * 4;
            if (progress > 99.99) progress = 99.99;
        }
        progressFill.style.width = progress + '%';
        progressPercent.textContent = progress.toFixed(2) + '%';
    }, 400);
    // Cycle loading text to reassure users the system is still active
    window.messageInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % loadingMessages.length;
        loadingText.textContent = loadingMessages[messageIndex];
    }, 3500);
}

function finishProgressBar() {
    if (progressInterval) clearInterval(progressInterval);
    if (window.messageInterval) clearInterval(window.messageInterval);
    progressFill.style.width = '100%';
    progressPercent.textContent = '100%';
    setTimeout(() => {
        loadingIndicator.classList.add('hidden');
        progressFill.style.width = '0%';
        progressPercent.textContent = '0%';
    }, 400);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function looksLikeProblemStatementFn(text) {
    if (!text) return false;
    const lower = text.toLowerCase();
    const hasStruggle = lower.includes('struggle');
    const hasBecause = lower.includes('because');
    const hasBlockquote = text.includes('>');
    const hasBold = text.includes('**');
    const hasConfirms = lower.includes('does this accurately capture') || lower.includes('what should i adjust');
    return hasStruggle && hasBecause && (hasBlockquote || hasBold || hasConfirms);
}

function markdownToHtml(markdown) {
    let html = escapeHtml(markdown);

    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/^&gt; (.*$)/gim, '<blockquote>$1</blockquote>');
    html = html.replace(/^---$/gim, '<hr>');

    const tableRegex = /((?:\|[^\n]*\|\n?)+)/g;
    html = html.replace(tableRegex, (match) => {
        const rows = match.trim().split('\n').filter(r => r.trim());
        if (rows.length < 2) return match;
        let tableHtml = '<table>';
        rows.forEach((row, i) => {
            const cells = row.split('|').filter(c => c.trim() !== '');
            if (cells.length === 0) return;
            if (cells.every(c => c.trim().replace(/-/g, '') === '')) return;
            const tag = i === 0 ? 'th' : 'td';
            tableHtml += '<tr>' + cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>';
        });
        tableHtml += '</table>';
        return tableHtml;
    });

    html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => '<ul>' + match + '</ul>');
    html = html.replace(/\n\n/g, '</p><p>');
    html = '<p>' + html + '</p>';
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<(?:h[1-6]|ul|ol|pre|blockquote|hr|table)[^>]*>)/g, '$1');
    html = html.replace(/(<\/(?:h[1-6]|ul|ol|pre|blockquote|hr|table)>)<\/p>/g, '$1');

    return html;
}

function getCurrentPhases() {
    return SKILL_CONFIG[currentSkill].phases;
}

function updateJourneyTracker(phaseId, checkpoint = null) {
    const cp = checkpoint || currentCheckpoint || 1;

    document.querySelectorAll('.journey-item').forEach(item => {
        const itemPhase = parseInt(item.dataset.phase);
        item.classList.remove('active', 'completed');

        if (itemPhase === phaseId) {
            item.classList.add('active');
        } else if (itemPhase < phaseId) {
            item.classList.add('completed');
        }
    });

    // Update checkpoint sub-steps within Phase 1
    document.querySelectorAll('.checkpoint-substep').forEach((sub, index) => {
        sub.classList.remove('active', 'completed');
        const subCp = index + 1;
        if (subCp === cp) {
            sub.classList.add('active');
        } else if (subCp < cp) {
            sub.classList.add('completed');
        }
    });

    // Update checkpoint badge
    if (currentSkill === 'discovery' && checkpoint) {
        checkpointBadge.classList.remove('hidden');
        checkpointNum.textContent = cp;
    } else {
        checkpointBadge.classList.add('hidden');
    }

    // Update header title based on phase
    const phase = getCurrentPhases().find(p => p.id === phaseId);
    if (phase) {
        stepTitle.textContent = phase.name;
        stepLabel.textContent = currentSkill === 'discovery' ? 'Product Discovery' : 'Solution Architect';
    }
}

function renderJourney() {
    const phases = getCurrentPhases();
    const title = currentSkill === 'discovery' ? 'Discovery Journey' : 'Solution Journey';

    // Build checkpoint sub-steps for Phase 1 (Problem Elicitation) in discovery mode
    const checkpointSubsteps = currentSkill === 'discovery' ? `
        <div class="checkpoint-substeps">
            <div class="checkpoint-substep active" data-substep="1">
                <div class="substep-dot"></div>
                <span>Problem Synthesis</span>
            </div>
            <div class="checkpoint-substep" data-substep="2">
                <div class="substep-dot"></div>
                <span>Problem Statement</span>
            </div>
        </div>
    ` : '';

    journeyNav.innerHTML = `
        <div class="journey-title">${title}</div>
        <div class="journey-list">
            ${phases.map((phase, index) => `
                <div class="journey-item ${index === 0 ? 'active' : ''}" data-phase="${phase.id}">
                    <div class="journey-dot"></div>
                    <div class="journey-info">
                        <div class="journey-name">${phase.name}</div>
                        <div class="journey-desc">${phase.desc}</div>
                        ${phase.id === 1 && currentSkill === 'discovery' ? checkpointSubsteps : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function applySkillUI() {
    const cfg = SKILL_CONFIG[currentSkill];

    brandName.textContent = cfg.brandName;
    stepLabel.textContent = cfg.stepLabel;
    stepTitle.textContent = cfg.stepTitle;

    renderJourney();

    landingEyebrow.textContent = cfg.landingEyebrow;
    landingHeadline.textContent = cfg.landingHeadline;
    landingSubtitle.textContent = cfg.landingSubtitle;
    startBtnLabel.textContent = cfg.startBtnText;

    welcomeSender.textContent = cfg.senderName;
    welcomeText.innerHTML = cfg.welcomeMsg;

    browseModalTitle.textContent = cfg.browseTitle;
    solutionToggleText.textContent = cfg.solutionToggleText;

    // Show/hide inputs based on skill
    if (currentSkill === 'solution') {
        // Default to PDF for solution mode
        setSolutionInputMode('pdf');
    } else {
        // Discovery mode: always text
        pdfUploadZone.classList.add('hidden');
        textInputWrapper.classList.remove('hidden');
        inputToggle.classList.add('hidden');
    }

    // Show/hide examples based on skill
    const examples = document.getElementById('landing-examples');
    if (examples) {
        examples.style.display = currentSkill === 'discovery' ? 'block' : 'none';
    }
}

function setSolutionInputMode(mode) {
    solutionInputMode = mode;
    if (mode === 'pdf') {
        pdfUploadZone.classList.remove('hidden');
        textInputWrapper.classList.add('hidden');
        inputToggle.classList.remove('hidden');
        inputToggle.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="12" x2="16" y2="12"/><polyline points="12 8 16 12 12 16"/></svg> I don't have a PDF, type instead`;
    } else {
        pdfUploadZone.classList.add('hidden');
        textInputWrapper.classList.remove('hidden');
        inputToggle.classList.remove('hidden');
        inputToggle.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg> Upload a PDF instead`;
    }
}

async function switchSkill(skill) {
    if (skill === 'solution') {
        const ready = await ensureSolutionIngested();
        if (!ready) return;
    }
    currentSkill = skill;
    applySkillUI();
    showLandingInterface();
    loadSessions();
}

function highlightCheckpoints(html) {
    // Checkpoint markers are now stripped by backend; this is a no-op
    return html;
}

// ── Validation UI ──────────────────────────────────────────────────────────

function showValidationUI(content) {
    // 1. Strip any checkpoint markers that may have slipped through
    let cleaned = content.replace(/📍\s*CHECKPOINT\s*\d+[^\n]*/gi, '').trim();

    // 2. Strip common preamble patterns the model sometimes adds
    cleaned = cleaned.replace(/^(Here[']?s|Here is)\s+(the\s+)?(synthesized\s+)?problem statement[^\n]*\.?\s*[\n\r]+/i, '');
    cleaned = cleaned.replace(/^Based on our discussion, here[']?s the problem statement\.?\s*[\n\r]+/i, '');
    cleaned = cleaned.replace(/^(Thank you for the detailed answers[^\n]*[\n\r]+)+/i, '');

    // 3. Split into paragraphs and identify statement vs follow-up
    const parts = cleaned.split(/\n\s*\n/).map(p => p.trim()).filter(p => p.length > 0);

    let statement = '';
    let followUp = '';

    for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        // Detect follow-up question (short and ends with ?)
        if (part.endsWith('?') && part.length < 300) {
            followUp = part;
            continue;
        }
        // Detect preamble (first paragraph, no bold, no blockquote)
        if (i === 0 && /here'?s the|based on our discussion|problem statement/i.test(part) && !part.startsWith('**') && !part.startsWith('>')) {
            continue;
        }
        // First remaining paragraph is the problem statement
        if (!statement) {
            statement = part;
        }
    }

    // Fallbacks
    if (!statement && parts.length > 0) {
        statement = parts[0];
    }
    if (!followUp) {
        followUp = 'Does this accurately capture the problem? What should I adjust?';
    }

    currentProblemStatement = statement || cleaned;
    problemStatementDisplay.innerHTML = markdownToHtml(currentProblemStatement);
    problemStatementEditor.value = currentProblemStatement.replace(/\*\*/g, '').replace(/&gt;\s*/g, '> ');

    // Show follow-up question below the statement box
    const followUpEl = document.getElementById('validation-follow-up');
    if (followUpEl) {
        followUpEl.innerHTML = markdownToHtml(followUp);
    }

    validationUi.classList.remove('hidden');
    chatMessages.classList.add('hidden');
    chatInputArea.classList.add('hidden');
    validationActionsView.classList.remove('hidden');
    validationActionsEdit.classList.add('hidden');
    problemStatementEdit.classList.add('hidden');
}

function hideValidationUI() {
    validationUi.classList.add('hidden');
    chatMessages.classList.remove('hidden');
    chatInputArea.classList.remove('hidden');
}

async function confirmProblemStatement() {
    if (!currentSessionId) return;
    hideValidationUI();
    await proceedToNextCheckpoint();
}

async function saveEditedStatement() {
    const edited = problemStatementEditor.value.trim();
    if (!edited) {
        showToast('Problem statement cannot be empty');
        return;
    }
    currentProblemStatement = edited;
    hideValidationUI();
    // Send the edited statement as confirmation
    await sendMessage(`Yes, that captures it. Here's my revised problem statement:\n\n${edited}`);
}

function hasCheckpointMarker(content) {
    return /📍\s*CHECKPOINT\s*\d+/i.test(content);
}

function getCheckpointNumber(content) {
    const match = content.match(/📍\s*CHECKPOINT\s*(\d+)/i);
    return match ? parseInt(match[1]) : null;
}

function addMessage(role, content, phase = 1, canAdvance = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.dataset.phase = phase;

    const avatarSvg = role === 'user'
        ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
        : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>';
    const sender = role === 'user' ? 'You' : SKILL_CONFIG[currentSkill].senderName;
    let htmlContent = markdownToHtml(content);
    htmlContent = highlightCheckpoints(htmlContent);

    let proceedButtonHtml = '';
    if (role === 'assistant' && canAdvance && currentSkill === 'discovery' && currentCheckpoint >= 3) {
        const nextCpName = currentCheckpoint < 7 ? CHECKPOINT_NAMES[currentCheckpoint + 1] : null;
        if (nextCpName) {
            proceedButtonHtml = `
                <div class="checkpoint-actions">
                    <button class="btn-proceed" onclick="proceedToNextCheckpoint()">
                        Confirm & Proceed to ${nextCpName}
                    </button>
                </div>
            `;
        }
    }

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatarSvg}</div>
        <div class="message-body">
            <div class="message-sender">${sender}</div>
            <div class="message-text">${htmlContent}</div>
            ${proceedButtonHtml}
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function proceedToNextCheckpoint() {
    if (!currentSessionId || isLoading) return;

    document.querySelectorAll('.checkpoint-actions').forEach(el => el.remove());

    setLoading(true);
    try {
        const response = await fetch('/api/advance-checkpoint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId }),
        });

        const data = await response.json();

        if (data.error) {
            addMessage('assistant', `**Error:** ${data.error}`);
        } else {
            currentCheckpoint = data.current_checkpoint || 1;
            addMessage('assistant', data.response, data.current_phase, data.can_advance);
            updateJourneyTracker(data.current_phase, currentCheckpoint);
            await loadSessions();
        }
    } catch (err) {
        addMessage('assistant', `**Connection Error:** ${err.message}`);
    } finally {
        setLoading(false);
        chatInput.focus();
    }
}

function showChatInterface() {
    landingState.classList.add('hidden');
    validationUi.classList.add('hidden');
    chatMessages.classList.remove('hidden');
    chatInputArea.classList.remove('hidden');
    exportBtn.disabled = false;
    saveBtn.disabled = false;
}

function showLandingInterface() {
    landingState.classList.remove('hidden');
    validationUi.classList.add('hidden');
    chatMessages.classList.add('hidden');
    chatInputArea.classList.add('hidden');
    exportBtn.disabled = true;
    saveBtn.disabled = true;
    problemInput.value = '';
    chatInput.value = '';
    currentSessionId = null;
    currentCheckpoint = 1;
    selectedPdfFile = null;
    pdfFileInfo.classList.add('hidden');
    pdfTarget.classList.remove('hidden');
    updateJourneyTracker(1, 1);

    // Reset input mode
    if (currentSkill === 'solution') {
        setSolutionInputMode('pdf');
    }

    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="message-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
            </div>
            <div class="message-body">
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
            currentCheckpoint = data.current_checkpoint || 1;

            if (data.validation_ui) {
                showValidationUI(data.response);
            } else if (currentCheckpoint <= 2 && looksLikeProblemStatementFn(data.response)) {
                // Safety net: backend missed the problem statement detection (only for CP1/CP2)
                currentCheckpoint = 2;
                showValidationUI(data.response);
            } else {
                addMessage('assistant', data.response, data.current_phase, data.can_advance);
            }

            updateJourneyTracker(data.current_phase, currentCheckpoint);
            await loadSessions();
        }
    } catch (err) {
        addMessage('assistant', `**Connection Error:** ${err.message}\n\nPlease make sure the Flask server is running.`);
    } finally {
        setLoading(false);
        if (!validationUi.classList.contains('hidden')) {
            // Focus nothing when validation UI is shown
        } else {
            chatInput.focus();
        }
    }
}

async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        sessions = data;

        const currentVal = sessionSelect.value;
        sessionSelect.innerHTML = '<option value="">New Session</option>';

        data.forEach(session => {
            if (session.skill !== currentSkill) return;
            const option = document.createElement('option');
            option.value = session.id;
            const date = new Date(session.created_at).toLocaleString();
            const cpLabel = session.current_checkpoint ? ` · CP${session.current_checkpoint}` : '';
            option.textContent = `Session ${session.id} — ${session.phase_name}${cpLabel}`;
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

        if (session.skill && session.skill !== currentSkill) {
            switchSkill(session.skill);
        }

        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="message-avatar">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
                </div>
                <div class="message-body">
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
        currentCheckpoint = session.current_checkpoint || 1;
        updateJourneyTracker(session.current_phase, currentCheckpoint);

        // If session was in checkpoint 2 (or last message looks like a problem statement),
        // show validation UI with last assistant message
        const lastAssistantMsg = session.messages.filter(m => m.role === 'assistant').pop();
        const looksLikeProblemStatement = lastAssistantMsg && currentCheckpoint <= 2 && looksLikeProblemStatementFn(lastAssistantMsg.content);
        if ((currentCheckpoint === 2 || looksLikeProblemStatement) && lastAssistantMsg) {
            showValidationUI(lastAssistantMsg.content);
        } else {
            showChatInterface();
        }
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
    }
}

async function generateReport() {
    if (!currentSessionId) return;

    const cfg = SKILL_CONFIG[currentSkill];
    await saveOutput();

    try {
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
                    <div class="discovery-meta">${d.formatted_date} · ${d.md_files} files ${d.has_report ? '· Report ready' : ''}</div>
                </div>
                <div class="discovery-actions">
                    ${d.has_report ? `<a href="${cfg.reportUrlPrefix}/${d.name}/index.html" target="_blank" class="btn-primary">View</a>` : ''}
                    <button class="btn-secondary btn-generate" data-folder="${d.name}">Generate</button>
                </div>
            </div>
        `).join('');

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

startBtn.addEventListener('click', async () => {
    if (currentSkill === 'solution' && solutionInputMode === 'pdf') {
        if (!selectedPdfFile) {
            showToast('Please upload a PDF first');
            pdfTarget.click();
            return;
        }
        await uploadPdfAndStart();
        return;
    }

    const problem = problemInput.value.trim();
    if (!problem) {
        showToast('Please describe your problem first');
        problemInput.focus();
        return;
    }
    showChatInterface();
    sendMessage(problem);
});

// PDF upload handling
pdfTarget.addEventListener('click', () => pdfInput.click());

pdfInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handlePdfSelect(file);
});

// Drag & drop
pdfUploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    pdfTarget.style.borderColor = 'var(--text-secondary)';
    pdfTarget.style.background = 'var(--bg-elevated)';
});

pdfUploadZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    pdfTarget.style.borderColor = '';
    pdfTarget.style.background = '';
});

pdfUploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    pdfTarget.style.borderColor = '';
    pdfTarget.style.background = '';
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
        handlePdfSelect(file);
    } else {
        showToast('Please drop a PDF file');
    }
});

function handlePdfSelect(file) {
    selectedPdfFile = file;
    pdfFileName.textContent = file.name;
    pdfTarget.classList.add('hidden');
    pdfFileInfo.classList.remove('hidden');
}

pdfRemoveBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    selectedPdfFile = null;
    pdfInput.value = '';
    pdfFileInfo.classList.add('hidden');
    pdfTarget.classList.remove('hidden');
});

inputToggle.addEventListener('click', () => {
    const newMode = solutionInputMode === 'pdf' ? 'text' : 'pdf';
    setSolutionInputMode(newMode);
});

async function uploadPdfAndStart() {
    if (!selectedPdfFile) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('pdf', selectedPdfFile);

    try {
        const response = await fetch('/api/upload-solution-pdf', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (data.error) {
            showToast(`Error: ${data.error}`);
            setLoading(false);
            return;
        }

        const extractedText = data.text || '';
        const message = extractedText
            ? `Here is my discovery summary from a PDF:\n\n${extractedText}\n\nPlease help me explore solutions based on this.`
            : 'I uploaded a discovery PDF. Please help me explore solutions.';

        showChatInterface();
        sendMessage(message);
    } catch (err) {
        showToast(`Upload failed: ${err.message}`);
        setLoading(false);
    }
}

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
    // Ensure cursor stays visible when typing multi-line text
    chatInput.scrollTop = chatInput.scrollHeight;
});

problemInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        startBtn.click();
    }
});

exportBtn.addEventListener('click', exportSession);
saveBtn.addEventListener('click', saveOutput);
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

solutionToggle.addEventListener('click', () => {
    const newSkill = currentSkill === 'discovery' ? 'solution' : 'discovery';
    switchSkill(newSkill);
});

// Validation UI event listeners
btnConfirmStatement.addEventListener('click', confirmProblemStatement);

btnEditStatement.addEventListener('click', () => {
    validationActionsView.classList.add('hidden');
    validationActionsEdit.classList.remove('hidden');
    problemStatementEdit.classList.remove('hidden');
    problemStatementDisplay.classList.add('hidden');
    problemStatementEditor.focus();
});

btnCancelEdit.addEventListener('click', () => {
    validationActionsEdit.classList.add('hidden');
    validationActionsView.classList.remove('hidden');
    problemStatementEdit.classList.add('hidden');
    problemStatementDisplay.classList.remove('hidden');
});

btnSaveEdit.addEventListener('click', saveEditedStatement);

btnAddContext.addEventListener('click', async () => {
    if (!currentSessionId || isLoading) return;
    setLoading(true, 'Going back to add more context...');
    try {
        const response = await fetch('/api/go-back-checkpoint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId }),
        });
        const data = await response.json();
        if (data.error) {
            showToast(`Error: ${data.error}`);
        } else {
            currentCheckpoint = data.current_checkpoint || 1;
            hideValidationUI();
            addMessage('assistant', data.response, data.current_phase, data.can_advance);
            updateJourneyTracker(data.current_phase, currentCheckpoint);
        }
    } catch (err) {
        showToast(`Failed: ${err.message}`);
    } finally {
        setLoading(false);
    }
});

// Example pills
document.querySelectorAll('.example-pill').forEach(pill => {
    pill.addEventListener('click', () => {
        problemInput.value = pill.dataset.example;
        problemInput.focus();
    });
});

// ── Onboarding / Ingestion ───────────────────────────────────────────────

let onboardingInterval = null;

function startOnboardingProgress() {
    let progress = 0;
    onboardingFill.style.width = '0%';
    if (onboardingInterval) clearInterval(onboardingInterval);
    onboardingInterval = setInterval(() => {
        if (progress < 85) {
            progress += Math.random() * 3;
            if (progress > 85) progress = 85;
        } else {
            progress += Math.random() * 1;
            if (progress > 98) progress = 98;
        }
        onboardingFill.style.width = progress + '%';
    }, 600);
}

function stopOnboardingProgress() {
    if (onboardingInterval) clearInterval(onboardingInterval);
    onboardingFill.style.width = '100%';
}

async function checkIngestionStatus() {
    try {
        const response = await fetch('/api/ingest-status');
        const data = await response.json();
        if (data.discovery_ingested) {
            onboardingScreen.classList.add('hidden');
            return;
        }
        // Show onboarding for discovery ingestion only
        onboardingScreen.classList.remove('hidden');
        onboardingTitle.textContent = 'Product Discovery Manager';
        onboardingSubtitle.textContent = 'Setting up your discovery workspace...';
        startOnboardingProgress();
        await fetch('/api/ingest-materials', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ skill: 'discovery' }),
        });
        // Poll until discovery complete
        const poll = setInterval(async () => {
            try {
                const r = await fetch('/api/ingest-status');
                const d = await r.json();
                // Update hint with current file
                if (d.current_file) {
                    onboardingHint.textContent = `Processing ${d.current_file}...`;
                } else if (d.stage === 'summarizing') {
                    onboardingHint.textContent = 'Summarizing reference materials...';
                }
                if (d.discovery_ingested) {
                    clearInterval(poll);
                    stopOnboardingProgress();
                    setTimeout(() => {
                        onboardingScreen.classList.add('hidden');
                    }, 800);
                }
            } catch (e) {
                // Keep polling
            }
        }, 2000);
    } catch (err) {
        onboardingScreen.classList.add('hidden');
        console.error('Ingestion status check failed:', err);
    }
}

async function ensureSolutionIngested() {
    try {
        const response = await fetch('/api/ingest-status');
        const data = await response.json();
        if (data.solution_ingested) {
            return true;
        }
        // Show onboarding for solution ingestion
        onboardingScreen.classList.remove('hidden');
        onboardingTitle.textContent = 'Solution Architect';
        onboardingSubtitle.textContent = 'Preparing solution frameworks...';
        onboardingHint.textContent = 'Ingesting reference materials so solutioning sessions are fast and lightweight.';
        startOnboardingProgress();
        await fetch('/api/ingest-materials', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ skill: 'solution' }),
        });
        return new Promise((resolve) => {
            const poll = setInterval(async () => {
                try {
                    const r = await fetch('/api/ingest-status');
                    const d = await r.json();
                    if (d.current_file) {
                        onboardingHint.textContent = `Processing ${d.current_file}...`;
                    } else if (d.stage === 'summarizing') {
                        onboardingHint.textContent = 'Summarizing reference materials...';
                    }
                    if (d.solution_ingested) {
                        clearInterval(poll);
                        stopOnboardingProgress();
                        setTimeout(() => {
                            onboardingScreen.classList.add('hidden');
                            resolve(true);
                        }, 800);
                    }
                } catch (e) {
                    // Keep polling
                }
            }, 2000);
        });
    } catch (err) {
        onboardingScreen.classList.add('hidden');
        console.error('Solution ingestion check failed:', err);
        return true; // Allow switch to proceed even if ingestion fails
    }
}

// ── Init ───────────────────────────────────────────────────────────────────

async function init() {
    applySkillUI();
    await checkIngestionStatus();
    await loadSessions();
    problemInput.focus();
    console.log('Product Discovery Manager loaded');
}

init();
