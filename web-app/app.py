#!/usr/bin/env python3
"""
Product Discovery Manager - Web Interface
A locally-runnable web app that triggers the product-discovery-manager skill via Kimi CLI.
"""

import os
import re
import sys
import json
import uuid
import time
import subprocess
from datetime import datetime
from threading import Lock, Thread

from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Optional PDF text extraction
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

# Import report generator
from report_generator import (
    create_discovery_folder,
    save_discovery_phase,
    save_discovery_summary,
    generate_report,
    list_discovery_folders,
    create_solution_folder,
    save_solution_phase,
    save_solution_summary,
    list_solution_folders,
    DISCOVERIES_DIR,
    SOLUTIONS_DIR,
)

# ── Configuration ──────────────────────────────────────────────────────────

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_WORK_DIR = PROJECT_ROOT
DEFAULT_TIMEOUT = 300  # seconds

# Kimi CLI path: override with KIMI_BIN env var for portability.
KIMI_BIN = os.environ.get(
    "KIMI_BIN",
    os.path.expanduser(
        "~/Library/Application Support/Code/User/globalStorage/"
        "moonshot-ai.kimi-code/bin/kimi/kimi"
    ),
)

# ── Flask App ──────────────────────────────────────────────────────────────

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ── In-Memory Session Store ────────────────────────────────────────────────

sessions = {}
sessions_lock = Lock()

DISCOVERY_PHASES = [
    {"id": 1, "name": "Problem Elicitation", "keywords": ["problem statement", "problem elicitation", "phase 1"]},
    {"id": 2, "name": "JTBD Analysis", "keywords": ["jobs-to-be-done", "jtbd", "jobs to be done", "phase 2"]},
    {"id": 3, "name": "Competitive Landscape", "keywords": ["competitive landscape", "existing solutions", "phase 3"]},
    {"id": 4, "name": "Success Metrics", "keywords": ["success metrics", "satisfaction metrics", "phase 4"]},
    {"id": 5, "name": "User Journey Mapping", "keywords": ["user journey", "journey map", "phase 5"]},
]

SOLUTION_PHASES = [
    {"id": 1, "name": "Discovery Input", "keywords": ["discovery input", "retrieve discovery", "phase 1"]},
    {"id": 2, "name": "Barrier Analysis", "keywords": ["barrier analysis", "jtbd barrier", "what prevents", "phase 2"]},
    {"id": 3, "name": "Opportunity Exploration", "keywords": ["opportunity exploration", "explore opportunities", "low tech", "no code", "phase 3"]},
    {"id": 4, "name": "Opportunity Solution Tree", "keywords": ["opportunity tree", "solution tree", "phase 4"]},
    {"id": 5, "name": "T-Shirt Sizing", "keywords": ["t-shirt sizing", "sizing", "effort estimate", "phase 5"]},
    {"id": 6, "name": "RICE Prioritization", "keywords": ["rice", "prioritization", "rice score", "phase 6"]},
    {"id": 7, "name": "Solution Recommendation", "keywords": ["recommendation", "recommended next step", "next step", "phase 7"]},
    {"id": 8, "name": "Validation Plan", "keywords": ["validation plan", "pilot", "validate", "phase 8"]},
]

CHECKPOINT_NAMES = {
    1: "Ask Probing Questions",
    2: "Synthesize Problem Statement",
    3: "JTBD Analysis",
    4: "Competitive Landscape",
    5: "Success Metrics",
    6: "User Journey Mapping",
    7: "Discovery Summary",
}

