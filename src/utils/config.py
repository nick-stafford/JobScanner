"""
Configuration and search keywords for JobScanner
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Note: Job search uses FREE APIs (RemoteOK, Remotive, Arbeitnow) - no keys needed!

# AI Model
GROQ_MODEL = "llama-3.3-70b-versatile"

# Minimum salary filter
MIN_SALARY = 100000

# Database
DATABASE_PATH = "data/jobs.db"

# Resume paths (for reference in cover letters)
RESUME_PATHS = {
    "main": r"C:\Users\Nick\OneDrive\Desktop\Resumes\Final\Nick_Stafford_Resume.pdf",
    "ai_ml": r"C:\Users\Nick\OneDrive\Desktop\Resumes\Nick_Stafford_Resume_AI_ML_Engineer.docx",
    "solutions_architect": r"C:\Users\Nick\OneDrive\Desktop\Resumes\Nick_Stafford_Resume_Solutions_Architect.docx",
    "financial_automation": r"C:\Users\Nick\OneDrive\Desktop\Resumes\Nick_Stafford_Resume_Financial_Automation.docx",
}

# Nick's core skills (extracted from resume)
CORE_SKILLS = {
    "financial": [
        "ERP Automation", "Financial Reporting", "GAAP Compliance",
        "Budgeting & Forecasting", "Variance Analysis", "Month-End Close",
        "Reconciliation", "Audit Support", "Cash Flow Management", "FP&A"
    ],
    "platforms": [
        "Sage Intacct", "QuickBooks", "SAP", "NetSuite", "Oracle Financials",
        "Palantir Foundry", "Power BI", "Tableau", "Workday",
        "Adaptive Insights", "Anaplan"
    ],
    "technical": [
        "Python", "SQL", "Excel/VBA", "ETL Pipelines", "Data Modeling",
        "REST APIs", "RPA", "UiPath", "Alteryx", "SSIS", "Git", "AI Agents"
    ]
}

# Search keywords - ordered by priority (financial AI first, then general AI)
SEARCH_KEYWORDS = [
    # Tier 1: Financial + AI (highest priority)
    "AI Financial Systems Engineer",
    "Financial Automation Engineer",
    "AI Finance Analyst",
    "FP&A Automation Engineer",
    "AI Accounting Systems",
    "FinTech AI Engineer",
    "Financial AI Developer",
    "ERP Automation Engineer",
    "RPA Developer Finance",
    "Intelligent Automation Finance",

    # Tier 2: Solutions/Architecture roles
    "Solutions Architect Finance",
    "Solutions Architect FinTech",
    "Financial Systems Architect",
    "Enterprise Architect Finance",
    "Integration Architect Finance",

    # Tier 3: General AI roles
    "AI Engineer",
    "Machine Learning Engineer",
    "AI Solutions Engineer",
    "AI Automation Engineer",
    "AI Platform Engineer",
    "LLM Engineer",
    "AI Agent Developer",
    "Generative AI Engineer",

    # Tier 4: Automation & Integration
    "Automation Engineer Python",
    "ETL Developer",
    "Data Pipeline Engineer",
    "Integration Engineer",
    "RPA Developer",
    "Process Automation Engineer",
]

# Job statuses
JOB_STATUSES = [
    "new",
    "reviewing",
    "interested",
    "applied",
    "interview",
    "offer",
    "rejected",
    "passed"
]

# Nick's profile summary for AI matching
PROFILE_SUMMARY = """
Nick Stafford - AI Financial Systems Engineer

UNIQUE VALUE: Rare combination of CS degree + Masters in Accounting + AI expertise.
Can bridge the gap between finance teams and engineering, automating complex financial processes.

CURRENT ROLE: AI Financial Systems Engineer at Cruize (Aug 2025 - Present)
- Built AI-driven financial intelligence agents
- Automated financial analysis, reporting, capital allocation recommendations
- Python pipelines processing 500K+ monthly transactions from Sage Intacct
- Anomaly detection for audit accuracy

PREVIOUS:
- Operating Architect at RCN (forecasting models, government contracts)
- Software Engineer at Publicis Sapient (QuickBooks/SAP/Snowflake integrations)
- Corporate Accounting Associate at Stone Pine (GAAP, private equity funds)

EDUCATION:
- B.S. Computer Science, University of Colorado Boulder (2022)
- B.S. & M.S. Accounting, University of Colorado Boulder (2016, 2017)

TECHNICAL SKILLS:
- Languages: Python, SQL, Excel/VBA
- Platforms: Sage Intacct, QuickBooks, SAP, NetSuite, Oracle, Palantir, Power BI, Tableau
- AI/ML: LLM integration, AI agents, intelligent automation
- Automation: ETL pipelines, RPA (UiPath, Alteryx), REST APIs

IDEAL ROLES:
- AI Financial Systems Engineer
- Financial Automation Engineer
- Solutions Architect (FinTech)
- AI/ML Engineer with finance focus
- Any role combining AI + Finance + Automation

LOCATION: Seattle, WA (open to remote or nationwide relocation)
SALARY: $100k+ minimum
"""
