# JobScanner

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-00D4AA?style=flat)](https://groq.com)

**AI-powered job search assistant with intelligent matching and cover letter generation.**

JobScanner aggregates job listings, scores them against your profile using AI, and generates tailored cover letters—streamlining your job search workflow.

---

## Features

### Job Discovery
- **Multi-Source Search** — Aggregates from RemoteOK, Remotive, and manual URL entry
- **Smart Filtering** — Filter by salary, location, keywords, and job type
- **Keyword Presets** — Pre-configured searches for target roles

### AI Matching
- **Match Scoring** — AI analyzes job requirements vs. your skills (0-100 score)
- **Requirement Analysis** — Breaks down must-haves, nice-to-haves, and gaps
- **Fit Explanation** — Detailed reasoning for each match score

### Application Tools
- **Cover Letter Generator** — AI-crafted letters tailored to each position
- **PDF Export** — Professional PDF cover letters ready to submit
- **Interview Prep** — Talking points based on job requirements

### Tracking
- **Application Pipeline** — Track status: New → Applied → Interview → Offer
- **Search History** — Log of all searches and results
- **Job Database** — SQLite storage for all discovered positions

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **AI Engine** | Groq API (Llama 3.3 70B) |
| **PDF Generation** | fpdf2 |
| **Database** | SQLite |
| **Job APIs** | RemoteOK, Remotive |

---

## Quick Start

```bash
# Clone and setup
git clone https://github.com/nickstafford/jobscanner.git
cd jobscanner
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your GROQ_API_KEY

# Run
streamlit run app.py
```

Open http://localhost:8501

---

## Search Keywords (Configurable)

**Tier 1 — Financial AI**
- AI Financial Systems Engineer
- Financial Automation Engineer
- FP&A Automation Specialist

**Tier 2 — AI/ML**
- AI Engineer
- ML Engineer
- LLM Engineer
- Solutions Architect (FinTech)

---

## Project Structure

```
JobScanner/
├── app.py                    # Streamlit entry point
├── src/
│   ├── services/
│   │   ├── job_search.py     # Job API integrations
│   │   ├── ai_matcher.py     # Groq scoring & analysis
│   │   └── pdf_generator.py  # Cover letter PDFs
│   └── utils/
│       ├── database.py       # SQLite operations
│       └── config.py         # Keywords & settings
└── output/                   # Generated PDFs
```

---

## License

MIT License

---

<p align="center">
  Built by <a href="https://nickstafford.dev">Nick Stafford</a>
</p>
