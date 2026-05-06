# AI-PM-Skills Project

> **CRITICAL: At the start of EVERY new session, read `references.md` in the project root first.** It contains the full design history, architecture decisions, known bugs, and mistakes to avoid. Do not make changes without consulting it.

---

## Project Overview

AI-PM-Skills is a **locally-runnable web application** that guides users through structured **Product Discovery** and **Solution Architecture** workflows. It combines PDF reference materials (Marty Cagan's product model, JTBD, User Journey Mapping) with an interactive chat interface powered by the Kimi CLI.

The app has two primary modes:
- **Product Discovery Manager** — 5-phase discovery with 7 checkpoints (Problem Elicitation → JTBD → Competitive Landscape → Success Metrics → User Journey Mapping)
- **Solution Architect** — 8-phase solutioning starting from low-tech/no-code options

---

## Project Structure

```
.
├── _context/                          # Core reference materials (PDFs)
│   ├── INSPIRED-BY-MARTY-CAGAN-BOOK-SUMMARY-AND-PDF.pdf
│   ├── [Poster] Product Model First Principles.pdf
│   └── Product Model First Principles In Depth: Product Team and Product Strategy.pdf
│
├── Discovery/                         # Discovery-phase research materials
│   └── _context/
│       ├── Jobs-to-be-Done-Framework.pdf
│       ├── Jobs-to-be-Done-Product-Framework-Guide.pdf
│       └── User Journey Mapping.pdf
│
├── Solutions/                         # Solution architecture outputs
│   ├── _context/
│   └── _result/                       # Generated solution reports
│
├── Discovery/_result/                 # Generated discovery reports
│
├── web-app/                           # Flask web application
│   ├── static/
│   │   ├── css/style.css              # All UI styling
│   │   └── js/app.js                  # Frontend logic
│   ├── templates/
│   │   └── index.html                 # Main app page
│   ├── venv/                          # Python virtual environment
│   ├── app.py                         # Flask backend, API routes
│   ├── report_generator.py            # Report generation utilities
│   └── requirements.txt               # Python dependencies
│
├── references.md                      # SESSION REFERENCE — READ FIRST
└── AGENTS.md                          # This file
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask, Flask-CORS |
| AI Engine | Kimi CLI (local subprocess calls) |
| PDF Processing | PyPDF2 (text extraction) |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Fonts | Poppins (display), Open Sans (body) |
| Templating | Jinja2 (Flask) |

---

## How to Run

```bash
cd web-app
source venv/bin/activate
python app.py
```

Then open **http://localhost:5050** in your browser.

---

## Key Backend Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Main chat — handles checkpoint counting, auto-advance, validation UI flags |
| `/api/advance-checkpoint` | POST | Explicitly advance to next discovery checkpoint |
| `/api/go-back-checkpoint` | POST | Return from CP2 to CP1 to add more context |
| `/api/upload-solution-pdf` | POST | Accept PDF upload, extract text with PyPDF2 |
| `/api/save-discovery` | POST | Save discovery session to `Discovery/_result/` |
| `/api/save-solution` | POST | Save solution session to `Solutions/_result/` |
| `/api/generate-report/<folder>` | POST | Generate HTML report from saved session |
| `/api/export/<session_id>` | GET | Export session as Markdown |

---

## Design System (Summary)

See `references.md` Section 2 for full details.

- **Palette:** `#C5FFFD` · `#88D9E6` · `#3E7CB1` · `#0A2342` · `#F18F01`
- **Input focus:** Dark blue (`#0A2342`)
- **CTA buttons:** Orange (`#F18F01`)
- **Checkpoint markers** are stripped by backend before display

---

## Development Conventions

1. **Always read `references.md` first** in every new session.
2. **Bump static file versions** in `index.html` query strings (`?v=N`) when changing CSS/JS to bust browser cache.
3. **Background tasks need `timeout=86400`** — the Flask dev server runs indefinitely.
4. **PDF documents** live in `_context/` folders, not at directory roots.
5. **Minimal changes** — follow the existing code style; don't over-engineer.

---

## Session State Structure

```python
{
    "id": "abc123",
    "created_at": "...",
    "messages": [{"role": "user|assistant", "content": "...", "phase": 1}],
    "current_phase": 1,
    "current_checkpoint": 1,
    "cp_input_count": 0,      # Inputs in current checkpoint
    "skill": "discovery|solution"
}
```

---

## Security Considerations

- No secrets or credentials in code.
- All PDFs are publicly available reference materials.
- Flask runs locally only (`localhost:5050`).
- PDF uploads are processed in-memory + temp files; cleaned up after extraction.

---

*Last updated: 2026-05-06*