DISCOVERY_CHECKPOINTS = {
    1: {
        "instruction": (
            "You are at CHECKPOINT 1: Problem Elicitation — Ask Probing Questions.\n\n"
            "Your ONLY task is to ask 3–5 structured probing questions about the user's problem. "
            "Draw from these categories:\n"
            "- Context: When does this problem occur? What is the user trying to accomplish?\n"
            "- Frequency & severity: How often does this happen? What is the impact?\n"
            "- Current behavior: What do users do today? What workarounds exist?\n"
            "- User segment: Who experiences this most? Which persona or segment?\n"
            "- Desired outcome: What would success look like? If solved, what changes?\n\n"
            "ABSOLUTE RULES:\n"
            "1. Ask ONLY questions. Do NOT synthesize a problem statement.\n"
            "2. Do NOT do JTBD analysis or any other phase.\n"
            "3. End your response with: 📍 CHECKPOINT 1\n"
            "4. Then stop. The user will answer your questions or ask clarifying questions."
        ),
    },
    2: {
        "instruction": (
            "You are at CHECKPOINT 2: Problem Elicitation — Synthesize Problem Statement.\n\n"
            "The user has been discussing their problem with you. "
            "Your ONLY task is to synthesize a confirmed problem statement in this exact format:\n\n"
            "> **[User type]** struggles to **[achieve goal]** because **[obstacle]**, which leads to **[negative consequence]**.\n\n"
            "After presenting the problem statement, ask:\n"
            "\"Does this accurately capture the problem? What should I adjust?\"\n\n"
            "If the user asks clarifying questions or requests changes, address them. "
            "Stay in this checkpoint until they confirm the problem statement.\n\n"
            "ABSOLUTE RULES:\n"
            "1. Present ONLY the synthesized problem statement (or address user feedback).\n"
            "2. Do NOT proceed to JTBD analysis or any other phase.\n"
            "3. End your response with: 📍 CHECKPOINT 2\n"
            "4. Then stop. The user will confirm, edit, or ask questions."
        ),
    },
    3: {
        "instruction": (
            "You are at CHECKPOINT 3: JTBD Analysis.\n\n"
            "The user has confirmed the problem statement. "
            "Your ONLY task is to perform Jobs-to-be-Done (JTBD) analysis.\n\n"
            "1. Identify the core functional job — the main task the user is trying to accomplish.\n"
            "2. Identify related jobs across three dimensions:\n"
            "   - Functional: Practical, task-oriented jobs\n"
            "   - Emotional: How the user wants to feel\n"
            "   - Social: How the user wants to be perceived\n"
            "3. Formulate JTBD statements using: When I [situation], I want to [motivation], so I can [expected outcome].\n\n"
            "For each job, document:\n"
            "- Job statement\n"
            "- Value of completion (why it matters)\n"
            "- Current satisfaction (frustrated / tolerating / satisfied, or 1–5)\n"
            "- Importance (critical / important / nice-to-have)\n\n"
            "After presenting the JTBD analysis, ask:\n"
            "\"Does this capture what you're trying to accomplish? What's missing or mischaracterized?\"\n\n"
            "If the user asks clarifying questions or requests changes, address them. "
            "Stay in this checkpoint until they validate the JTBD.\n\n"
            "ABSOLUTE RULES:\n"
            "1. Present ONLY the JTBD analysis (or address user feedback).\n"
            "2. Do NOT proceed to Competitive Landscape or any other phase.\n"
            "3. End your response with: 📍 CHECKPOINT 3\n"
            "4. Then stop. The user will validate, edit, or ask questions."
        ),
    },
    4: {
        "instruction": (
            "You are at CHECKPOINT 4: Competitive Landscape & Existing Solutions.\n\n"
            "The user has validated the JTBD analysis. "
            "Your ONLY task is to map the competitive landscape and existing solutions.\n\n"
            "If you need more information from the user, ask 1–3 questions about:\n"
            "- What tools, processes, or workarounds do users rely on?\n"
            "- What specific step or limitation causes the most friction?\n"
            "- What does this solution fail to deliver?\n"
            "- When do users abandon it?\n\n"
            "If the user has already provided enough detail, present a competitive gap map with:\n"
            "- Solution: Name/tool/process\n"
            "- Strengths: What it does well\n"
            "- Gaps: Unmet needs or pain points\n"
            "- Retention reason: Why users still use it\n\n"
            "After presenting, ask for confirmation before proceeding.\n\n"
            "If the user asks clarifying questions or requests changes, address them. "
            "Stay in this checkpoint until they confirm.\n\n"
            "ABSOLUTE RULES:\n"
            "1. Present ONLY the competitive landscape analysis (or address user feedback).\n"
            "2. Do NOT proceed to Success Metrics or any other phase.\n"
            "3. End your response with: 📍 CHECKPOINT 4\n"
            "4. Then stop. The user will respond with feedback or confirmation."
        ),
    },
    5: {
        "instruction": (
            "You are at CHECKPOINT 5: Success & Satisfaction Metrics.\n\n"
            "The user has confirmed the competitive landscape. "
            "Your ONLY task is to define success and satisfaction metrics.\n\n"
            "1. Elicit success signals: How would you know this problem is solved?\n"
            "2. Categorize metrics:\n"
            "   - Outcome: What changes in the user's life\n"
            "   - Process: How the experience improves\n"
            "   - Emotional: How the user feels\n"
            "3. Capture current baselines where possible.\n\n"
            "Present a metrics table and ask if they reflect reality.\n\n"
            "If the user asks clarifying questions or requests changes, address them. "
            "Stay in this checkpoint until they confirm.\n\n"
            "ABSOLUTE RULES:\n"
            "1. Present ONLY the success metrics (or address user feedback).\n"
            "2. Do NOT proceed to User Journey Mapping or any other phase.\n"
            "3. End your response with: 📍 CHECKPOINT 5\n"
            "4. Then stop. The user will confirm or adjust."
        ),
    },
    6: {
        "instruction": (
            "You are at CHECKPOINT 6: User Journey Mapping.\n\n"
            "The user has confirmed the success metrics. "
            "Your ONLY task is to create a user journey map.\n\n"
            "Create a journey map with these columns:\n"
            "| Stage | User Action | Touchpoint | Pain Point | Emotion | Opportunity |\n\n"
            "Typical stages (adapt to context):\n"
            "1. Awareness / Trigger: User realizes the need\n"
            "2. Consideration: User explores options\n"
            "3. Decision: User selects a solution\n"
            "4. Execution: User performs the core job\n"
            "5. Completion: User achieves the outcome\n"
            "6. Follow-up: Post-job reflection or next steps\n\n"
            "Link each stage to the relevant JTBD from Checkpoint 3.\n\n"
            "After presenting, ask:\n"
            "\"Does this match your users' actual experience? What stages, pain points, or opportunities are missing?\"\n\n"
            "If the user asks clarifying questions or requests changes, address them. "
            "Stay in this checkpoint until they confirm.\n\n"
            "ABSOLUTE RULES:\n"
            "1. Present ONLY the user journey map (or address user feedback).\n"
            "2. Do NOT produce the final summary yet.\n"
            "3. End your response with: 📍 CHECKPOINT 6\n"
            "4. Then stop. The user will confirm or edit."
        ),
    },
    7: {
        "instruction": (
            "You are at CHECKPOINT 7: Final Discovery Summary.\n\n"
            "The user has confirmed the user journey map. "
            "Your ONLY task is to produce the final structured discovery summary.\n\n"
            "Produce this exact format:\n\n"
            "# Product Discovery Summary\n\n"
            "## 1. Problem Statement\n"
            "[Confirmed problem statement]\n\n"
            "## 2. Jobs-to-be-Done\n"
            "### Core Job\n"
            "- Job: [Statement]\n"
            "- Value: [Why it matters]\n"
            "- Satisfaction: [Current level]\n"
            "- Importance: [Critical/Important/Nice-to-have]\n\n"
            "### Related Jobs\n"
            "[Repeat format]\n\n"
            "## 3. Existing Solutions & Gaps\n"
            "[Table]\n\n"
            "## 4. Success Metrics\n"
            "[Table]\n\n"
            "## 5. User Journey Map\n"
            "[Table]\n\n"
            "ABSOLUTE RULES:\n"
            "1. Produce ONLY the final summary.\n"
            "2. Do NOT ask for further confirmation.\n"
            "3. End your response with: 📍 CHECKPOINT 7 — Discovery Complete"
        ),
    },
}

