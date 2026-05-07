# AI-PM-Skills Web App — Session Reference

> **Read this file at the start of every new session.** It contains the full context of what has been built, design decisions, known issues, and architecture notes.
>
> **Also read `mistakes.md` and `design-preferences.md`** before implementing any solution.

---

## 1. What Was Built

### Overview
A **Product Discovery Manager + Solution Architect** web interface (Flask app at `web-app/`) with a clean, minimalist UI inspired by dona.ai. The app guides users through structured product discovery (JTBD, Cagan's principles) and solution architecture workflows powered by Kimi CLI.

### Key Features

#### Landing Page
- Large centered headline: **"What problem are you trying to solve today?"**
- Elegant textarea for problem description
- Example pills for quick inspiration (Discovery mode only)
- **"Help me explore solutions"** toggle switches to Solution Architect mode

#### Sidebar Journey Tracker
- Vertical timeline showing discovery/solution phases
- **Checkpoint sub-steps** nested within Phase 1 (Problem Elicitation):
  - Problem Synthesis (Checkpoint 1)
  - Problem Statement (Checkpoint 2)
- Active step highlighted, completed steps checked

#### Solution Architect Mode
- **PDF upload as primary input** — drag & drop or click to browse
- **"I don't have a PDF, type instead"** toggle reveals text field
- Extracts text via PyPDF2 backend endpoint (`/api/upload-solution-pdf`)

#### Progress Bar
- **Full-width animated progress bar** during Kimi analysis
- **2-decimal precision** percentage for smoother perceived motion
- **Evenly distributed progress curve** — slow 0–30%, steady 30–60%, faster 60–85%, fast finish 85–99.99%. Caps at `99.99%` while waiting
- **Shimmer animation** sweeps across the bar continuously
- **Cycling status text** rotates through messages every 3.5s
- Chat input is **hidden while loading**

#### Auto-Advance & Validation UI (v17)
- **Checkpoint 1 auto-advances to Checkpoint 2 after 3 user inputs**
- **Defense-in-depth problem statement detection:**
  1. Input counter (`cp_input_count >= 3`)
  2. Content heuristic (`response_contains_problem_statement()` — detects `struggle` + `because` + blockquote/bold/confirmation)
  3. Frontend safety net (`looksLikeProblemStatementFn()`)
- **Validation UI card** appears for problem statement review:
  - Styled display box with the proposed statement
  - **Follow-up question** displayed **below** the statement box
  - **Confirm & Proceed** → advances to JTBD Analysis
  - **Edit** → reveals inline textarea pre-filled with the statement
  - **Add more context** → goes back to Checkpoint 1 for additional probing
  - No open chat field during validation
- **Frontend sanitization** strips model-generated preambles (variations of "Here's the synthesized problem statement…" and "Thank you for the detailed answers…")
- **Checkpoint 3–6: "Confirm & Proceed" button** appears after each assistant response
- **Explicit advancement from CP2 works without checkpoint markers** — removed broken `cp_marker in last_assistant` check

#### Material Ingestion
- **Discovery ingestion** runs on first launch (~20s), extracts PDFs from `Discovery/_context/`, generates `Discovery/summary.md`
- **Solution ingestion** deferred until user switches to Solution Architect mode
- Per-file progress hints show only filenames

#### Backend Endpoints
| Endpoint | Purpose |
|----------|---------|
| `POST /api/chat` | Main chat, handles checkpoint counting, auto-advance, validation UI flags, problem statement detection |
| `POST /api/advance-checkpoint` | Explicitly advance to next checkpoint |
| `POST /api/go-back-checkpoint` | Return from CP2 to CP1 for more context |
| `POST /api/upload-solution-pdf` | Accept PDF, extract text with PyPDF2 |
| `GET /api/ingest-status` | Poll ingestion progress |
| `POST /api/ingest-materials` | Trigger material ingestion |
| `GET/POST` (save, export, report, sessions) | Session management |

---

## 2. Design System

### Typography
- **Primary/Display:** `Poppins` — headlines, headers, UI labels, buttons
- **Body:** `Open Sans` — chat messages, descriptions, body text

### Color Palette (Coolors)
| Token | Hex | Usage |
|-------|-----|-------|
| Light Cyan | `#C5FFFD` | Accent tint reference |
| Sky Blue | `#88D9E6` | Mid-tone reference |
| Steel Blue | `#3E7CB1` | Secondary text, success states |
| Deep Navy | `#0A2342` | Primary text, input focus borders |
| Vibrant Orange | `#F18F01` | CTA buttons, accent, active highlights |

### CSS Variables
```css
--bg-base: #F4FBFC;
--bg-surface: #ffffff;
--bg-elevated: #E8F6F8;
--text-primary: #0A2342;
--text-secondary: #3E7CB1;
--text-muted: #6B9DB8;
--accent: #F18F01;
--border-focus: #0A2342;
--focus-soft: rgba(10, 35, 66, 0.08);
```

### Key Rules
- **Input focus = dark blue** (`#0A2342`), not orange
- **Button CTAs = orange** (`#F18F01`)
- Checkpoint markers (`📍 CHECKPOINT N`) are **stripped by backend** before display

---

## 3. Architecture Notes

### Session State (Backend)
Each session tracks:
- `id`, `created_at`, `messages[]`
- `current_phase`, `current_checkpoint`
- `cp_input_count` — user inputs in current checkpoint (for auto-advance)
- `skill` — `"discovery"` or `"solution"`

### Checkpoint Auto-Advance Logic
```
CP1 (Problem Elicitation):
  User Input 1 → Kimi asks probing questions
  User Input 2 → Kimi asks more
  User Input 3 → AUTO-ADVANCE to CP2 (synthesize problem statement)
```
- Backend increments `cp_input_count` per user message in CP1
- At count >= 3: sets checkpoint=2, triggers CP2 synthesis, returns `validation_ui: true`
- **Defense-in-depth:** even if counter fails, `response_contains_problem_statement()` detects problem statement in Kimi output and forces validation UI

### Validation UI Flow
```
1. Backend returns response with validation_ui: true
2. Frontend calls showValidationUI(response)
3. Hides chat-messages + chat-input-area
4. Shows validation-card with parsed problem statement
5. User clicks Confirm → proceedToNextCheckpoint() → CP3
6. User clicks Edit → inline editor appears
7. User clicks Add Context → POST /api/go-back-checkpoint → CP1
```

### Proceed Button Flow (CP3–6)
```
1. Assistant presents checkpoint content (JTBD, Competitive Landscape, etc.)
2. Frontend appends "Confirm & Proceed to [Next Checkpoint]" button
3. User clicks → POST /api/advance-checkpoint → next checkpoint
4. New assistant response appears with next checkpoint's content
```

### Explicit Advancement via Chat (CP2)
```
User in CP2 types "go ahead" / "confirmed" / "proceed"
→ Backend detects advance signal via user_wants_to_advance()
→ No checkpoint-marker check (markers are stripped)
→ Unconditionally advances to CP3
→ Kimi receives CP3 trigger, outputs JTBD analysis
```

---

## 4. File Inventory

| File | Purpose | Last Updated |
|------|---------|--------------|
| `web-app/app.py` | Flask backend, API routes, Kimi CLI integration, problem statement detection | v17: explicit advancement fix, content heuristic |
| `web-app/templates/index.html` | Main page template | v17: cache bust |
| `web-app/static/css/style.css` | All styling | v16: palette, fonts, layout, validation card, progress bar shimmer |
| `web-app/static/js/app.js` | Frontend logic | v17: preamble regex fix, safety net detection, loadSession fallback |
| `web-app/requirements.txt` | Dependencies | Flask, flask-cors, PyPDF2 |
| `mistakes.md` | Living mistake journal — read before implementing | v17: added Mistakes 14–16 |
| `design-preferences.md` | User design preferences — read before designing | v17: added Defense-in-Depth preference |

---

## 5. How to Run

```bash
cd web-app
source venv/bin/activate
python app.py
```

Open **http://localhost:5050**

---

## 6. Open Items / Next Steps

- ~~CP3–7: Add explicit "Proceed" buttons~~ ✅ Done
- ~~Progress bar: eliminate freeze perception~~ ✅ Done
- ~~Progress bar: full width, 2-decimal, even distribution~~ ✅ Done
- ~~Validation UI: strip model preamble, separate follow-up~~ ✅ Done
- ~~Validation UI: auto-detect problem statement, fix explicit advancement~~ ✅ Done (v17)
- Solution Architect mode full journey
- Report generation polish
- Mobile responsiveness review

---

*Last updated: 2026-05-06*
