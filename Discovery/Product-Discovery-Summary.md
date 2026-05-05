# Product Discovery Summary

## 1. Problem Statement

> **Cash-strapped Indonesians who complete KYC on a pinjol app** struggle to **convert into active borrowers** because **the approved credit limit is perceived as insufficient relative to their financial need and the effort invested**, which leads to **high drop-off at the approval stage, stagnant conversion rates, and missed revenue—while Risk maintains strict underwriting criteria to control NPL**.

**Key tension**: User needs (higher perceived limit) vs. Business constraint (strict risk criteria to prevent NPL). The solution space must improve *perceived value* and *conversion* without loosening underwriting.

---

## 2. Jobs-to-be-Done

### Core Job
- **Job**: When I have an urgent or planned financial need, I want to access a sufficient amount of credit quickly and with minimal effort, so I can cover my expense and maintain my financial stability.
- **Value**: Prevents falling into worse alternatives (loan sharks, asset sale, social shame).
- **Satisfaction**: Frustrated (2/5) — users complete effort but don't get the expected outcome.
- **Importance**: Critical

### Related Jobs

#### Functional
- **Job**: When I submit my personal documents for KYC, I want the process to feel fast and transparent, so I don't feel my time and data are wasted.
  - *Value*: Reduces cognitive cost of applying.
  - *Satisfaction*: Tolerating (3/5)
  - *Importance*: Important

- **Job**: When I receive a credit limit offer, I want to understand how it was determined, so I can decide whether to accept it or look elsewhere.
  - *Value*: Enables informed decision-making.
  - *Satisfaction*: Frustrated (2/5)
  - *Importance*: Important

- **Job**: When my initial limit is lower than I need, I want a clear and achievable path to increase it over time, so I can rely on this service in the future.
  - *Value*: Builds long-term customer value and retention.
  - *Satisfaction*: Frustrated (2/5)
  - *Importance*: Critical

#### Emotional
- **Job**: When I apply for a loan, I want to feel respected and trusted as a borrower, so I don't feel judged or devalued by a low offer.
  - *Value*: Protects self-esteem and brand relationship.
  - *Satisfaction*: Frustrated (2/5)
  - *Importance*: Important

- **Job**: When I face a financial gap, I want to feel in control and hopeful, so I can reduce my anxiety about money.
  - *Value*: Emotional relief during stress.
  - *Satisfaction*: Frustrated (2/5)
  - *Importance*: Critical

#### Social
- **Job**: When I borrow money digitally, I want to be seen as financially savvy and responsible, so I can maintain my self-image and social standing.
  - *Value*: Avoids stigma associated with borrowing or low creditworthiness.
  - *Satisfaction*: Tolerating (3/5)
  - *Importance*: Nice-to-have

---

## 3. Existing Solutions & Gaps

| Solution | Strengths | Gaps | Why Users Stay |
|----------|-----------|------|----------------|
| **Other pinjol apps** (e.g., Kredivo, Akulaku, Shopee PayLater) | Quick approval, familiar KYC, promo rates | Same limit-anxiety risk; users repeat KYC across apps; no guarantee of better limit | Habit, better promo, slightly higher limit |
| **Informal lending** (family/friends, loan sharks) | No KYC, flexible terms, immediate cash | High interest, social shame, legal risk, no record | No alternative available, personal trust |
| **Credit cards** | Higher limits, revolving credit, prestige | Hard to qualify for thin-file users; slower onboarding | Status, rewards, convenience |
| **Salary advance** | No interest, instant access | Dependent on employer policy; limited amount | Safety, no debt cycle |
| **Pawning / asset sale** (Pegadaian, selling goods) | Immediate cash, no credit check | Loss of asset, undervaluation, irreversible | Desperation, no other access |

**Key insight**: The real competition is not just other pinjol apps—it's informal lending and salary advances. If the pinjol experience feels untrustworthy or insufficient, users exit to offline alternatives.

---

## 4. Success Metrics

| Metric Type | Metric | Current | Target |
|-------------|--------|---------|--------|
| **Outcome** | Application-to-disbursement conversion rate | Stagnant (baseline to be measured) | +15-25% improvement |
| **Outcome** | Credit limit acceptance rate (% of approved users who draw down) | Low (implied by problem) | +20% improvement |
| **Outcome** | 30-day NPL rate among users who accepted lower initial limits | Baseline | Maintain or improve (do not trade risk for conversion) |
| **Process** | Time from KYC completion to limit display | Unknown | < 2 minutes |
| **Process** | Support tickets / complaints about "low limit" or "unfair limit" | Unknown | -30% reduction |
| **Process** | Drop-off rate at the limit-reveal screen | High | -20% reduction |
| **Emotional** | Perceived fairness of limit (survey: "The limit I received was fair" 1-5) | ~2.5 | ≥ 3.5 |
| **Emotional** | Trust score in brand/app (post-experience survey) | Unknown | ≥ 4.0 / 5 |
| **Emotional** | % of users who feel "in control" of their borrowing options | Unknown | ≥ 60% |

---

## 5. User Journey Map

| Stage | User Action | Touchpoint | Pain Point | Emotion | Opportunity |
|-------|-------------|------------|------------|---------|-------------|
| **Awareness / Trigger** | Realizes need for quick cash due to emergency or planned expense | Personal circumstance, social media ad, word-of-mouth | Uncertainty about safe borrowing options; fear of scams | Anxious, urgent | Transparent messaging about responsible lending; pre-qualification limit estimator |
| **Consideration** | Compares pinjol apps, reads reviews, checks terms | App store, Google search, social media, friend recommendations | Too many options; unclear which app will give the best limit; fear of hidden fees | Skeptical, hopeful | Show estimated limit range *before* KYC; display trust signals (OJK license, user count) |
| **Application / KYC** | Downloads app, fills forms, uploads KTP/selfie, links bank/e-wallet | Mobile app, camera, OCR, third-party data providers | Repetitive data entry; unclear why each field is needed; anxiety about data privacy | Frustrated, committed | Progressive profiling; explain "why we need this" at each step; show progress bar |
| **Decision (Limit Reveal)** | Views approved limit, interest rate, and tenor | In-app limit screen, push notification | Limit feels too low vs. effort invested and actual need; no explanation provided; no recourse | Disappointed, betrayed, embarrassed | Explain limit rationale in plain language; show personalized growth path; offer partial draw or appeal option |
| **Execution** | Accepts/rejects offer, signs e-contract, receives disbursement | E-contract, disbursement flow, bank/e-wallet account | If rejected, all KYC effort feels wasted; if accepted, may still feel resentment | Resigned or relieved | Instant feedback on appeal; option to draw partial amount; clear repayment schedule |
| **Follow-up / Repayment** | Repays installments, checks app for future offers | Repayment reminders, app re-open, customer service | No visibility into when or how limit can increase; feels like a dead end | Cautious, uncertain | Proactive limit-review notifications; loyalty rewards for on-time repayment; transparent eligibility criteria |

---

## Discovery Notes & Next Steps

1. **Validate baselines**: The current metrics (conversion rate, acceptance rate, NPL by segment) must be measured before solutioning.
2. **Segment deep-dive**: Not all users drop off for the same reason. Segment by credit profile, loan purpose, and channel to identify which group has the highest upside.
3. **Risk collaboration**: Since Risk will not loosen criteria, co-discovery with the Risk team is essential to find *friction-reduction* and *perception-improvement* levers that do not increase NPL.
4. **Prototype testing**: Cagan's validation approach (feasibility, usability, value) should be applied to any limit-reveal redesign—test prototypes with real users before engineering build.
