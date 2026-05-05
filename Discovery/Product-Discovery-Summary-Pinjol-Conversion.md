# Product Discovery Summary: Pinjol Credit Limit Conversion Gap

> **Discovery Context**: Pinjol (digital lending) users complete KYC but abandon the funnel upon receiving a credit limit lower than expected. Business demands conversion growth; Risk refuses to loosen criteria due to NPL concerns. This discovery applies Cagan's *INSPIRED* principles (outcomes over output, validate before building) and Ulwick's JTBD Needs Framework.

---

## 1. Problem Statement

> **[Credit-seeking users]** struggle to **[obtain a credit limit that meets their financial need]** because **[the risk-assessed limit is perceived as insufficient relative to the effort and personal data invested in KYC]**, which leads to **[conversion stagnation, user abandonment, and erosion of trust in the lending platform]**.

### Underlying Tension (The "Impossible Trinity")
| Force | Demand | Constraint |
|-------|--------|------------|
| **Business** | Increase conversion rate and loan disbursement volume | Cannot force users to accept low limits |
| **Risk** | Maintain portfolio quality and low NPL | Unwilling to lower scoring thresholds |
| **User** | Get sufficient credit to solve their financial problem | Unwilling to complete KYC for a disappointingly low limit |

> *Cagan's principle*: "The product manager must be able to quickly evaluate opportunities to decide which are promising and which are not." The opportunity here is not to loosen risk criteria, but to **bridge the expectation-reality gap** before the user sinks cost into KYC.

---

## 2. Jobs-to-be-Done

### Core Functional Job

| Attribute | Detail |
|-----------|--------|
| **Job Statement** | When I face an urgent or planned financial shortfall, I want to access credit quickly and digitally, so I can resolve my cash-flow gap without disrupting my life or relying on informal lenders. |
| **Value of Completion** | Prevents financial disruption (late fees, missed opportunities, emergencies); provides dignity and independence compared to borrowing from family or loan sharks. |
| **Current Satisfaction** | 2/5 — Frustrated. The core job is partially satisfied (credit is accessible) but the *output* of the job (limit amount) often fails to meet the user's actual need. |
| **Importance** | Critical |

### Related Functional Jobs

| # | Job Statement | Value | Satisfaction | Importance |
|---|---------------|-------|--------------|------------|
| 1 | When I consider applying for credit, I want to know what limit I am likely to receive *before* I invest time in KYC, so I can decide whether the effort is worth it. | Saves time; reduces sunk-cost frustration; enables comparison shopping. | 1/5 — Highly frustrated. Most pinjol apps hide or obfuscate pre-KYC estimates. | Critical |
| 2 | When I receive a lower-than-expected limit, I want to understand *why* and what I can do to increase it, so I can still access the funds I need. | Restores sense of agency; builds trust through transparency. | 2/5 — Tolerating. Most apps offer generic or no explanation. | Important |
| 3 | When one lender cannot meet my need, I want to quickly identify alternative funding sources (within or outside the app), so I can still close my financial gap. | Prevents dead-ends; increases likelihood of user retention in the ecosystem. | 2/5 — Frustrated. Users must manually restart comparison elsewhere. | Important |
| 4 | When I borrow, I want to clearly understand the total cost of repayment (interest, fees, penalties), so I can plan my finances and avoid surprise debt. | Reduces anxiety; supports responsible borrowing; aligns with regulatory expectations. | 3/5 — Tolerating. Disclosure exists but is often buried in complex terms. | Important |

### Emotional Jobs

| # | Job Statement | Value | Satisfaction | Importance |
|---|---------------|-------|--------------|------------|
| 1 | When I go through the lending process, I want to feel **financially empowered and in control**, not desperate or helpless. | Dignity; reduces shame associated with borrowing. | 2/5 — Frustrated. A low limit after KYC makes users feel powerless and misled. | Critical |
| 2 | When I submit sensitive personal data for KYC, I want to feel **respected and trusted**, not scrutinized or treated like a criminal. | Trust; reduces drop-off during KYC; increases brand loyalty. | 3/5 — Neutral. KYC is tolerated as a necessary evil. | Important |
| 3 | When I complete a tedious application process, I want to feel that **my effort was worthwhile and rewarded**, not wasted. | Reduces cognitive dissonance; increases willingness to return. | 1/5 — Highly frustrated. Sunk-cost feeling is the primary driver of abandonment. | Critical |

### Social Jobs

| # | Job Statement | Value | Satisfaction | Importance |
|---|---------------|-------|--------------|------------|
| 1 | When I use a digital lender, I want to be perceived as **financially savvy and responsible**, not reckless or desperate. | Social identity; willingness to recommend the app to peers. | 3/5 — Neutral. Brand perception varies by lender. | Nice-to-have |
| 2 | When I discuss credit options with peers, I want to be seen as someone who **makes smart, informed decisions** based on transparency and fairness. | Word-of-mouth; social proof; community trust. | 2/5 — Tolerating. Negative experiences are shared more than positive ones. | Important |

