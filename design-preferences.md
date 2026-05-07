# User Design & Approach Preferences

> **Synthesized from feedback across sessions.** Refer to these when making future UI/UX decisions.

---

## Visual-First Communication
- **Prefer UI elements over text instructions.** Example: "Confirm & Proceed" buttons instead of "just say the word and we'll move forward."
- **Remove redundant text** when a visual design element already communicates the same thing. Example: deleted the "Here's the problem statement based on our discussion" preamble because the styled validation card already made it obvious.
- **Separate content types into distinct visual containers.** A follow-up question should not share the same quoted-box treatment as the content being reviewed.

## One-Click Actions
- Users want **explicit, deterministic buttons** to move forward. Do not rely on natural language as the primary advancement mechanism.
- Every checkpoint validation step should offer a clear CTA to proceed.

## Progress Must Feel Alive
- **Never let progress indicators appear frozen.** If true completion % is unknown, use:
  - Continuous motion (shimmer, animated gradients)
  - Cycling status messages
  - Very slow percentage crawls rather than hard stops
- **Never show 100% before completion.** Cap at `99.99%` while waiting; snap to `100%` only when the response actually arrives.
- **Progress bar math matters.** Design the curve so the bar is still visibly moving in the final phase. A "full" bar with rotating text feels broken.
- Users interpret a stalled progress bar as a crashed system.

## No Hidden / Disabled States
- **Hide input surfaces when they shouldn't be used.** If a validation card is shown, the chat input must be completely hidden (not just visually obscured).
- Chat input visibility must be strictly coupled to the active view state.

## Input Ergonomics
- Textareas must **auto-scroll to keep the cursor visible** when typing multi-line content.
- No text should ever be obscured by its own container.

## Iterative Refinement Mindset
- The user gives **specific, actionable feedback** with screenshots and numbered lists.
- They care about **micro-interactions and edge cases** (e.g., "only after clicking a 3rd time", "2 decimal digits").
- They appreciate minimal, surgical fixes over sweeping redesigns.
- **Sanitization must be defense-in-depth.** Strip at both backend AND frontend display layers.

## Palette & Style Discipline
- Strict adherence to the ocean palette. Input focus = dark blue (`#0A2342`), CTAs = orange (`#F18F01`).
- Clean, minimalist aesthetic inspired by dona.ai. Avoid clutter.

## Defense-in-Depth for Critical Transitions
- **Never rely on a single signal** for critical UI state transitions.
- Example: the validation UI trigger now uses THREE independent signals:
  1. Input counter (`cp_input_count >= 3`)
  2. Content heuristic (`response_contains_problem_statement()`)
  3. Frontend safety net (`looksLikeProblemStatementFn()`)
- If one layer fails, the next catches it. This is the standard for anything that changes the user's primary view mode.

---

*Last updated: 2026-05-06*