# ── Helpers ────────────────────────────────────────────────────────────────

def detect_phase(text: str, skill: str = "discovery") -> int:
    """Auto-detect which phase a message belongs to."""
    phases = DISCOVERY_PHASES if skill == "discovery" else SOLUTION_PHASES
    text_lower = text.lower()
    for phase in reversed(phases):
        for kw in phase["keywords"]:
            if kw in text_lower:
                return phase["id"]
    return 1


def user_wants_to_advance(text: str) -> bool:
    """Detect if the user's message explicitly signals they want to proceed to the next checkpoint."""
    text_lower = text.lower().strip()
    advance_signals = [
        "proceed", "next", "continue", "move on", "move forward", "go ahead",
        "looks good", "looks great", "looks accurate", "confirmed", "confirm",
        "yes, that", "yes that", "yes accurate", "yes proceed", "yes continue",
        "yes next", "yes move", "validated", "approved", "accept", "agreed",
        "that captures it", "that is accurate", "that is correct", "that works",
        "satisfied", "happy with", "good to go", "let's move", "lets move",
    ]
    return any(sig in text_lower for sig in advance_signals)


def response_contains_problem_statement(text: str) -> bool:
    """Detect if a Kimi response contains a synthesized problem statement."""
    text_lower = text.lower()
    # Core pattern: [user type] struggle[s] to ... because ...
    has_struggle = "struggle" in text_lower
    has_because = "because" in text_lower
    # Additional signals: blockquote, bold emphasis, confirmation question
    has_blockquote = ">" in text
    has_bold = "**" in text
    has_confirms = (
        "does this accurately capture" in text_lower
        or "what should i adjust" in text_lower
        or "synthesized problem statement" in text_lower
    )
    return has_struggle and has_because and (has_blockquote or has_bold or has_confirms)


def strip_checkpoint_markers(text: str) -> str:
    """Remove checkpoint marker lines from Kimi responses for cleaner UI."""
    # Remove lines like "📍 CHECKPOINT 1" or "📍 CHECKPOINT 2 — ..."
    text = re.sub(r'📍\s*CHECKPOINT\s*\d+[^\n]*', '', text, flags=re.IGNORECASE)
    # Clean up extra whitespace left behind
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# Summary file paths — placed in parent folders to keep them separate from raw PDF materials
DISCOVERY_SUMMARY_PATH = os.path.join(PROJECT_ROOT, "Discovery", "summary.md")
SOLUTION_SUMMARY_PATH = os.path.join(PROJECT_ROOT, "Solutions", "summary.md")

# Ingestion state
ingestion_lock = Lock()
ingestion_state = {
    "in_progress": False,
    "skill": None,
    "current_file": None,
    "stage": "idle",  # idle | extracting | summarizing
}


def _read_summary(skill: str = "discovery") -> str:
    """Read the summary.md file if it exists, returning its contents or empty string."""
    path = DISCOVERY_SUMMARY_PATH if skill == "discovery" else SOLUTION_SUMMARY_PATH
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return ""