---

## 3. Existing Solutions & Gaps

| Solution | Strengths | Gaps | Why Users Stay / Why They Leave |
|----------|-----------|------|---------------------------------|
| **Other Pinjol Apps (competitors)** | Fast approval; minimal KYC; often aggressive marketing with high advertised limits. | Same underlying risk models lead to similar low limits; hidden fees; predatory terms; trust issues. | Users leave easily — switching costs are near zero in digital lending. Multi-homing is common. |
| **Traditional Banks (personal loans, credit cards)** | Lower interest rates; regulated; higher potential limits; builds credit history. | Slower process (days/weeks); stricter KYC; requires salary slips or collateral; less accessible to gig workers. | Users stay for reliability and lower cost, but abandon when speed is critical. |
| **Informal Lending (family, friends, loan sharks)** | Immediate cash; no KYC; flexible terms (family) or none (loan sharks). | Social stigma and relationship strain (family); extreme interest and harassment (loan sharks); no legal protection. | Users stay only when desperate; digital lenders aim to displace this but fail when limits are too low. |
| **Salary Advance / Earned Wage Access Apps** | No interest; very fast; no credit check. | Limited to salaried employees with verified payroll; small amounts (1x monthly salary max). | Users stay if eligible, but these don't serve the underbanked or gig economy. |
| **Step-Up / Loyalty Limit Programs** | Rewards good repayment with gradual limit increases; builds long-term relationship. | Does not solve the *immediate* need that triggered the first visit; requires patience users don't have. | Users stay if their need is small and patience is high; most churn before reaching higher tiers. |
| **Loan Aggregators / Comparison Sites** | Side-by-side comparison; saves user research time. | Often biased by commission; doesn't solve the expectation-reality gap at the individual lender level. | Users visit for research but still face the same abandonment problem at each individual lender. |

### Key Gap Insight
> The fundamental gap is **not** that risk criteria are too strict. The gap is that **users invest effort before knowing the reward**, creating a predictable pattern of sunk-cost disappointment. No existing solution adequately solves the "expectation setting before KYC" problem.

---

## 4. Success Metrics

### Outcome Metrics (What changes in the user's life / business results)

| Metric | Current (Estimated) | Target | Rationale |
|--------|---------------------|--------|-----------|
| **KYC-to-Drawdown Conversion Rate** | Stagnant / Declining | +20% uplift | Primary business outcome. Measures whether expectation-setting reduces abandonment. |
| **Revenue per Approved User** | Baseline | Maintain or improve | Ensures we don't just convert more low-value users. |
| **30-Day User Retention** (post-limit disclosure) | Low | +15% | Indicates whether the experience builds relationship even when limit is modest. |
| **Repeat Borrow Rate** | Baseline | +10% | Signals long-term job satisfaction and trust. |

### Process Metrics (How the experience improves)

| Metric | Current (Estimated) | Target | Rationale |
|--------|---------------------|--------|-----------|
| **Drop-off Rate at Limit Disclosure Screen** | High (primary leak) | -30% | Direct measure of the core problem. |
| **Time from KYC Completion to First Drawdown** | Hours to days | < 30 minutes | Friction reduction; users who know their limit upfront decide faster. |
| **Support Tickets Related to "Why is my limit so low?"** | High volume | -40% | Indicates clarity and transparency improvement. |
| **Pre-KYC Limit Estimate Accuracy** | N/A or low | > 80% correlation with final limit | Ensures the expectation-setting mechanism is trustworthy. |

### Emotional Metrics (How the user feels)

| Metric | Current | Target | Rationale |
|--------|---------|--------|-----------|
| **"I felt the limit was fair"** (post-disclosure survey, 1–5) | ~2.0 | > 3.5 | Captures perceived fairness even when limit is low. |
| **"I understood why I received this limit"** (clarity score, 1–5) | ~2.0 | > 4.0 | Measures transparency of risk decisioning. |
| **"I feel trusted by this lender"** (trust score, 1–5) | ~2.5 | > 3.5 | Emotional outcome that predicts retention. |
| **NPS (Net Promoter Score)** | Likely negative | Move toward neutral/positive | Ultimate emotional and loyalty signal. |

---

## 5. User Journey Map

> *Framework reference*: Journey stages adapted from Figma's five-step model (Awareness, Consideration, Decision, Purchase, Retention), customized for the lending context.

