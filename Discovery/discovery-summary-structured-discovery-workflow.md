# Product Discovery Summary: Structured Discovery Workflow

> **Discovery Context**: This exercise applies the Product Discovery Manager skill to a representative problem space highly relevant to the product management reference materials in this repository. The problem was selected because it directly intersects with the core themes of Marty Cagan's *INSPIRED* (discovery vs. execution, opportunity assessment, empowered product teams), Tony Ulwick's JTBD framework (organizing customer needs), and User Journey Mapping (visualizing the discovery experience).

---

## 1. Problem Statement

> **Product managers at small-to-mid-size teams** struggle to **synthesize scattered customer discovery insights into structured, shareable artifacts** because **existing tools are either too heavy (enterprise research platforms) or too unstructured (docs and spreadsheets)**, which leads to **product decisions based on gut feel rather than validated customer needs**.

### Validation Notes
- **Context**: This problem surfaces after every round of customer interviews, usability tests, or sales call listening sessions.
- **Frequency & Severity**: High frequency (weekly to bi-weekly during active discovery) and high severity — misalignment on customer needs is a primary cause of failed products per the JTBD framework reference.
- **Current Behavior**: PMs paste raw notes into Google Docs, tag quotes in spreadsheets, or screenshot sticky notes from FigJam sessions. Insights live in silos and decay quickly.
- **User Segment**: Product managers and product leads at startups and growth-stage companies without dedicated user researchers.
- **Desired Outcome**: A lightweight, repeatable workflow that turns raw discovery inputs into clear, searchable, shareable artifacts the entire team can trust and act upon.

---

## 2. Jobs-to-be-Done

### Core Job

| Attribute | Detail |
|-----------|--------|
| **Job** | When I finish a round of customer interviews, I want to synthesize raw notes into clear customer needs and opportunities, so I can prioritize what to build with confidence. |
| **Value** | Without synthesis, discovery is just anecdote collection. This job bridges the gap between "talking to customers" and "making evidence-based product decisions" — the central theme of Cagan's product discovery philosophy. |
| **Satisfaction** | Frustrated (2/5) — most PMs cobble together ad-hoc processes that break under scale. |
| **Importance** | Critical — if this job is unmet, the entire discovery investment is wasted. |

### Related Functional Jobs

1. **Organize and retrieve past discovery insights**
   - *Statement*: When I start a new initiative, I want to find relevant insights from past interviews quickly, so I don't have to rediscover what we already know.
   - *Value*: Prevents redundant research, accelerates opportunity assessment.
   - *Satisfaction*: Tolerating (2/5) — past insights are scattered across tools and often lost.
   - *Importance*: Important