def build_discovery_system_prompt(checkpoint: int = None) -> str:
    """Build the discovery skill-triggering system prompt."""
    summary = _read_summary("discovery")

    # CP1: lightweight prompt, no reference reading needed
    if checkpoint == 1:
        return (
            "You are a Product Discovery Manager conducting structured problem elicitation.\n\n"
            "Your ONLY task is to ask 3–5 structured probing questions about the user's problem. "
            "Draw from these categories:\n"
            "- Context: When does this problem occur? What is the user trying to accomplish?\n"
            "- Frequency & severity: How often does this happen? What is the impact?\n"
            "- Current behavior: What do users do today? What workarounds exist?\n"
            "- User segment: Who experiences this most? Which persona or segment?\n"
            "- Desired outcome: What would success look like? If solved, what changes?\n\n"
            "ABSOLUTE RULES:\n"
            "1. Ask ONLY questions. Do NOT synthesize a problem statement.\n"
            "2. Do NOT do JTBD analysis or any other phase.\n"
            "3. End your response with: 📍 CHECKPOINT 1\n"
            "4. Then stop. The user will answer your questions or ask clarifying questions."
        )

    # CP2: isolated prompt — no file references, only conversation history.
    # Kimi CLI sometimes reads referenced files and gets confused by JTBD content in the summary.
    if checkpoint == 2:
        return (
            "You are a Product Discovery Manager at CHECKPOINT 2: Problem Statement Synthesis.\n\n"
            "Based ONLY on the conversation history, synthesize a single confirmed problem statement "
            "in this exact format:\n\n"
            "> **[User type]** struggles to **[achieve goal]** because **[obstacle]**, which leads to **[negative consequence]**.\n\n"
            "After presenting the statement, ask:\n"
            '"Does this accurately capture the problem? What should I adjust?"\n\n'
            "ABSOLUTE RULES:\n"
            "1. Output ONLY the problem statement and the follow-up question.\n"
            "2. Do NOT read any reference files.\n"
            "3. Do NOT do JTBD analysis or any other phase.\n"
            "4. Do NOT add preamble like 'Here is the problem statement'.\n"
            "5. End your response with: 📍 CHECKPOINT 2"
        )

    # For CP3+, embed the summary directly in the prompt if available.
    if summary:
        base = (
            "You are a Product Discovery Manager following the structured discovery workflow.\n\n"
            "Use the user's own language in JTBD and problem statements. "
            "Iterate rather than perfecting. Present drafts for validation. "
            "If the user asks questions or requests changes, address them collaboratively. "
            "Never rush to the next phase without the user's explicit confirmation.\n\n"
            "--- REFERENCE GUIDE ---\n"
            f"{summary}\n"
            "--- END REFERENCE GUIDE ---\n\n"
        )
    else:
        base = (
            "You are a Product Discovery Manager following the structured discovery workflow "
            "defined in the product-discovery-manager skill. "
            "Ground your work in product model principles, JTBD, and User Journey Mapping.\n\n"
            "Use the user's own language in JTBD and problem statements. "
            "Iterate rather than perfecting. Present drafts for validation. "
            "If the user asks questions or requests changes, address them collaboratively. "
            "Never rush to the next phase without the user's explicit confirmation.\n\n"
        )

    if checkpoint and checkpoint in DISCOVERY_CHECKPOINTS:
        cp = DISCOVERY_CHECKPOINTS[checkpoint]
        return base + cp["instruction"]

    return (
        base +
        "This is a COLLABORATIVE, CHECKPOINT-DRIVEN workflow with 7 checkpoints. "
        "At each checkpoint, output the content for that phase and end your response. "
        "Do not proceed to the next phase within the same response. "
        "The user will reply with their input or confirmation, and you will continue in the next response."
    )


def build_solution_system_prompt() -> str:
    """Build the solution architect skill-triggering system prompt."""
    summary = _read_summary("solution")

    if summary:
        base = (
            "You are a Solution Architect — a senior software engineer adept in various tech stacks, "
            "including no/low code solutions. Your objective is to find the quickest, easiest solution "
            "with as little friction as possible for non-tech-savvy users.\n\n"
            "You follow the structured solution workflow defined in the solution-architect skill.\n\n"
            "--- REFERENCE GUIDE ---\n"
            f"{summary}\n"
            "--- END REFERENCE GUIDE ---\n\n"
        )
    else:
        base = (
            "You are a Solution Architect — a senior software engineer adept in various tech stacks, "
            "including no/low code solutions. Your objective is to find the quickest, easiest solution "
            "with as little friction as possible for non-tech-savvy users.\n\n"
            "You follow the structured solution workflow defined in the solution-architect skill. "
            "Ground your work in Opportunity Solution Trees, RICE Prioritization, and T-Shirt Sizing frameworks.\n\n"
        )

    return (
        base +
        "Your goal is to guide the user through 8 phases:\n"
        "1. Discovery Input - retrieve and synthesize discovery findings\n"
        "2. Barrier Analysis - identify what prevents users from completing each JTBD\n"
        "3. Opportunity Exploration - explore solutions starting from lowest-tech (process fixes, free tools, no/low-code) before proposing custom builds\n"
        "4. Opportunity Solution Tree - visualize barriers, opportunities, and outcomes\n"
        "5. T-Shirt Sizing - estimate relative effort for each opportunity\n"
        "6. RICE Prioritization - score opportunities by Reach, Impact, Confidence, Effort\n"
        "7. Solution Recommendation - recommend the next easiest high-impact step\n"
        "8. Validation Plan - define how to test the solution with real users\n\n"
        "Key principles:\n"
        "- Low-tech first: a spreadsheet + WhatsApp group that works today beats an app that ships in 3 months\n"
        "- Friction-aware: the best solution is the one users will actually adopt\n"
        "- Validate before building: never recommend a custom build without testing a no-code version first\n"
        "- Ground in discovery: every opportunity must trace back to a specific JTBD barrier\n\n"
        "At the end, produce a structured summary with: Discovery Input, Opportunity Solution Tree, "
        "T-Shirt Sizing table, RICE Analysis table, Recommended Next Step, and Validation Plan."
    )


def run_kimi(prompt: str, skill: str = "discovery", work_dir: str = DEFAULT_WORK_DIR,
             timeout: int = DEFAULT_TIMEOUT, system_prompt: str = None) -> str:
    """Invoke Kimi CLI in non-interactive print mode."""
    if system_prompt is None:
        if skill == "solution":
            system_prompt = build_solution_system_prompt()
        else:
            system_prompt = build_discovery_system_prompt()

    full_prompt = f"{system_prompt}\n\n---\n\nConversation history:\n{prompt}"

    cmd = [
        KIMI_BIN,
        "--print",
        "--prompt", full_prompt,
        "--work-dir", work_dir,
        "--output-format", "text",
        "--final-message-only",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=work_dir,
        )
        if result.returncode != 0:
            error_msg = result.stderr.strip() or "Unknown error from Kimi CLI"
            return f"[Error] Kimi CLI exited with code {result.returncode}:\n{error_msg}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[Error] Kimi CLI timed out. The request took too long to process."
    except FileNotFoundError:
        return f"[Error] Kimi CLI not found at: {KIMI_BIN}"
    except Exception as e:
        return f"[Error] Failed to run Kimi CLI: {str(e)}"