| Stage | User Action | Touchpoint | Pain Point | Emotion | Opportunity |
|-------|-------------|------------|------------|---------|-------------|
| **1. Trigger / Awareness** | User realizes they need cash (emergency, bill, opportunity). | Life event; social media ad; word-of-mouth; app notification. | Urgency creates anxiety; user may not know where to start. | Anxious, urgent | Push pre-qualified limit offers based on existing data before KYC. |
| **2. Consideration** | User compares lending options (pinjol apps, banks, informal). | Google search; app store; comparison sites; peer advice. | Misleading ads promise high limits; terms are unclear; fear of scams. | Skeptical, hopeful | Display realistic, personalized limit estimates *before* download or registration. |
| **3. Onboarding / KYC** | User downloads app, registers, submits ID, selfie, bank data. | Mobile app; camera; e-KYC provider; bank statement upload. | KYC is tedious and intrusive; user fears data misuse; effort feels high. | Tolerant, cautious | **Show estimated limit range after minimal data input (before full KYC)** to validate effort. |
| **4. Evaluation / Decision** | User receives approved credit limit and decides whether to proceed. | In-app limit screen; push notification; SMS. | **THE CORE PAIN POINT**: Limit is lower than expected; no explanation; sunk-cost feeling. | Disappointed, betrayed, frustrated | **Provide transparent reason for limit + actionable path to increase it**; offer alternative products. |
| **5. Drawdown / Execution** | User accepts limit, selects loan amount, signs agreement, receives funds. | In-app loan builder; e-signature; disbursement to e-wallet/bank. | If limit was disappointing, user may skip this stage entirely. If proceeding, fees may feel hidden. | Resigned or relieved | Celebrate the drawdown; reinforce responsible borrowing messaging; make fees crystal clear. |
| **6. Post-Experience / Retention** | User repays (or defaults); decides whether to return for future needs. | Repayment reminders; app re-engagement; customer support. | If initial experience was negative, user will not return; may warn peers. | Indifferent or resentful | Proactive limit re-evaluation; loyalty rewards; transparent step-up program; re-engagement with empathy. |

### Journey Map Insights

1. **The biggest drop-off is Stage 4 (Evaluation/Decision)** — this is where the expectation-reality mismatch hits. Every other stage can be perfect, but if Stage 4 disappoints, the journey ends.
2. **The highest-leverage opportunity is in Stage 3 (Onboarding/KYC)** — by providing an *estimate* after partial data input, the user can self-select whether to invest effort in full KYC. This respects the user's time and reduces the volume of disappointed users entering Stage 4.
3. **Emotional recovery is possible even with low limits** — if Stage 4 includes transparency (why) and agency (how to improve), users may still proceed or return later.

---

## 6. Synthesis & Strategic Implications

### What This Discovery Reveals

Per Cagan's opportunity assessment framework, the 10 fundamental questions applied to this problem yield the following insight:

| Cagan's Question | Discovery Insight |
|------------------|-------------------|
| What problem will this solve? | Reduce KYC-to-conversion abandonment by aligning user expectations with risk reality *before* effort is sunk. |
| For whom? | Credit-seeking users who need quick digital loans but receive disappointingly low limits after KYC. |
| How big is the opportunity? | Conversion uplift of 20%+ on a stagnant funnel directly impacts revenue; support cost reduction is secondary. |
| How will we measure success? | KYC-to-drawdown rate; drop-off at limit disclosure; fairness/clarity emotional scores. |
| What alternatives exist? | Competitors, banks, informal lenders, salary advances — none solve the expectation-reality gap well. |
| Why are we best suited? | We have the data to provide accurate pre-KYC estimates; we have the risk model to explain decisions. |
| Why now? | Conversion stagnation is actively hurting growth; competitive pressure is intensifying; regulatory scrutiny on opaque lending is rising. |

### The Non-Obvious Solution Path

> **The solution is likely NOT to change the risk model.** It is to **change *when* and *how* the user learns their limit**, and to **give them agency even when the limit is low**.

Candidate solution directions (to be validated through prototyping and user testing per Cagan's discovery process):

1. **Pre-KYC Limit Estimator** — Show a range after phone number + basic demographic input, before full identity verification. Set accurate expectations upfront.
2. **Transparent Limit Explanation Engine** — When a low limit is given, show the specific factors (income stability, repayment history, device risk signals) and the weight of each.
3. **Limit Improvement Roadmap** — Give the user a concrete, time-bound path to a higher limit (e.g., "Link your payroll account → +Rp500K"; "Repay 3 small loans on time → +Rp1M").
4. **Alternative Product Routing** — If the primary product limit is insufficient, seamlessly offer alternatives (shorter tenor, partnered lenders, salary advance) without making the user restart.
5. **Effort-Validation Moment** — Celebrate KYC completion *before* showing the limit, framing it as "You are now verified" rather than "Here is your disappointing reward."

---

*This discovery summary was produced using the Product Discovery Manager skill, grounded in Marty Cagan's INSPIRED principles and Tony Ulwick's Jobs-to-be-Done Needs Framework, and references the User Journey Mapping methodology from Figma.*
