# AI PM Skills

A structured workspace and web interface for product discovery and solution architecture. Grounded in Marty Cagan's product model principles, Jobs-to-be-Done (JTBD) theory, user journey mapping, and low-friction solution design.

> **Built for product managers** who want a systematic, repeatable approach to understanding customer problems *and* finding the quickest path to validate solutions.

---

## What This Is

This repository gives you three things:

1. **Reference Materials** — Curated PDF guides on product discovery frameworks (Cagan's *INSPIRED*, JTBD, User Journey Mapping) and solution frameworks (Opportunity Solution Trees, RICE Prioritization, T-Shirt Sizing)
2. **Two Kimi Skills** — `product-discovery-manager` and `solution-architect` skill definitions that auto-trigger via the Kimi CLI
3. **A Web Interface** — A local chat app that runs both skills, with skill switching, phased workflows, and beautiful HTML reports

You own all your data. Everything runs locally on your machine. No cloud, no subscriptions, no data leaving your device.

---

## The Two Skills

### 🔍 Product Discovery Manager
Guides structured customer discovery across 5 phases:

| Phase | Output |
|-------|--------|
| **1. Problem Elicitation** | Validated problem statement |
| **2. JTBD Analysis** | Core + related jobs with satisfaction & importance |
| **3. Competitive Landscape** | Solutions & gaps table |
| **4. Success Metrics** | Outcome, process, and emotional metrics |
| **5. User Journey Mapping** | Journey map with pain points & opportunities |

**Skill file:** `.agents/skills/product-discovery-manager/SKILL.md`

### 🛠️ Solution Architect
Finds the lowest-friction path from discovery to validated solution across 8 phases:

| Phase | Output |
|-------|--------|
| **1. Discovery Input** | Synthesized discovery findings |
| **2. Barrier Analysis** | What prevents users from completing each JTBD |
| **3. Opportunity Exploration** | Low-tech → no/low-code → SaaS → custom build options |
| **4. Opportunity Solution Tree** | Visual tree of barriers → opportunities → outcomes |
| **5. T-Shirt Sizing** | Relative effort estimates (XS–XL) |
| **6. RICE Prioritization** | Reach × Impact × Confidence / Effort scores |
| **7. Solution Recommendation** | Next easiest high-impact step |
| **8. Validation Plan** | Pilot scope, metrics, go/no-go criteria |

**Key principle:** A spreadsheet + WhatsApp group that works today beats an app that ships in 3 months.

**Skill file:** `.agents/skills/solution-architect/SKILL.md`

---

## Quick Start

### Prerequisites

- **macOS** (the web interface uses Kimi Code CLI which currently integrates best on Mac)
- **Python 3.9+**
- **Kimi Code CLI** installed (VS Code extension)

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd AI-PM-Skills

# Install Python dependencies
cd web-app
pip3 install -r requirements.txt

# Set your Kimi CLI path (only needed if it's not in the default location)
export KIMI_BIN="$HOME/Library/Application Support/Code/User/globalStorage/moonshot-ai.kimi-code/bin/kimi/kimi"
```

### Run the Web Interface

```bash
cd web-app
python3 app.py
```

Then open **http://localhost:5050** in your browser.

---

## How to Use

### Switch Skills

Use the dropdown in the top-right corner to switch between **🔍 Discovery** and **🛠️ Solution** mode.

### Discovery Mode

1. **Describe your problem** — Type a customer problem and click **Start Discovery**
2. **Chat through 5 phases** — The Product Discovery Manager guides you with probing questions
3. **Save** (💾) — Persists outputs to `Discovery/_result/yyyymmdd-problem-name/`
4. **Report** (📄) — Generates a dark-mode HTML report with tables, badges, and reading time
5. **Browse** (📂) — View all past discoveries

### Solution Mode

1. **Share discovery output** — Paste your discovery summary or describe the problem space
2. **Chat through 8 phases** — The Solution Architect explores barriers, opportunities, and sizing
3. **Save** (💾) — Persists outputs to `Solutions/_result/yyyymmdd-problem-name/`
4. **Report** (📄) — Generates the same HTML report format for solution artifacts
5. **Browse** (📂) — View all past solution reports

---

## Reference Materials

The `_context/` folders contain the frameworks that power both skills:

### Core Product Model (`_context/`)
- **INSPIRED** by Marty Cagan — Book summary covering product teams, discovery vs. execution, opportunity assessment
- **Product Model First Principles** — One-page visual poster of 20 principles across Product Team, Strategy, Discovery, Delivery, and Culture
- **Product Model First Principles In Depth** — Deep-dive on Product Team and Product Strategy principles

### Discovery Frameworks (`Discovery/_context/`)
- **Jobs-to-be-Done Framework** by Tony Ulwick — How to define, categorize, and capture customer needs
- **JTBD Product Framework Guide** — Comprehensive guide to applying JTBD in product development
- **User Journey Mapping** — Figma resource on creating journey maps with key components and a five-step process

### Solution Frameworks (`Solutions/_context/`)
- **Opportunity Solution Trees** — Framework for connecting opportunities to solutions
- **RICE Prioritization Framework for Product Managers** — Scoring methodology for prioritization
- **T-Shirt Sizing** — Relative effort estimation guide

---

## Folder Structure

```
.
├── _context/                          # Core product model references
│   ├── INSPIRED-BY-MARTY-CAGAN-...
│   ├── [Poster] Product Model First Principles.pdf
│   └── Product Model First Principles In Depth...
│
├── Discovery/                         # Discovery-phase materials
│   ├── _context/                      # JTBD & journey mapping references
│   │   ├── Jobs-to-be-Done-Framework.pdf
│   │   ├── Jobs-to-be-Done-Product-Framework-Guide.pdf
│   │   └── User Journey Mapping.pdf
│   └── discoveries/                   # ← Your personal discovery outputs (gitignored)
│       └── 20260502-problem-name/
│           ├── 01-problem-statement.md
│           ├── 02-jobs-to-be-done.md
│           ├── ...
│           └── index.html
│
├── Solutions/                         # Solution-phase materials
│   ├── _context/                      # Solution framework references (tracked)
│   │   ├── Opportunity Solution Trees.pdf
│   │   ├── RICE Prioritization Framework for Product Managers.pdf
│   │   └── T-Shirt Sizing.pdf
│   └── solutions/                     # ← Your personal solution outputs (gitignored)
│       └── 20260503-problem-name/
│           ├── 01-discovery-input.md
│           ├── 02-barrier-analysis.md
│           ├── ...
│           └── index.html
│
├── .agents/skills/                    # Kimi skill definitions
│   ├── product-discovery-manager/
│   │   └── SKILL.md
│   └── solution-architect/
│       └── SKILL.md
│
└── web-app/                           # Local web interface
    ├── app.py
    ├── report_generator.py
    ├── requirements.txt
    ├── templates/
    │   └── index.html
    └── static/
        ├── css/style.css
        └── js/app.js
```

> **Privacy note:** The `Discovery/_result/` and `Solutions/_result/` folders are gitignored. When someone forks this repo, they get a clean workspace with only the reference materials and skill definitions — none of your personal work.

---

## Security & Privacy

- **No API keys committed** — The Kimi CLI path defaults to the standard macOS install location. Override with the `KIMI_BIN` environment variable if needed.
- **Everything runs locally** — Your conversations and reports never leave your machine.
- **Personal work is gitignored** — Discovery outputs (`Discovery/_result/`) and solutioning results (`Solutions/_result/`) are excluded from version control by default.
- **No cloud services** — No databases, no third-party APIs, no analytics.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Kimi CLI not found" | Set `KIMI_BIN` environment variable to your kimi binary path |
| Port 5050 in use | The app auto-detects conflicts. Check the console output for the actual port |
| Flask server won't start | Ensure Python 3.9+ is installed and `pip3 install -r requirements.txt` succeeded |
| Reports look plain | Check your internet connection — the HTML report loads fonts from Google Fonts |
| Skill not triggering | Make sure the Kimi CLI has access to the `.agents/skills/` directory |

---

## Credits & Inspiration

- **Marty Cagan** — [Silicon Valley Product Group](https://www.svpg.com/), author of *INSPIRED* and *TRANSFORMED*
- **Tony Ulwick** — [Strategyn](https://strategyn.com/), creator of Jobs-to-be-Done Theory
- **Paweł Huryn** — Deep-dive analysis of Product Model First Principles
- **Medium.com** & **mellow.dev** — Design inspiration for the HTML report typography

---

## License

This is a personal knowledge workspace. The reference PDFs are publicly available materials. The code is provided as-is for educational and personal use.