2. **Share discovery findings with stakeholders in a compelling format**
   - *Statement*: When I need team or leadership alignment, I want to present discovery insights as a clear narrative with evidence, so stakeholders buy into the problem space.
   - *Value*: Alignment is a prerequisite for empowered teams (Cagan's Product Team principle).
   - *Satisfaction*: Tolerating (2/5) — presentations take hours to build and still face skepticism.
   - *Importance*: Critical

3. **Connect customer needs to specific product initiatives**
   - *Statement*: When I prioritize my roadmap, I want to trace each initiative back to validated customer jobs, so I can defend trade-offs with evidence.
   - *Value*: Enables outcome-over-output thinking and minimizes waste.
   - *Satisfaction*: Frustrated (1/5) — most roadmaps are disconnected from discovery data.
   - *Importance*: Critical

### Emotional Jobs

1. **Feel confident that decisions are grounded in real evidence**
   - *Statement*: When I present a product decision, I want to feel certain it's backed by real customer input, so I don't second-guess myself under challenge.
   - *Value*: Confidence drives decisive leadership, a key PM attribute per *INSPIRED*.
   - *Satisfaction*: Tolerating (2/5)
   - *Importance*: Important

2. **Avoid feeling overwhelmed by scattered, unstructured notes**
   - *Statement*: When I look at my discovery artifacts, I want to feel in control of the information, so I can focus on insight rather than clerical work.
   - *Value*: Cognitive overload reduces discovery quality and causes PM burnout.
   - *Satisfaction*: Frustrated (1/5)
   - *Importance*: Important

3. **Feel credible and prepared when presenting to leadership**
   - *Statement*: When I enter a leadership review, I want to feel prepared with clear evidence, so I can advocate for the customer effectively.
   - *Value*: Credibility unlocks autonomy and resources for the product team.
   - *Satisfaction*: Tolerating (2/5)
   - *Importance*: Important

### Social Jobs

1. **Be perceived as a customer-centric, data-informed product leader**
   - *Statement*: When I collaborate with engineering and design, I want to be seen as the voice of the customer, so my input carries weight in team decisions.
   - *Value*: Social proof reinforces the PM's role as the keeper of customer context.
   - *Satisfaction*: Tolerating (2/5)
   - *Importance*: Important

2. **Demonstrate rigor in discovery to cross-functional teammates**
   - *Statement*: When working with skeptical engineers or stakeholders, I want to demonstrate a structured discovery process, so they trust the inputs to our product bets.
   - *Value*: Trust over control is a Product Culture first principle; rigor builds trust.
   - *Satisfaction*: Tolerating (2/5)
   - *Importance*: Important

---

## 3. Existing Solutions & Gaps

| Solution | Strengths | Gaps | Why Users Stay |
|----------|-----------|------|----------------|
| **Spreadsheets (Excel, Google Sheets)** | Flexible, universally familiar, free, fast to open | No structure for JTBD or job statements; insights become unsearchable tables; no narrative flow; version chaos | Zero friction and no learning curve; team already has access |
| **Docs / Wikis (Notion, Confluence, Google Docs)** | Good for prose narratives; easy to share links; supports images and quotes | Insights get buried in long documents; no tagging or linking to decisions; no reuse mechanism; hard to compare across interviews | Flexibility and rich text; team collaboration habits already formed |
| **Enterprise Research Repositories (Dovetail, EnjoyHQ, Aurelius)** | Structured tagging, transcription, insight clustering, search, permissions | Expensive per-seat pricing; heavy onboarding; overkill for small teams without researchers; steep taxonomy setup; often requires dedicated research ops | When the organization has budget and dedicated UX researchers; high compliance needs |
| **Whiteboarding Tools (Miro, Mural, FigJam)** | Visual, collaborative, excellent for workshop synthesis | Insights are not persistent or searchable; no version control; hard to export into actionable formats; designed for sessions, not repositories | Excellent for real-time group synthesis during discovery workshops |
| **Ad-hoc Note-Taking (Apple Notes, Obsidian, Roam)** | Fast capture, personal knowledge graphs (in some cases), low friction | Not shareable by default; no team alignment; insights stay in the PM's head | Speed of capture during live interviews |

### Key Gap Themes
1. **Structure vs. Flexibility**: Spreadsheets/docs are too unstructured; enterprise tools are too rigid.
2. **Single-Person vs. Team**: Most lightweight tools optimize for individual capture, not team consumption.
3. **Capture vs. Synthesis vs. Sharing**: No lightweight tool spans the full lifecycle from raw notes → structured insights → shareable artifact.
4. **Insight Decay**: Even when insights are captured, they are rarely referenced in roadmap or prioritization conversations.

---

## 4. Success Metrics

| Metric Type | Metric | Current Baseline | Target |
|-------------|--------|------------------|--------|
| **Outcome** | Time from final interview to synthesized, shareable insight summary | 2–5 days (often never formally completed) | < 2 hours |
| **Outcome** | Reuse rate of past discovery insights in new product initiatives | < 10% (insights rarely referenced after initial share) | > 50% of initiatives explicitly reference past discovery |
| **Outcome** | Stakeholder alignment on priority problem (measured by pre/post survey or decision velocity) | Mixed — often re-litigated in roadmap meetings | 90% agreement on top 3 problems after discovery readout |
| **Process** | Number of distinct tools used in the discovery-synthesis-share workflow | 3–5 tools | 1–2 tools |
| **Process** | Steps to create a shareable insight summary from raw notes | 10+ manual steps (copy, paste, format, tag, organize, draft narrative, create slides) | < 5 steps |
| **Process** | Back-and-forth clarifications required from stakeholders after discovery shareout | 3–5 rounds of "can you find the quote for...?" | < 1 round (self-service access to evidence) |
| **Emotional** | PM confidence in product decisions (self-reported 1–5) | 2.5 / 5 (moderate, often anxious) | 4+ / 5 (confident, evidence-backed) |
| **Emotional** | Feeling overwhelmed by discovery artifacts (self-reported 1–5, lower is better) | 4 / 5 (highly overwhelmed) | 2 / 5 (manageable, in control) |
| **Emotional** | Credibility perception in discovery reviews (stakeholder-reported 1–5) | 2.5 / 5 (variable) | 4+ / 5 (consistently credible) |

---

## 5. User Journey Map

### Journey: From Raw Interview Notes to Trusted Team Insight

| Stage | User Action | Touchpoint | Pain Point | Emotion | Opportunity |
|-------|-------------|------------|------------|---------|-------------|
| **1. Awareness / Trigger** | PM finishes last interview of the week and realizes they have hours of raw notes but no structured takeaway | Zoom recording, notebook, scattered sticky notes | The "synthesis cliff" — energy drops after interviews; no clear next step | Overwhelmed, anxious | Provide a structured synthesis template triggered automatically after interview completion |
| **2. Consideration** | PM asks: "How should I process this? Spreadsheet? Doc? Whiteboard? Dedicated tool?" | Google Drive, Notion, bookmarks folder | Paralysis by choice; each tool has trade-offs; no team standard | Uncertain, frustrated | Offer a lightweight, opinionated workflow that fits between docs and enterprise tools |
| **3. Decision** | PM defaults to their usual habit (Google Doc or spreadsheet) because it's fastest and free | Google Docs, Excel | PM knows this approach is flawed but doesn't have time to learn or pay for a better system | Resigned, pragmatic | Reduce onboarding to near-zero; make the structured path the easiest path |
| **4. Execution** | PM manually copies quotes, tries to cluster by theme, drafts a narrative, hunts for specific timestamps | Spreadsheet cells, copy-paste, manual formatting | Tedious, error-prone, lossy; themes emerge but aren't tied to JTBD; no reuse of prior frameworks | Bored, drained, frustrated | Auto-cluster by JTBD dimensions; suggest job statements from quotes; link to prior similar insights |
| **5. Completion** | PM shares a long document or spreadsheet in Slack/Notion and presents in a team meeting | Slack, Google Slides, meeting room | Stakeholders skim or don't read; PM presents for 30 minutes; questions focus on methodology, not insights | Defensive, disappointed | Generate a one-page visual summary with evidence-linked quotes; enable async consumption |
| **6. Follow-up** | A month later, the team debates a roadmap item and no one can find the original discovery evidence | Email search, Slack scroll, old meeting notes | Insights decay; the discovery investment is effectively lost; PM must re-interview or argue from memory | Regretful, cynical, burned out | Create a searchable, persistent insight repository where every roadmap item links to discovery evidence |

### Journey Insights
- **The biggest drop-off happens between Execution and Follow-up**: PMs often complete the immediate shareout but fail to create a reusable asset. This is where enterprise repositories try to intervene — but they do so with too much friction.
- **Emotional low point is Follow-up**: The feeling that discovery "doesn't stick" causes PMs to deprioritize future customer conversations.
- **Highest leverage opportunity**: Make synthesis so fast and the output so useful that it becomes the default behavior — not a chore.

---

## Discovery Synthesis & Next Steps

### What We Learned
1. The problem is not a lack of customer conversations — it's a **synthesis and distribution gap** between conversation and decision.
2. PMs hire tools for speed and flexibility, but those same tools fail them at scale and sharing. The **retention reason** for lightweight tools (zero friction) is the exact attribute a better solution must preserve.
3. Emotional and social jobs are nearly as important as functional jobs: PMs need to **feel credible** and **be perceived as rigorous**, not just produce rigorous work.
4. The journey map reveals that **insight decay** is the hidden cost of poor synthesis — discovery outputs that aren't searchable and linkable become sunk costs.

### Recommended Next Steps
1. **Validate with 3–5 target users**: Interview PMs who fit the segment to confirm the problem statement and JTBD priorities.
2. **Prototype a lightweight synthesis workflow**: Design the minimum viable structure (e.g., interview → job statements → evidence links → one-page summary) that can be executed in under 2 hours.
3. **Define the insight repository model**: Determine how past insights should be tagged, searched, and linked to roadmap items to prevent decay.
4. **Run a solution experiment**: Test a templated workflow (Notion/Airtable-based or lightweight custom tool) with 2–3 teams and measure against the success metrics above.

---

*Discovery conducted following the Product Discovery Manager skill workflow, grounded in Marty Cagan's *INSPIRED* and *Product Model First Principles*, Tony Ulwick's Jobs-to-be-Done Framework, and Figma's User Journey Mapping methodology.*
