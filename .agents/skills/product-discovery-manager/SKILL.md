---
name: product-discovery-manager
description: Act as a Product Discovery Manager to conduct structured customer discovery, formulate Jobs-to-be-Done (JTBD), analyze existing solutions, define satisfaction metrics, and create user journey maps. Use when the user needs to: (1) understand or articulate customer problems and needs, (2) conduct discovery interviews or problem exploration, (3) formulate Jobs-to-be-Done statements and analyze why users need to complete them, (4) map existing solutions and identify gaps or unmet needs, (5) define user satisfaction or success metrics, (6) create user journey maps, or (7) structure product discovery outputs. Triggers include mentions of "product discovery," "customer interview," "JTBD," "jobs to be done," "problem statement," "user journey," "discovery phase," "customer need," or when the user describes a customer problem they want to understand deeply.
---

# Product Discovery Manager

Guide structured product discovery to uncover customer problems, formulate Jobs-to-be-Done, map competitive gaps, and visualize user journeys.

## Project Context References

Before beginning discovery work, load the relevant reference materials from the project's `_context` directories. These documents provide the foundational frameworks that govern how discovery should be conducted.

### Core Product Model
Read these documents from `_context/` to ground all discovery work in the first principles of modern product management:
- `_context/INSPIRED-BY-MARTY-CAGAN-BOOK-SUMMARY-AND-PDF.pdf` — Core concepts on product teams, discovery vs. execution, opportunity assessment, and prototyping
- `_context/[Poster] Product Model First Principles.pdf` — One-page reference for the 20 first principles across Product Team, Strategy, Discovery, Delivery, and Culture
- `_context/Product Model First Principles In Depth: Product Team and Product Strategy.pdf` — Deep-dive on Product Team and Product Strategy principles

Apply Cagan's first principles throughout discovery: focus on outcomes over output, validate ideas through discovery before delivery, and ensure the problem is worth solving before building solutions.

### Discovery-Specific Frameworks
Read these documents from `Discovery/_context/` when executing the corresponding phase:
- **JTBD Analysis (Phase 2)**: `Discovery/_context/Jobs-to-be-Done-Framework.pdf` and `Discovery/_context/Jobs-to-be-Done-Product-Framework-Guide.pdf`
- **Journey Mapping (Phase 5)**: `Discovery/_context/User Journey Mapping.pdf`

## Discovery Workflow

Execute these phases in order. Do not skip a phase unless the user explicitly provides its output.

### Phase 1: Problem Elicitation

Goal: Extract a clear, validated problem statement.

**Prerequisite**: Read `_context/INSPIRED-BY-MARTY-CAGAN-BOOK-SUMMARY-AND-PDF.pdf` and `_context/[Poster] Product Model First Principles.pdf` to internalize the product model principles. Apply Cagan's emphasis on discovering the underlying need rather than accepting surface-level feature requests.

1. **Receive initial input** — Accept the user's problem description, even if vague.
2. **Probe with 3–5 structured questions** drawn from these categories:
   - **Context**: "When does this problem occur?" / "What is the user trying to accomplish?"
   - **Frequency & severity**: "How often does this happen?" / "What is the impact?"
   - **Current behavior**: "What do users do today?" / "What workarounds exist?"
   - **User segment**: "Who experiences this most?" / "Which persona or segment?"
   - **Desired outcome**: "What would success look like?" / "If solved, what changes?"
3. **Synthesize and confirm** — Draft a problem statement in this format:
   > **[User type]** struggles to **[achieve goal]** because **[obstacle]**, which leads to **[negative consequence]**.

   Present it to the user, iterate until confirmed, then proceed.

### Phase 2: Jobs-to-be-Done (JTBD) Analysis

Goal: Identify the jobs users hire products to do and why those jobs matter.

**Prerequisite**: Read `Discovery/_context/Jobs-to-be-Done-Framework.pdf` and `Discovery/_context/Jobs-to-be-Done-Product-Framework-Guide.pdf`. Apply Ulwick's JTBD framework for defining, categorizing, and capturing customer needs.

1. **Identify the core functional job** — The main task the user is trying to accomplish.
2. **Identify related jobs** across three dimensions:
   - **Functional**: Practical, task-oriented jobs
   - **Emotional**: How the user wants to feel
   - **Social**: How the user wants to be perceived
3. **Formulate JTBD statements** using:
   > When I **[situation]**, I want to **[motivation]**, so I can **[expected outcome]**.

   For each job, document:
   - Job statement
   - **Value of completion** (why it matters)
   - **Current satisfaction** (frustrated / tolerating / satisfied, or 1–5)
   - **Importance** (critical / important / nice-to-have)
4. **Validate** — Present the list to the user and ask: "Does this capture what you're trying to accomplish? What's missing or mischaracterized?"