# ── API Routes ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    session_id = data.get("session_id")
    skill = data.get("skill", "discovery")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    phases = DISCOVERY_PHASES if skill == "discovery" else SOLUTION_PHASES

    # Create or retrieve session
    with sessions_lock:
        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())[:8]
            sessions[session_id] = {
                "id": session_id,
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "current_phase": 1,
                "current_checkpoint": 1,
                "cp_input_count": 0,
                "skill": skill,
            }
        session = sessions[session_id]

    # Detect phase from user message
    user_phase = detect_phase(message, skill)

    # Store user message
    session["messages"].append({
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat(),
        "phase": user_phase,
    })

    # For discovery skill: manage checkpoint progression
    checkpoint = session.get("current_checkpoint", 1)
    auto_advanced = False
    validation_ui = False
    can_go_back = False

    if skill == "discovery":
        # Track input count per checkpoint
        if checkpoint == 1:
            session["cp_input_count"] = session.get("cp_input_count", 0) + 1
            # Auto-advance to CP2 after 3 user inputs in CP1
            if session["cp_input_count"] >= 3:
                checkpoint = 2
                session["current_checkpoint"] = checkpoint
                auto_advanced = True

        # Also handle explicit advancement signals (e.g. user says "go ahead", "confirmed")
        # Note: checkpoint markers are stripped before storage, so we skip the marker check
        if not auto_advanced and user_wants_to_advance(message) and len(session["messages"]) >= 2 and checkpoint < 7:
            checkpoint += 1
            session["current_checkpoint"] = checkpoint

        # Set validation UI flags based on FINAL checkpoint — never show validation UI if we've advanced past CP2
        if checkpoint == 2:
            validation_ui = True
            can_go_back = True

    # Build system prompt
    system_prompt = None
    if skill == "discovery":
        system_prompt = build_discovery_system_prompt(checkpoint)

    # Build contextual prompt from conversation history
    history = "\n\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in session["messages"][-6:]  # Last 6 messages for context
    )

    # If auto-advancing to CP2, append trigger message
    if auto_advanced:
        history += "\n\nUser: Synthesize a confirmed problem statement from our discussion. Do NOT proceed to any other phase."

    # Run Kimi
    assistant_reply = run_kimi(history, skill=skill, system_prompt=system_prompt)

    # Strip checkpoint markers from response for cleaner UI
    assistant_reply = strip_checkpoint_markers(assistant_reply)

    # Intelligence: if Kimi spontaneously output a problem statement during synthesis,
    # ensure we present it in the validation UI regardless of prior checkpoint state.
    # Only trigger for CP1/CP2 — never re-show validation UI once user has advanced past CP2.
    if skill == "discovery" and checkpoint <= 2 and response_contains_problem_statement(assistant_reply):
        if checkpoint < 2:
            checkpoint = 2
            session["current_checkpoint"] = checkpoint
        validation_ui = True
        can_go_back = True

    assistant_phase = detect_phase(assistant_reply, skill)
    current_phase = max(user_phase, assistant_phase, session["current_phase"])
    session["current_phase"] = current_phase

    # Store assistant message
    session["messages"].append({
        "role": "assistant",
        "content": assistant_reply,
        "timestamp": datetime.now().isoformat(),
        "phase": current_phase,
    })

    return jsonify({
        "response": assistant_reply,
        "session_id": session_id,
        "current_phase": current_phase,
        "current_checkpoint": checkpoint,
        "phase_name": next((p["name"] for p in phases if p["id"] == current_phase), "Unknown"),
        "skill": skill,
        "can_advance": skill == "discovery" and checkpoint < 7 and not validation_ui,
        "validation_ui": validation_ui,
        "can_go_back": can_go_back,
    })


@app.route("/api/advance-checkpoint", methods=["POST"])
def advance_checkpoint():
    """Explicitly advance to the next discovery checkpoint and get Kimi's response."""
    data = request.get_json(force=True) or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    with sessions_lock:
        session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    if session.get("skill") != "discovery":
        return jsonify({"error": "Checkpoint advancement only for discovery skill"}), 400

    current_cp = session.get("current_checkpoint", 1)
    if current_cp >= 7:
        return jsonify({"error": "Already at final checkpoint"}), 400

    next_cp = current_cp + 1
    session["current_checkpoint"] = next_cp

    # Trigger messages to tell Kimi what to do at the new checkpoint
    trigger_messages = {
        2: "The user has confirmed their answers and wants to proceed. Please synthesize a confirmed problem statement.",
        3: "The user has confirmed the problem statement and wants to proceed. Please perform JTBD analysis.",
        4: "The user has validated the JTBD analysis and wants to proceed. Please map the competitive landscape.",
        5: "The user has confirmed the competitive landscape and wants to proceed. Please define success metrics.",
        6: "The user has confirmed the success metrics and wants to proceed. Please create a user journey map.",
        7: "The user has confirmed the user journey map and wants to proceed. Please produce the final discovery summary.",
    }
    trigger = trigger_messages.get(next_cp, "Please proceed to the next checkpoint.")

    # Build history including the trigger as a synthetic user message
    history = "\n\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in session["messages"][-6:]
    )
    history += f"\n\nUser: {trigger}"

    system_prompt = build_discovery_system_prompt(next_cp)
    assistant_reply = run_kimi(history, skill="discovery", system_prompt=system_prompt)

    assistant_reply = strip_checkpoint_markers(assistant_reply)

    assistant_phase = detect_phase(assistant_reply, "discovery")
    current_phase = max(assistant_phase, session["current_phase"])
    session["current_phase"] = current_phase

    # Store assistant message
    session["messages"].append({
        "role": "assistant",
        "content": assistant_reply,
        "timestamp": datetime.now().isoformat(),
        "phase": current_phase,
    })

    validation_ui = next_cp == 2
    can_go_back = next_cp == 2

    return jsonify({
        "response": assistant_reply,
        "session_id": session_id,
        "current_phase": current_phase,
        "current_checkpoint": next_cp,
        "phase_name": next((p["name"] for p in DISCOVERY_PHASES if p["id"] == current_phase), "Unknown"),
        "skill": "discovery",
        "can_advance": next_cp < 7 and not validation_ui,
        "validation_ui": validation_ui,
        "can_go_back": can_go_back,
    })


