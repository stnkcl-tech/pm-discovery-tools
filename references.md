# AI-PM-Skills Web App — Session Reference

> **Read this file at the start of every new session.** It contains the full context of what has been built, design decisions, known issues, and mistakes to avoid.

---

## 1. What Was Built Today

### Overview
A **Product Discovery Manager + Solution Architect** web interface (Flask app at `web-app/`) with a clean, minimalist UI inspired by dona.ai. The app guides users through structured product discovery (JTBD, Cagan's principles) and solution architecture workflows powered by Kimi CLI.

### Key Features Implemented

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
- **Full-width animated progress bar** during Kimi analysis (spans entire main content area)
- **2-decimal precision** percentage (e.g., `34.56%`, `78.91%`) for smoother perceived motion
- **Evenly distributed progress curve** — slow 0–50%, steady 50–80%, faster 80–95%, fast finish 95–99.99%. Caps at `99.99%` while waiting so it never sits at `100%` prematurely
- **Shimmer animation** sweeps across the bar continuously so it never appears frozen
- **Cycling status text** rotates through messages ("Synthesizing insights…", "Connecting the dots…", "Almost there…")
- Slim single-line layout (bar + status text + percentage)
- Chat input is **hidden while loading** to prevent mid-query input

#### Auto-Advance & Validation UI
- **Checkpoint 1 auto-advances to Checkpoint 2 after 3 user inputs**
- **Validation UI card** appears for problem statement review:
  - Styled display box with the proposed statement
  - **Follow-up question** (e.g. "Does this accurately capture…") displayed **below** the statement box, not inside it
  - **Confirm & Proceed** → advances to JTBD Analysis
  - **Edit** → reveals inline textarea pre-filled with the statement
  - **Add more context** → goes back to Checkpoint 1 for additional probing
  - No open chat field during validation
- **Frontend sanitization** strips model-generated preambles (e.g. "Here's the problem statement based on our discussion") before rendering in the validation card
- **Checkpoint 3–6: "Confirm & Proceed" button** appears after each assistant response, letting users advance to the next checkpoint with one click

#### Backend Endpoints
| Endpoint | Purpose |
|----------|---------|
| `POST /api/chat` | Main chat, handles checkpoint counting & auto-advance |
| `POST /api/advance-checkpoint` | Explicitly advance to next checkpoint |
| `POST /api/go-back-checkpoint` | Return from CP2 to CP1 for more context |
| `POST /api/upload-solution-pdf` | Accept PDF, extract text with PyPDF2 |
| `GET/POST` (save, export, report) | Existing session management |

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
--border-focus: #0A2342;   /* Dark blue for input focus */
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

---

## 4. Mistakes Made & Lessons

### Mistake 1: Server Timeout
- **What:** Background Flask task timed out after 60s (default)
- **Fix:** Set `timeout=86400` (24 hours) on background Shell tasks
- **Lesson:** Always set long timeouts for dev servers

### Mistake 2: Old Color References Left in CSS
- **What:** Updated palette but missed hardcoded `rgba(194, 94, 58, ...)` in `.btn-primary` shadows and `.message.user .message-avatar` border
- **Fix:** Grepped for all old hex codes and replaced with new orange `#F18F01`
- **Lesson:** After palette changes, grep for every old color value

### Mistake 3: Sidebar Layout Break
- **What:** Checkpoint sub-steps were inserted as a sibling of `.journey-dot` and `.journey-info` inside `.journey-item` (flex row), causing horizontal overlap
- **Fix:** Moved sub-steps inside `.journey-info` so they stack vertically
- **Lesson:** When adding nested UI inside flex containers, ensure it flows within the correct child

### Mistake 4: Validation UI Not Showing (Critical Backend Bug)
- **What:** `validation_ui` was set in `elif checkpoint == 2:` but after auto-advance modified `checkpoint = 2` inside `if checkpoint == 1:`, the `elif` never executed
- **Fix:** Set `validation_ui = True` and `can_go_back = True` inside the auto-advance block
- **Lesson:** Be careful with `if/elif` chains when mutating the condition variable inside the first block

### Mistake 5: Chat Input Visible During Loading
- **What:** Users could type while Kimi was processing because `chatInputArea` wasn't hidden
- **Fix:** Added `chatInputArea.classList.add('hidden')` inside `setLoading(true)`
- **Lesson:** Always disable/hide input during async operations

### Mistake 6: `showLandingInterface` Didn't Reset Validation UI
- **What:** Clicking "Clear" while validation UI was shown left the validation card visible
- **Fix:** Added `validationUi.classList.add('hidden')` in both `showLandingInterface()` and `showChatInterface()`
- **Lesson:** Every view transition must hide ALL other view states

### Mistake 7: `setLoading(false)` Overrode Validation UI Visibility
- **What:** After loading finished, `chatInputArea` was unconditionally shown even when the validation UI was active, letting users type into a chat that should have been disabled
- **Fix:** `setLoading(false)` now only restores `chatInputArea` when both `landingState` is hidden AND `validationUi` is hidden
- **Lesson:** State restoration functions must check ALL view-state preconditions, not just assume "loading done = show input"

### Mistake 8: Progress Bar Froze at 95%
- **What:** The progress interval had no branch for `progress >= 95`, so it stalled there until `finishProgressBar()` snapped it to 100%. Users thought the system hung.
- **Fix:** Added a slow crawl from 95% → 99.9%, plus a CSS shimmer animation and cycling status text to reassure users the system is active
- **Lesson:** Never let a progress indicator sit completely still. If true progress is unknown, use indeterminate animations or very slow crawls combined with motion/activity cues.

### Mistake 11: Progress Bar Stalled at 100% With Rotating Text
- **What:** After fixing the 95% freeze, the bar now crawled to 99.9% but then sat there while the status text kept cycling. Users perceived this as a bug because the bar was "full" but nothing was happening.
- **Fix:** Redesigned the entire progress curve: slow 0–50%, steady 50–80%, faster 80–95%, fast finish 95–99.99%. Cap at `99.99%` (never show `100%` until actually complete). Also added 2-decimal precision and full-width span.
- **Lesson:** Progress bar math matters. A "full" bar with rotating text feels broken. Design the curve so the bar is still visibly moving in the final phase, and never show 100% prematurely.

### Mistake 12: Model-Generated Preamble Leaked Into Validation UI
- **What:** After removing the backend-added preamble ("Here's the problem statement…"), the Kimi model itself started generating the exact same preamble text. `showValidationUI()` displayed it inside the problem statement box because it wasn't being stripped.
- **Fix:** Added frontend sanitization in `showValidationUI()` to strip common preamble patterns before rendering.
- **Lesson:** Sanitization must happen at the display layer, not just the data layer. Models can hallucinate instructional preambles that match the removed backend text.

### Mistake 13: Follow-Up Question Trapped Inside Quoted Box
- **What:** The assistant's follow-up question ("Does this accurately capture…") was rendered inside the same blue-bordered problem statement box, making it look like part of the statement itself.
- **Fix:** Split `showValidationUI()` into statement extraction + follow-up extraction. Added a separate `#validation-follow-up` element below the statement box.
- **Lesson:** Separate content types into distinct visual containers. A question directed at the user should not share the same visual treatment as the content being reviewed.

### Mistake 9: Parsing Checkpoint Markers on Frontend
- **What:** `addMessage()` tried to extract the checkpoint number from assistant message content using `getCheckpointNumber(content)` to decide whether to show a "Proceed" button. But the backend strips checkpoint markers before sending, so the regex always returned `null` and the button never appeared.
- **Fix:** Use the frontend's already-updated `currentCheckpoint` state variable instead of parsing the message text
- **Lesson:** Never rely on parsing display content for UI logic. Use canonical state variables. If the backend strips markers, the frontend cannot depend on them.

### Mistake 10: `go-back-checkpoint` Released Lock Before Mutating Session
- **What:** The `sessions_lock` was acquired only to read the session, then released before modifying `current_checkpoint` and `cp_input_count`. In rapid successive requests this could create a race condition.
- **Fix:** Hold the lock through the read-modify-write of checkpoint state
- **Lesson:** In-memory session mutations that depend on read values must be atomic with the read.

---

## 5. User Design & Approach Preferences

> **Synthesized from feedback across sessions.** Refer to these when making future UI/UX decisions.

### Visual-First Communication
- **Prefer UI elements over text instructions.** Example: "Confirm & Proceed" buttons instead of "just say the word and we'll move forward."
- **Remove redundant text** when a visual design element already communicates the same thing. Example: deleted the "Here's the problem statement based on our discussion" preamble because the styled validation card already made it obvious.
- **Separate content types into distinct visual containers.** A follow-up question should not share the same quoted-box treatment as the content being reviewed.

### One-Click Actions
- Users want **explicit, deterministic buttons** to move forward. Do not rely on natural language as the primary advancement mechanism.
- Every checkpoint validation step should offer a clear CTA to proceed.

### Progress Must Feel Alive
- **Never let progress indicators appear frozen.** If true completion % is unknown, use:
  - Continuous motion (shimmer, animated gradients)
  - Cycling status messages
  - Very slow percentage crawls rather than hard stops
- **Never show 100% before completion.** Cap at `99.99%` while waiting; snap to `100%` only when the response actually arrives.
- **Progress bar math matters.** Design the curve so the bar is still visibly moving in the final phase. A "full" bar with rotating text feels broken.
- Users interpret a stalled progress bar as a crashed system.

### No Hidden / Disabled States
- **Hide input surfaces when they shouldn't be used.** If a validation card is shown, the chat input must be completely hidden (not just visually obscured).
- Chat input visibility must be strictly coupled to the active view state.

### Input Ergonomics
- Textareas must **auto-scroll to keep the cursor visible** when typing multi-line content.
- No text should ever be obscured by its own container.

### Iterative Refinement Mindset
- The user gives **specific, actionable feedback** with screenshots and numbered lists.
- They care about **micro-interactions and edge cases** (e.g., "only after clicking a 3rd time", "2 decimal digits").
- They appreciate minimal, surgical fixes over sweeping redesigns.
- **Sanitization must be defense-in-depth.** Strip at both backend AND frontend display layers.

### Palette & Style Discipline
- Strict adherence to the ocean palette. Input focus = dark blue (`#0A2342`), CTAs = orange (`#F18F01`).
- Clean, minimalist aesthetic inspired by dona.ai. Avoid clutter.

---

## 6. File Inventory

| File | Purpose | Last Updated |
|------|---------|--------------|
| `web-app/app.py` | Flask backend, API routes, Kimi CLI integration | Checkpoint logic, PDF upload, go-back endpoint, preamble removal |
| `web-app/templates/index.html` | Main page template | Progress bar, validation UI, PDF upload zone, version footer |
| `web-app/static/css/style.css` | All styling | Palette, fonts, layout, validation card, progress bar shimmer, full-width bar |
| `web-app/static/js/app.js` | Frontend logic | Auto-advance, validation UI, PDF handling, progress bar, proceed buttons, preamble stripping, follow-up extraction |
| `web-app/requirements.txt` | Dependencies | Flask, flask-cors (PyPDF2 already in venv) |

---

## 7. How to Run

```bash
cd web-app
source venv/bin/activate
python app.py
```

Open **http://localhost:5050**

---

## 8. Open Items / Next Steps (From User)

- ~~CP3–7: Add explicit "Proceed" buttons~~ ✅ Done
- ~~Progress bar: eliminate 95% freeze perception~~ ✅ Done
- ~~Progress bar: full width, 2-decimal, even distribution~~ ✅ Done
- ~~Validation UI: strip model preamble, separate follow-up~~ ✅ Done
- Solution Architect mode full journey
- Report generation polish
- Mobile responsiveness review

---

*Last updated: 2026-05-06*
