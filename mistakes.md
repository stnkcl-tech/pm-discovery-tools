# Mistakes Made & Lessons Learned

> **Read this file before implementing any solution.** Every mistake here cost real user time. Avoid repeating them.

---

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

### Mistake 9: Parsing Checkpoint Markers on Frontend
- **What:** `addMessage()` tried to extract the checkpoint number from assistant message content using `getCheckpointNumber(content)` to decide whether to show a "Proceed" button. But the backend strips checkpoint markers before sending, so the regex always returned `null` and the button never appeared.
- **Fix:** Use the frontend's already-updated `currentCheckpoint` state variable instead of parsing the message text
- **Lesson:** Never rely on parsing display content for UI logic. Use canonical state variables. If the backend strips markers, the frontend cannot depend on them.

### Mistake 10: `go-back-checkpoint` Released Lock Before Mutating Session
- **What:** The `sessions_lock` was acquired only to read the session, then released before modifying `current_checkpoint` and `cp_input_count`. In rapid successive requests this could create a race condition.
- **Fix:** Hold the lock through the read-modify-write of checkpoint state
- **Lesson:** In-memory session mutations that depend on read values must be atomic with the read.

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

### Mistake 14: Explicit Advancement From CP2 Was Dead Code
- **What:** The backend checked `cp_marker in last_assistant` to decide whether to let a user explicitly advance from CP2 via chat message. But checkpoint markers are stripped before messages are stored, so this condition was **never** true. When users typed "go ahead" in CP2, the checkpoint stayed at 2 and Kimi regenerated the problem statement — causing duplication.
- **Fix:** Removed the broken marker check. Now if a user signals confirmation while in CP2, the system unconditionally advances to CP3.
- **Lesson:** Never write guard conditions that depend on data you know is sanitized away elsewhere. If you strip markers for display, you cannot use them for logic.

### Mistake 15: No Fallback Detection for Problem Statement Output
- **What:** The system relied exclusively on `cp_input_count >= 3` to trigger the validation UI. If session state ever drifted (page reload, race condition, or `cp_input_count` miscount), Kimi could output a problem statement but the user would still see it as a regular chat message.
- **Fix:** Added `response_contains_problem_statement()` — a content-based heuristic that detects `struggle` + `because` + (`>` or `**` or confirmation question). This runs on every Kimi response and forces `validation_ui = True` regardless of checkpoint state.
- **Lesson:** For critical UI state transitions, implement defense-in-depth. Never rely on a single signal (like a counter). Always have a content-based fallback.

### Mistake 16: Preamble Regex Was Too Narrow
- **What:** The frontend regex for stripping preambles matched "Here's the problem statement based on our discussion" but missed the variant "Here is the synthesized problem statement:" that Kimi actually generated. The preamble leaked into the validation card.
- **Fix:** Replaced the rigid regex with a broader pattern: `/^(Here's|Here is)\s+(the\s+)?(synthesized\s+)?problem statement[^\n]*\.?\s*[\n\r]+/i`. Also added stripping for "Thank you for the detailed answers…" filler.
- **Lesson:** When sanitizing model output, assume infinite variation in phrasing. Write permissive regexes anchored on keyword groups, not exact strings.

---

*Last updated: 2026-05-06*
