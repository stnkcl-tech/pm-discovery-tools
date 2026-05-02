# Product Discovery Manager

A structured workspace and web interface for conducting customer discovery using proven product management frameworks. Grounded in Marty Cagan's product model principles, Jobs-to-be-Done (JTBD) theory, and user journey mapping.

> **Built for product managers** who want a systematic, repeatable approach to understanding customer problems before building solutions.

---

## What This Is

This repository gives you two things:

1. **Reference Materials** — Curated PDF guides on modern product discovery frameworks (Cagan's *INSPIRED*, JTBD, User Journey Mapping)
2. **A Web Interface** — A local chat app that guides you through a 5-phase discovery process and generates beautiful HTML reports

You own all your data. Everything runs locally on your machine. No cloud, no subscriptions, no data leaving your device.

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

### 1. Start a Discovery

Type your customer problem in the text box and click **Start Discovery**.

Example:
> "Freelance designers struggle to manage scattered client feedback across email, Slack, and Figma comments"

### 2. Chat Through 5 Phases

The Product Discovery Manager (powered by Kimi) will guide you through:

| Phase | What You'll Do | Output |
|-------|---------------|--------|
| **1. Problem Elicitation** | Answer probing questions about context, frequency, and impact | A validated problem statement |
| **2. JTBD Analysis** | Identify the jobs users hire products to do | Core + related jobs with satisfaction scores |
| **3. Competitive Landscape** | Map existing solutions and their gaps | Solutions & gaps table |
| **4. Success Metrics** | Define how you'd measure success | Outcome, process, and emotional metrics |
| **5. User Journey Mapping** | Visualize the end-to-end experience | Journey map table |

### 3. Save Your Work

Click **💾 Save** at any time to persist your discovery to a dated folder:

```
Discovery/
└── discoveries/
    └── 20260502-freelance-designer-feedback/
        ├── 01-problem-statement.md
        ├── 02-jobs-to-be-done.md
        ├── 03-competitive-landscape.md
        ├── 04-success-metrics.md
        ├── 05-user-journey-map.md
        └── summary.md
```

### 4. Generate a Report

Click **📄 Report** to generate a beautiful HTML report with:

- Medium-style **reading time** estimation
- Typography-focused design (elegant serif headings + readable body text)
- Sticky sidebar navigation
- Highlighted key findings and clean data tables

The report is saved as `index.html` in the same discovery folder. Open it in any browser or print to PDF.

### 5. Browse Past Discoveries

Click **📂 Browse** to see all your saved discoveries and their reports.

---

## Reference Materials

The `_context/` folders contain the frameworks that power the discovery process:

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
├── Solutions/                         # ← Your solutioning outputs (gitignored)
│   └── _context/                      # Solution framework references
│       └── Opportunity Solution Trees.pdf
│
├── .agents/skills/                    # Kimi skill definition
│   └── product-discovery-manager/
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

> **Privacy note:** The `Discovery/discoveries/` and `Solutions/` folders are gitignored. When someone forks this repo, they get a clean workspace with only the reference materials — none of your personal discovery work.

---

## Security & Privacy

- **No API keys committed** — The Kimi CLI path defaults to the standard macOS install location. Override with the `KIMI_BIN` environment variable if needed.
- **Everything runs locally** — Your discovery conversations and reports never leave your machine.
- **Personal work is gitignored** — Discovery outputs and solutioning results are excluded from version control by default.
- **No cloud services** — No databases, no third-party APIs, no analytics.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Kimi CLI not found" | Set `KIMI_BIN` environment variable to your kimi binary path |
| Port 5050 in use | The app auto-detects conflicts. Check the console output for the actual port |
| Flask server won't start | Ensure Python 3.9+ is installed and `pip3 install -r requirements.txt` succeeded |
| Reports look plain | Check your internet connection — the HTML report loads fonts from Google Fonts |

---

## Credits & Inspiration

- **Marty Cagan** — [Silicon Valley Product Group](https://www.svpg.com/), author of *INSPIRED* and *TRANSFORMED*
- **Tony Ulwick** — [Strategyn](https://strategyn.com/), creator of Jobs-to-be-Done Theory
- **Paweł Huryn** — Deep-dive analysis of Product Model First Principles
- **Medium.com** & **mellow.dev** — Design inspiration for the HTML report typography

---

## License

This is a personal knowledge workspace. The reference PDFs are publicly available materials. The code is provided as-is for educational and personal use.
