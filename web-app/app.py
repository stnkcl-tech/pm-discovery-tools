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
from threading import Lock

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS

# ── Configuration ──────────────────────────────────────────────────────────

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIMI_BIN = (
    "/Users/thagstn/Library/Application Support/Code/User/globalStorage/"
    "moonshot-ai.kimi-code/bin/kimi/kimi"
)
DEFAULT_WORK_DIR = PROJECT_ROOT
DEFAULT_TIMEOUT = 300  # seconds

# ── Flask App ──────────────────────────────────────────────────────────────

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ── In-Memory Session Store ────────────────────────────────────────────────

sessions = {}
sessions_lock = Lock()

PHASES = [
    {"id": 1, "name": "Problem Elicitation", "keywords": ["problem statement", "problem elicitation", "phase 1"]},
    {"id": 2, "name": "JTBD Analysis", "keywords": ["jobs-to-be-done", "jtbd", "jobs to be done", "phase 2"]},
    {"id": 3, "name": "Competitive Landscape", "keywords": ["competitive landscape", "existing solutions", "phase 3"]},
    {"id": 4, "name": "Success Metrics", "keywords": ["success metrics", "satisfaction metrics", "phase 4"]},
    {"id": 5, "name": "User Journey Mapping", "keywords": ["user journey", "journey map", "phase 5"]},
]

# ── Helpers ────────────────────────────────────────────────────────────────

def detect_phase(text: str) -> int:
    """Auto-detect which discovery phase a message belongs to."""
    text_lower = text.lower()
    for phase in reversed(PHASES):  # Check later phases first (more specific)
        for kw in phase["keywords"]:
            if kw in text_lower:
                return phase["id"]
    return 1  # Default to Phase 1


def build_system_prompt() -> str:
    """Build the skill-triggering system prompt."""
    return (
        "You are a Product Discovery Manager. You follow the structured discovery workflow "
        "defined in the product-discovery-manager skill. Ground all your work in the project's "
        "reference materials: read _context/ for core product model principles (Cagan's INSPIRED, "
        "Product Model First Principles) and Discovery/_context/ for JTBD Framework and User Journey "
        "Mapping guidance.\n\n"
        "Your goal is to guide the user through 5 phases:\n"
        "1. Problem Elicitation - validate the problem statement\n"
        "2. Jobs-to-be-Done Analysis - identify core and related jobs\n"
        "3. Competitive Landscape - map existing solutions and gaps\n"
        "4. Success Metrics - define outcome, process, and emotional metrics\n"
        "5. User Journey Mapping - visualize the end-to-end experience\n\n"
        "Ask probing questions, confirm assumptions before finalizing, and iterate rather than "
        "perfecting. Use the user's own language in JTBD and problem statements.\n\n"
        "At the end of discovery, produce a structured summary with: Problem Statement, "
        "Jobs-to-be-Done list, Existing Solutions & Gaps table, Success Metrics table, and "
        "User Journey Map table."
    )


def run_kimi(prompt: str, work_dir: str = DEFAULT_WORK_DIR, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Invoke Kimi CLI in non-interactive print mode."""
    system_prompt = build_system_prompt()
    full_prompt = f"{system_prompt}\n\n---\n\nUser message:\n{prompt}"

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

    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Create or retrieve session
    with sessions_lock:
        if not session_id or session_id not in sessions:
            session_id = str(uuid.uuid4())[:8]
            sessions[session_id] = {
                "id": session_id,
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "current_phase": 1,
            }
        session = sessions[session_id]

    
    # Detect phase from user message
    user_phase = detect_phase(message)

    # Store user message
    session["messages"].append({
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat(),
        "phase": user_phase,
    })

    # Build contextual prompt from conversation history
    history = "\n\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in session["messages"][-6:]  # Last 6 messages for context
    )

    # Run Kimi
    assistant_reply = run_kimi(history)
    assistant_phase = detect_phase(assistant_reply)
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
        "phase_name": next((p["name"] for p in PHASES if p["id"] == current_phase), "Unknown"),
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
                "phase_name": next((p["name"] for p in PHASES if p["id"] == s["current_phase"]), "Unknown"),
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

    # Build a markdown export from the conversation
    lines = ["# Product Discovery Session\n"]
    lines.append(f"**Session ID:** {session['id']}  ")
    lines.append(f"**Created:** {session['created_at']}  ")
    lines.append(f"**Current Phase:** {next((p['name'] for p in PHASES if p['id'] == session['current_phase']), 'Unknown')}\n")
    lines.append("---\n")

    for msg in session["messages"]:
        role = "🧑 User" if msg["role"] == "user" else "🤖 Assistant"
        phase = next((p["name"] for p in PHASES if p["id"] == msg.get("phase", 1)), "")
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


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import subprocess  # noqa: re-import at top-level for module clarity

    print(f"=" * 60)
    print("Product Discovery Manager - Web Interface")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Kimi CLI:     {KIMI_BIN}")
    print(f"=" * 60)
    print("Open http://localhost:5000 in your browser")
    print("Press Ctrl+C to stop")
    print(f"=" * 60)
    app.run(host="0.0.0.0", port=5050, debug=False)
