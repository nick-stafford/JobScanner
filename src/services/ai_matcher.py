"""
AI-powered job matching and cover letter generation using Groq
"""
import json
from typing import Dict, Optional, Tuple
from groq import Groq
from src.utils.config import GROQ_API_KEY, GROQ_MODEL, PROFILE_SUMMARY, CORE_SKILLS


def get_groq_client():
    """Get Groq client instance."""
    if not GROQ_API_KEY:
        return None
    return Groq(api_key=GROQ_API_KEY)


def score_job_match(job: Dict) -> Tuple[int, str, str]:
    """
    Score how well a job matches Nick's profile.
    Returns: (score 0-100, match_reasons, recommended_resume)
    """
    client = get_groq_client()
    if not client:
        return 50, "AI scoring unavailable", "main"

    job_text = f"""
    Title: {job.get('title', 'Unknown')}
    Company: {job.get('company', 'Unknown')}
    Location: {job.get('location', 'Unknown')}
    Salary: {job.get('salary_text', 'Not specified')}
    Description: {job.get('description', 'No description')[:2000]}
    """

    prompt = f"""Analyze this job posting and score how well it matches this candidate's profile.

CANDIDATE PROFILE:
{PROFILE_SUMMARY}

JOB POSTING:
{job_text}

Respond with a JSON object containing:
1. "score": Integer 0-100 (100 = perfect match)
   - 90-100: Perfect match (financial AI/automation, matches experience exactly)
   - 70-89: Strong match (AI role or finance role, good skill overlap)
   - 50-69: Moderate match (some relevant skills, could be interesting)
   - 30-49: Weak match (few overlapping skills)
   - 0-29: Poor match (unrelated field)

2. "reasons": List of 3-5 bullet points explaining why this is/isn't a good match

3. "recommended_resume": Which resume version to use:
   - "financial_automation" for finance/accounting/ERP roles
   - "ai_ml" for AI/ML engineering roles
   - "solutions_architect" for architecture/consulting roles
   - "main" for hybrid or general roles

4. "key_requirements": List of key requirements from the job posting

5. "missing_skills": Any required skills the candidate may lack

Respond ONLY with valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )

        result_text = response.choices[0].message.content.strip()

        # Clean up JSON if wrapped in markdown
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        result_text = result_text.strip()

        result = json.loads(result_text)

        score = min(100, max(0, int(result.get("score", 50))))
        reasons = "\n".join([f"• {r}" for r in result.get("reasons", [])])
        recommended = result.get("recommended_resume", "main")

        return score, reasons, recommended

    except Exception as e:
        print(f"Error scoring job: {e}")
        return 50, f"Error scoring: {str(e)}", "main"


def generate_cover_letter(job: Dict, style: str = "professional") -> str:
    """
    Generate a customized cover letter for a specific job.
    """
    client = get_groq_client()
    if not client:
        return "Error: Groq API key not configured"

    job_text = f"""
    Title: {job.get('title', 'Unknown')}
    Company: {job.get('company', 'Unknown')}
    Location: {job.get('location', 'Unknown')}
    Description: {job.get('description', 'No description')[:3000]}
    """

    prompt = f"""Write a compelling cover letter for this job application.

CANDIDATE PROFILE:
{PROFILE_SUMMARY}

JOB POSTING:
{job_text}

INSTRUCTIONS:
1. Write a professional cover letter (3-4 paragraphs)
2. Highlight specific relevant experience from the candidate's background
3. Connect the candidate's unique value (CS + Accounting + AI) to the role
4. Mention specific achievements with metrics where relevant
5. Show enthusiasm for the company and role
6. Keep it concise but impactful
7. Do NOT include placeholder brackets like [Company Name] - use actual values
8. Do NOT include the date or addresses - just the letter body

Style: {style}

Write the cover letter now:"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error generating cover letter: {str(e)}"


def analyze_job_requirements(job: Dict) -> Dict:
    """
    Extract and analyze key requirements from a job posting.
    """
    client = get_groq_client()
    if not client:
        return {"error": "Groq API not configured"}

    prompt = f"""Analyze this job posting and extract key information.

JOB POSTING:
Title: {job.get('title', '')}
Company: {job.get('company', '')}
Description: {job.get('description', '')[:3000]}

Extract and return as JSON:
1. "required_skills": List of must-have skills
2. "preferred_skills": List of nice-to-have skills
3. "years_experience": Required years of experience (number or "not specified")
4. "education": Required education level
5. "key_responsibilities": Top 5 responsibilities
6. "red_flags": Any concerning requirements or red flags
7. "company_culture": Any hints about company culture
8. "remote_status": "remote", "hybrid", "onsite", or "unknown"

Respond ONLY with valid JSON."""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000
        )

        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]

        return json.loads(result_text.strip())

    except Exception as e:
        return {"error": str(e)}


def suggest_talking_points(job: Dict) -> str:
    """
    Generate interview talking points for a specific job.
    """
    client = get_groq_client()
    if not client:
        return "Error: Groq API not configured"

    prompt = f"""Based on this job and candidate profile, suggest key talking points for an interview.

CANDIDATE:
{PROFILE_SUMMARY}

JOB:
Title: {job.get('title', '')}
Company: {job.get('company', '')}
Description: {job.get('description', '')[:2000]}

Provide:
1. 5 key talking points that highlight relevant experience
2. 3 questions to ask the interviewer
3. 2-3 potential weaknesses to prepare for
4. A brief "elevator pitch" for this specific role

Format with clear headers and bullet points."""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1500
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"