@app.route("/api/go-back-checkpoint", methods=["POST"])
def go_back_checkpoint():
    """Go back from CP2 to CP1 to allow adding more context."""
    data = request.get_json(force=True) or {}
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    with sessions_lock:
        session = sessions.get(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        if session.get("skill") != "discovery":
            return jsonify({"error": "Checkpoint navigation only for discovery skill"}), 400

        current_cp = session.get("current_checkpoint", 1)
        if current_cp != 2:
            return jsonify({"error": "Can only go back from checkpoint 2"}), 400

        session["current_checkpoint"] = 1
        session["cp_input_count"] = max(0, session.get("cp_input_count", 3) - 1)

    # Build history and ask Kimi to continue probing with the added context
    history = "\n\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in session["messages"][-6:]
    )
    history += "\n\nUser: I have more context to add. Please ask additional probing questions before we synthesize the problem statement."

    system_prompt = build_discovery_system_prompt(1)
    assistant_reply = run_kimi(history, skill="discovery", system_prompt=system_prompt)
    assistant_reply = strip_checkpoint_markers(assistant_reply)

    assistant_phase = detect_phase(assistant_reply, "discovery")
    current_phase = max(assistant_phase, session["current_phase"])
    session["current_phase"] = current_phase

    session["messages"].append({
        "role": "assistant",
        "content": assistant_reply,
        "timestamp": datetime.now().isoformat(),
        "phase": current_phase,
    })

    return jsonify({
        "response": assistant_reply,
        "session_id": session_id,
        "current_phase": current_phase,
        "current_checkpoint": 1,
        "phase_name": next((p["name"] for p in DISCOVERY_PHASES if p["id"] == current_phase), "Unknown"),
        "skill": "discovery",
        "can_advance": False,
        "validation_ui": False,
        "can_go_back": False,
    })


@app.route("/api/session/<session_id>", methods=["GET"])
def get_session(session_id):
    with sessions_lock:
        session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session)


@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    with sessions_lock:
        session_list = [
            {
                "id": s["id"],
                "created_at": s["created_at"],
                "message_count": len(s["messages"]),
                "current_phase": s["current_phase"],
                "current_checkpoint": s.get("current_checkpoint", 1),
                "phase_name": next((p["name"] for p in (DISCOVERY_PHASES if s.get("skill") == "discovery" else SOLUTION_PHASES) if p["id"] == s["current_phase"]), "Unknown"),
                "skill": s.get("skill", "discovery"),
            }
            for s in sessions.values()
        ]
    return jsonify(session_list)


@app.route("/api/export/<session_id>", methods=["GET"])
def export_session(session_id):
    with sessions_lock:
        session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    skill = session.get("skill", "discovery")
    phases = DISCOVERY_PHASES if skill == "discovery" else SOLUTION_PHASES

    lines = ["# Product Discovery Session\n"]
    lines.append(f"**Session ID:** {session['id']}  ")
    lines.append(f"**Created:** {session['created_at']}  ")
    lines.append(f"**Current Phase:** {next((p['name'] for p in phases if p['id'] == session['current_phase']), 'Unknown')}\n")
    lines.append("---\n")

    for msg in session["messages"]:
        role = "🧑 User" if msg["role"] == "user" else "🤖 Assistant"
        phase = next((p["name"] for p in phases if p["id"] == msg.get("phase", 1)), "")
        lines.append(f"## {role} (Phase: {phase})\n")
        lines.append(f"{msg['content']}\n")

    markdown = "\n".join(lines)
    return Response(
        markdown,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=discovery-{session_id}.md"},
    )