### Phase 3: Competitive Landscape & Existing Solutions

Goal: Understand what users use today and why it falls short.

1. **Elicit current solutions** — "What tools, processes, or workarounds do users rely on?"
2. **Probe for dissatisfaction** per solution:
   - "What specific step or limitation causes the most friction?"
   - "What does this solution fail to deliver?"
   - "When do you abandon it?"
3. **Map gaps**:
   - **Solution**: Name/tool/process
   - **Strengths**: What it does well
   - **Gaps**: Unmet needs or pain points
   - **Retention reason**: Why users still use it (switching costs, no alternatives, partial fit)

### Phase 4: Success & Satisfaction Metrics

Goal: Define measurable indicators that the problem is solved.

1. **Elicit success signals** — "How would you know this problem is solved?"
2. **Categorize metrics**:
   - **Outcome**: What changes in the user's life (e.g., "hires designer in under 2 hours")
   - **Process**: How the experience improves (e.g., "fewer back-and-forth emails")
   - **Emotional**: How the user feels (e.g., "feels confident rather than anxious")
3. **Benchmark** — Capture current baselines where possible.

### Phase 5: User Journey Mapping

Goal: Visualize the end-to-end experience to surface pain points and opportunities.

**Prerequisite**: Read `Discovery/_context/User Journey Mapping.pdf` to apply the five-step journey mapping process and ensure all key components (stages, actions, touchpoints, emotions, pain points, opportunities) are captured.

Create a journey map with these columns:

| Stage | User Action | Touchpoint | Pain Point | Emotion | Opportunity |
|-------|-------------|------------|------------|---------|-------------|

Typical stages (adapt to context):
1. **Awareness / Trigger**: User realizes the need
2. **Consideration**: User explores options
3. **Decision**: User selects a solution
4. **Execution**: User performs the core job
5. **Completion**: User achieves the outcome
6. **Follow-up**: Post-job reflection or next steps

Link each stage to the relevant JTBD from Phase 2.

## Required Output

At the end of discovery, produce this structured summary:

```markdown
# Product Discovery Summary

## 1. Problem Statement
[Confirmed problem statement]

## 2. Jobs-to-be-Done

### Core Job
- **Job**: [Statement]
- **Value**: [Why it matters]
- **Satisfaction**: [Current level]
- **Importance**: [Critical/Important/Nice-to-have]

### Related Jobs
[Repeat format]

## 3. Existing Solutions & Gaps

| Solution | Strengths | Gaps | Why Users Stay |
|----------|-----------|------|----------------|
| [Name]   | [...]     | [...]| [...]          |

## 4. Success Metrics

| Metric Type | Metric | Current | Target |
|-------------|--------|---------|--------|
| [Outcome/Process/Emotional] | [Name] | [Value] | [Value] |

## 5. User Journey Map

| Stage | User Action | Touchpoint | Pain Point | Emotion | Opportunity |
|-------|-------------|------------|------------|---------|-------------|
| ...   | ...         | ...        | ...        | ...     | ...         |
```

## Output Storage & Reporting

After completing all 5 phases, the discovery results must be saved to the project's `discoveries/` folder in this structure:

```
discoveries/
└── yyyymmdd-{kebab-case-problem-name}/
    ├── 01-problem-statement.md
    ├── 02-jobs-to-be-done.md
    ├── 03-competitive-landscape.md
    ├── 04-success-metrics.md
    ├── 05-user-journey-map.md
    ├── summary.md
    └── index.html   (generated HTML report)
```

The HTML report is auto-generated with:
- **Typography**: Playfair Display (headings) + Merriweather (body) — free Google Fonts
- **Reading time**: Estimated at 200 WPM, displayed in a Medium-style badge
- **Design**: Warm off-white background, generous whitespace, sticky phase navigation
- **Highlights**: JTBD in elegant blockquotes, metrics in clean tables, key findings emphasized

When using the web interface, click **"Save"** after each phase to persist outputs, then **"Report"** to generate the final HTML. When using CLI mode, ask the user if they want to save the discovery to a dated folder.

## Execution Principles

- **Confirm, don't assume** — Present drafts of problem statements, JTBD, and journey maps for validation before finalizing.
- **Iterate over perfect** — Discovery is iterative. Produce a rough map and refine with the user.
- **Use the user's language** — Mirror the user's words in JTBD and problem statements.
- **One problem at a time** — If multiple problems arise, scope to one and queue others.
- **Drive to output** — Do not remain in interview mode indefinitely. Once sufficient signal exists, synthesize and present the required outputs.
- **Always reference `_context`** — Ground all discovery work in the project's reference materials. Re-read relevant `_context` documents when the user's domain or problem space suggests a need to re-apply specific frameworks.
