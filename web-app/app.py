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

from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from flask_cors import CORS

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
# Default path matches standard macOS Kimi Code CLI install location.
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

# ── Helpers ────────────────────────────────────────────────────────────────

def detect_phase(text: str, skill: str = "discovery") -> int:
    """Auto-detect which phase a message belongs to."""
    phases = DISCOVERY_PHASES if skill == "discovery" else SOLUTION_PHASES
    text_lower = text.lower()
    for phase in reversed(phases):  # Check later phases first (more specific)
        for kw in phase["keywords"]:
            if kw in text_lower:
                return phase["id"]
    return 1  # Default to Phase 1


def build_discovery_system_prompt() -> str:
    """Build the discovery skill-triggering system prompt."""
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


def build_solution_system_prompt() -> str:
    """Build the solution architect skill-triggering system prompt."""
    return (
        "You are a Solution Architect — a senior software engineer adept in various tech stacks, "
        "including no/low code solutions. Your objective is to find the quickest, easiest solution "
        "with as little friction as possible for non-tech-savvy users.\n\n"
        "You follow the structured solution workflow defined in the solution-architect skill. "
        "Ground all your work in the project's reference materials: read Solutions/_context/ for "
        "Opportunity Solution Trees, RICE Prioritization Framework, and T-Shirt Sizing guidance.\n\n"
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


def run_kimi(prompt: str, skill: str = "discovery", work_dir: str = DEFAULT_WORK_DIR, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Invoke Kimi CLI in non-interactive print mode."""
    if skill == "solution":
        system_prompt = build_solution_system_prompt()
    else:
        system_prompt = build_discovery_system_prompt()
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

    # Build contextual prompt from conversation history
    history = "\n\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in session["messages"][-6:]  # Last 6 messages for context
    )

    # Run Kimi
    assistant_reply = run_kimi(history, skill=skill)
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
        "phase_name": next((p["name"] for p in phases if p["id"] == current_phase), "Unknown"),
        "skill": skill,
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


# ── Discovery Save & Report Routes ─────────────────────────────────────────

@app.route("/api/save-discovery", methods=["POST"])
def save_discovery():
    """Save the current session as structured discovery files."""
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
        # Create discovery folder
        folder_path = create_discovery_folder(problem_name)
        folder_name = os.path.basename(folder_path)

        # Extract phase content from messages and save as separate files
        skill = session.get("skill", "discovery")
        phases = DISCOVERY_PHASES if skill == "discovery" else SOLUTION_PHASES
        save_fn = save_discovery_phase if skill == "discovery" else save_solution_phase
        save_summary_fn = save_discovery_summary if skill == "discovery" else save_solution_summary
        label = "Product Discovery" if skill == "discovery" else "Solution Architecture"
        dir_label = "Discovery/discoveries" if skill == "discovery" else "Solutions/solutions"

        phase_content = {p["id"]: [] for p in phases}
        current_summary_lines = [f"# {label} Summary\n"]

        for msg in session["messages"]:
            phase = msg.get("phase", 1)
            if msg["role"] == "assistant":
                phase_content[phase].append(msg["content"])

        # Save each phase
        for phase in phases:
            pid = phase["id"]
            if phase_content[pid]:
                content = f"# {phase['name']}\n\n" + "\n\n".join(phase_content[pid])
                save_fn(folder_path, pid, phase["name"], content)
                current_summary_lines.append(f"\n## {phase['name']}\n")
                current_summary_lines.append("\n\n".join(phase_content[pid]))

        # Save summary
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
    """Generate an HTML report for a discovery folder."""
    # Prevent path traversal
    folder = os.path.basename(folder)
    folder_path = os.path.join(DISCOVERIES_DIR, folder)
    if not os.path.exists(folder_path):
        return jsonify({"error": f"Folder not found: {folder}"}), 404

    try:
        report_path = generate_report(folder_path)
        return jsonify({
            "success": True,
            "report_path": report_path,
            "report_url": f"/Discovery/discoveries/{folder}/index.html",
            "message": "Report generated successfully",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/discoveries", methods=["GET"])
def get_discoveries():
    """List all discovery folders."""
    return jsonify(list_discovery_folders())


@app.route("/api/solutions", methods=["GET"])
def get_solutions():
    """List all solution folders."""
    return jsonify(list_solution_folders())


@app.route("/api/save-solution", methods=["POST"])
def save_solution():
    """Save the current session as structured solution files."""
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
            "message": f"Solution saved to Solutions/solutions/{folder_name}/",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-solution-report/<folder>", methods=["POST"])
def generate_solution_report(folder):
    """Generate an HTML report for a solution folder."""
    folder = os.path.basename(folder)
    folder_path = os.path.join(SOLUTIONS_DIR, folder)
    if not os.path.exists(folder_path):
        return jsonify({"error": f"Folder not found: {folder}"}), 404

    try:
        report_path = generate_report(folder_path)
        return jsonify({
            "success": True,
            "report_path": report_path,
            "report_url": f"/Solutions/solutions/{folder}/index.html",
            "message": "Report generated successfully",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/Solutions/solutions/<path:filename>")
def serve_solution(filename):
    """Serve solution report files."""
    safe_path = os.path.normpath(os.path.join(SOLUTIONS_DIR, filename))
    if not safe_path.startswith(os.path.normpath(SOLUTIONS_DIR)):
        return jsonify({"error": "Invalid path"}), 403
    return send_from_directory(SOLUTIONS_DIR, filename)


@app.route("/Discovery/discoveries/<path:filename>")
def serve_discovery(filename):
    """Serve discovery report files."""
    # Prevent path traversal by ensuring the resolved path stays within DISCOVERIES_DIR
    safe_path = os.path.normpath(os.path.join(DISCOVERIES_DIR, filename))
    if not safe_path.startswith(os.path.normpath(DISCOVERIES_DIR)):
        return jsonify({"error": "Invalid path"}), 403
    return send_from_directory(DISCOVERIES_DIR, filename)


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import subprocess  # noqa: re-import at top-level for module clarity

    print(f"=" * 60)
    print("Product Discovery Manager + Solution Architect - Web Interface")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Kimi CLI:     {KIMI_BIN}")
    print(f"=" * 60)
    print("Open http://localhost:5050 in your browser")
    print("Press Ctrl+C to stop")
    print(f"=" * 60)
    app.run(host="0.0.0.0", port=5050, debug=False)