@app.route("/api/delete/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    with sessions_lock:
        if session_id in sessions:
            del sessions[session_id]
            return jsonify({"success": True})
    return jsonify({"error": "Session not found"}), 404


# ── Discovery Save & Report Routes ─────────────────────────────────────────

@app.route("/api/save-discovery", methods=["POST"])
def save_discovery():
    data = request.get_json(force=True) or {}
    session_id = data.get("session_id")
    problem_name = (data.get("problem_name") or "untitled-discovery").strip()

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    with sessions_lock:
        session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    try:
        folder_path = create_discovery_folder(problem_name)
        folder_name = os.path.basename(folder_path)

        skill = session.get("skill", "discovery")
        phases = DISCOVERY_PHASES if skill == "discovery" else SOLUTION_PHASES
        save_fn = save_discovery_phase if skill == "discovery" else save_solution_phase
        save_summary_fn = save_discovery_summary if skill == "discovery" else save_solution_summary
        label = "Product Discovery" if skill == "discovery" else "Solution Architecture"
        dir_label = "Discovery/_result" if skill == "discovery" else "Solutions/_result"

        phase_content = {p["id"]: [] for p in phases}
        current_summary_lines = [f"# {label} Summary\n"]

        for msg in session["messages"]:
            phase = msg.get("phase", 1)
            if msg["role"] == "assistant":
                phase_content[phase].append(msg["content"])

        for phase in phases:
            pid = phase["id"]
            if phase_content[pid]:
                content = f"# {phase['name']}\n\n" + "\n\n".join(phase_content[pid])
                save_fn(folder_path, pid, phase["name"], content)
                current_summary_lines.append(f"\n## {phase['name']}\n")
                current_summary_lines.append("\n\n".join(phase_content[pid]))

        summary_content = "\n".join(current_summary_lines)
        save_summary_fn(folder_path, summary_content)

        return jsonify({
            "success": True,
            "folder": folder_name,
            "folder_path": folder_path,
            "message": f"{label} saved to {dir_label}/{folder_name}/",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-report/<folder>", methods=["POST"])
def generate_discovery_report(folder):
    folder = os.path.basename(folder)
    folder_path = os.path.join(DISCOVERIES_DIR, folder)
    if not os.path.exists(folder_path):
        return jsonify({"error": f"Folder not found: {folder}"}), 404

    try:
        report_path = generate_report(folder_path)
        return jsonify({
            "success": True,
            "report_path": report_path,
            "report_url": f"/Discovery/_result/{folder}/index.html",
            "message": "Report generated successfully",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/discoveries", methods=["GET"])
def get_discoveries():
    return jsonify(list_discovery_folders())


@app.route("/api/solutions", methods=["GET"])
def get_solutions():
    return jsonify(list_solution_folders())


@app.route("/api/save-solution", methods=["POST"])
def save_solution():
    data = request.get_json(force=True) or {}
    session_id = data.get("session_id")
    problem_name = (data.get("problem_name") or "untitled-solution").strip()

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    with sessions_lock:
        session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    try:
        folder_path = create_solution_folder(problem_name)
        folder_name = os.path.basename(folder_path)

        phases = SOLUTION_PHASES
        save_fn = save_solution_phase
        save_summary_fn = save_solution_summary

        phase_content = {p["id"]: [] for p in phases}
        current_summary_lines = ["# Solution Architecture Summary\n"]

        for msg in session["messages"]:
            phase = msg.get("phase", 1)
            if msg["role"] == "assistant":
                phase_content[phase].append(msg["content"])

        for phase in phases:
            pid = phase["id"]
            if phase_content[pid]:
                content = f"# {phase['name']}\n\n" + "\n\n".join(phase_content[pid])
                save_fn(folder_path, pid, phase["name"], content)
                current_summary_lines.append(f"\n## {phase['name']}\n")
                current_summary_lines.append("\n\n".join(phase_content[pid]))

        summary_content = "\n".join(current_summary_lines)
        save_summary_fn(folder_path, summary_content)

        return jsonify({
            "success": True,
            "folder": folder_name,
            "folder_path": folder_path,
            "message": f"Solution saved to Solutions/_result/{folder_name}/",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-solution-report/<folder>", methods=["POST"])
def generate_solution_report(folder):
    folder = os.path.basename(folder)
    folder_path = os.path.join(SOLUTIONS_DIR, folder)
    if not os.path.exists(folder_path):
        return jsonify({"error": f"Folder not found: {folder}"}), 404

    try:
        report_path = generate_report(folder_path)
        return jsonify({
            "success": True,
            "report_path": report_path,
            "report_url": f"/Solutions/_result/{folder}/index.html",
            "message": "Report generated successfully",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/Solutions/_result/<path:filename>")
def serve_solution(filename):
    safe_path = os.path.normpath(os.path.join(SOLUTIONS_DIR, filename))
    if not safe_path.startswith(os.path.normpath(SOLUTIONS_DIR)):
        return jsonify({"error": "Invalid path"}), 403
    return send_from_directory(SOLUTIONS_DIR, filename)


@app.route("/Discovery/_result/<path:filename>")
def serve_discovery(filename):
    safe_path = os.path.normpath(os.path.join(DISCOVERIES_DIR, filename))
    if not safe_path.startswith(os.path.normpath(DISCOVERIES_DIR)):
        return jsonify({"error": "Invalid path"}), 403
    return send_from_directory(DISCOVERIES_DIR, filename)


# ── PDF Upload ─────────────────────────────────────────────────────────────

@app.route("/api/upload-solution-pdf", methods=["POST"])
def upload_solution_pdf():
    """Accept a PDF upload, extract text, and return it."""
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400

    pdf_file = request.files["pdf"]
    if pdf_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not pdf_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "File must be a PDF"}), 400

    # Save temporarily
    temp_dir = os.path.join(PROJECT_ROOT, ".tmp")
    os.makedirs(temp_dir, exist_ok=True)
    filename = secure_filename(pdf_file.filename)
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{filename}")

    try:
        pdf_file.save(temp_path)

        # Extract text
        extracted_text = ""
        if HAS_PYPDF2:
            try:
                with open(temp_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += page_text + "\n"
            except Exception as e:
                return jsonify({"error": f"Failed to extract PDF text: {str(e)}"}), 500
        else:
            return jsonify({"error": "PyPDF2 is not installed"}), 500

        # Truncate if extremely long
        if len(extracted_text) > 30000:
            extracted_text = extracted_text[:30000] + "\n\n[Content truncated due to length]"

        return jsonify({"success": True, "text": extracted_text.strip(), "filename": filename})
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


# ── Material Ingestion ─────────────────────────────────────────────────────

def _extract_pdf_text_from_dir(directory: str, max_chars: int = 50000) -> str:
    """Extract text from all PDFs in a directory, up to max_chars total."""
    global ingestion_state
    if not HAS_PYPDF2 or not os.path.isdir(directory):
        return ""
    texts = []
    total = 0
    for filename in sorted(os.listdir(directory)):
        if not filename.lower().endswith(".pdf"):
            continue
        with ingestion_lock:
            ingestion_state["current_file"] = filename
            ingestion_state["stage"] = "extracting"
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    if page_text:
                        texts.append(f"--- {filename} ---\n{page_text}")
                        total += len(page_text)
                        if total >= max_chars:
                            break
        except Exception:
            continue
        if total >= max_chars:
            break
    return "\n\n".join(texts)


def _generate_summary(skill: str, raw_text: str) -> str:
    """Call Kimi to summarize extracted reference material text into a summary.md."""
    if skill == "discovery":
        prompt = (
            "You are a Product Discovery Manager. I've extracted text from reference materials on "
            "product discovery frameworks (Cagan's INSPIRED, Product Model First Principles, "
            "Jobs-to-be-Done, User Journey Mapping).\n\n"
            "Write a concise, structured markdown summary that serves as a quick-reference guide for "
            "conducting product discovery sessions. Include:\n"
            "1. Core principles from each framework (2-3 sentences each)\n"
            "2. Phase-by-phase checklist with key questions to ask\n"
            "3. Common templates (problem statement format, JTBD format, journey map columns)\n"
            "4. Decision criteria for moving between phases\n\n"
            "Keep it under 2000 words. Use markdown headers and bullet points.\n\n"
            "--- EXTRACTED MATERIAL TEXT ---\n"
            + raw_text[:40000]
        )
    else:
        prompt = (
            "You are a Solution Architect. I've extracted text from reference materials on "
            "solution architecture (Opportunity Solution Trees, RICE Prioritization, T-Shirt Sizing).\n\n"
            "Write a concise, structured markdown summary that serves as a quick-reference guide. Include:\n"
            "1. Core principles for each framework\n"
            "2. Step-by-step process for each phase\n"
            "3. Common templates and scoring criteria\n"
            "4. Decision criteria for recommending solutions\n\n"
            "Keep it under 1500 words. Use markdown headers and bullet points.\n\n"
            "--- EXTRACTED MATERIAL TEXT ---\n"
            + raw_text[:40000]
        )

    system = (
        "You are a technical writer creating a concise reference guide. "
        "Distill the key frameworks, templates, and decision criteria into a well-structured markdown document. "
        "Preserve the most actionable content while removing verbose explanations."
    )
    return run_kimi(prompt, skill=skill, system_prompt=system, timeout=600)


def _run_ingestion(skill: str):
    """Background thread: extract PDF text and generate summary.md for one skill."""
    global ingestion_state
    try:
        if skill == "discovery":
            dirs = [
                os.path.join(PROJECT_ROOT, "_context"),
                os.path.join(PROJECT_ROOT, "Discovery", "_context"),
            ]
            path = DISCOVERY_SUMMARY_PATH
        else:
            dirs = [
                os.path.join(PROJECT_ROOT, "_context"),
                os.path.join(PROJECT_ROOT, "Solutions", "_context"),
            ]
            path = SOLUTION_SUMMARY_PATH

        raw_text = "\n\n".join(_extract_pdf_text_from_dir(d) for d in dirs)
        if raw_text:
            with ingestion_lock:
                ingestion_state["current_file"] = None
                ingestion_state["stage"] = "summarizing"
            summary = _generate_summary(skill, raw_text)
            with open(path, "w", encoding="utf-8") as f:
                f.write(summary)
            # Safety net: if Kimi CLI wrote a summary.md to the work dir (project root), delete it
            root_summary = os.path.join(PROJECT_ROOT, "summary.md")
            if os.path.exists(root_summary):
                try:
                    os.remove(root_summary)
                except Exception:
                    pass
    except Exception as e:
        print(f"[Ingestion Error] {e}")
    finally:
        with ingestion_lock:
            ingestion_state["in_progress"] = False
            ingestion_state["skill"] = None
            ingestion_state["current_file"] = None
            ingestion_state["stage"] = "idle"


@app.route("/api/ingest-status", methods=["GET"])
def ingest_status():
    """Check whether reference material summaries have been generated."""
    discovery_done = os.path.exists(DISCOVERY_SUMMARY_PATH)
    solution_done = os.path.exists(SOLUTION_SUMMARY_PATH)
    with ingestion_lock:
        state = dict(ingestion_state)
    return jsonify({
        "discovery_ingested": discovery_done,
        "solution_ingested": solution_done,
        "all_ingested": discovery_done and solution_done,
        "in_progress": state["in_progress"],
        "current_file": state["current_file"],
        "stage": state["stage"],
        "skill": state["skill"],
    })


@app.route("/api/ingest-materials", methods=["POST"])
def ingest_materials():
    """Trigger background ingestion of reference materials into summary.md files."""
    global ingestion_state
    data = request.get_json(force=True) or {}
    skill = data.get("skill", "discovery")
    if skill not in ("discovery", "solution"):
        return jsonify({"error": "skill must be 'discovery' or 'solution'"}), 400

    with ingestion_lock:
        if ingestion_state["in_progress"]:
            return jsonify({"status": "already_in_progress", "skill": ingestion_state["skill"]})
        ingestion_state["in_progress"] = True
        ingestion_state["skill"] = skill
        ingestion_state["current_file"] = None
        ingestion_state["stage"] = "idle"

    thread = Thread(target=_run_ingestion, args=(skill,), daemon=True)
    thread.start()
    return jsonify({"status": "started", "skill": skill})


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"=" * 60)
    print("Product Discovery Manager + Solution Architect - Web Interface")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Kimi CLI:     {KIMI_BIN}")
    print(f"=" * 60)
    print("Open http://localhost:5050 in your browser")
    print("Press Ctrl+C to stop")
    print(f"=" * 60)
    app.run(host="0.0.0.0", port=5050, debug=False)
