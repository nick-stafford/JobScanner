"""
Job search service using FREE APIs (no account needed)
- RemoteOK: Remote tech/dev jobs
- Remotive: Remote jobs across categories
- Arbeitnow: EU and remote jobs
- Plus: Manual URL entry for LinkedIn/Indeed
"""
import requests
from typing import List, Dict, Optional
import re
import time
from src.utils.config import MIN_SALARY


def search_remoteok(keyword: str = "", limit: int = 50) -> List[Dict]:
    """
    Search RemoteOK - FREE, no API key needed.
    Great for remote tech jobs.
    """
    url = "https://remoteok.com/api"

    headers = {
        "User-Agent": "JobScanner/1.0 (job search assistant)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # First item is metadata, skip it
        jobs_data = data[1:] if len(data) > 1 else []

        jobs = []
        keyword_lower = keyword.lower() if keyword else ""

        for job in jobs_data[:limit * 2]:  # Get more, filter later
            title = job.get("position", "")
            company = job.get("company", "")
            description = job.get("description", "")
            tags = " ".join(job.get("tags", []))

            # Filter by keyword if provided
            if keyword_lower:
                searchable = f"{title} {company} {description} {tags}".lower()
                if keyword_lower not in searchable:
                    continue

            salary_min, salary_max = parse_remoteok_salary(job)

            jobs.append({
                "title": title,
                "company": company,
                "location": job.get("location", "Remote"),
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_text": job.get("salary", ""),
                "job_url": job.get("url", f"https://remoteok.com/remote-jobs/{job.get('id', '')}"),
                "description": description[:3000],
                "posted_date": job.get("date", ""),
                "source": "remoteok",
                "search_keyword": keyword or "all",
                "tags": tags
            })

            if len(jobs) >= limit:
                break

        return jobs

    except Exception as e:
        print(f"Error searching RemoteOK: {e}")
        return []


def search_remotive(keyword: str = "", category: str = "") -> List[Dict]:
    """
    Search Remotive - FREE, no API key needed.
    Categories: software-dev, data, finance, marketing, etc.
    """
    url = "https://remotive.com/api/remote-jobs"

    params = {}
    if category:
        params["category"] = category
    if keyword:
        params["search"] = keyword

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        jobs = []
        for job in data.get("jobs", [])[:50]:
            salary_text = job.get("salary", "")
            salary_min, salary_max = parse_salary_text(salary_text)

            jobs.append({
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "location": job.get("candidate_required_location", "Remote"),
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_text": salary_text,
                "job_url": job.get("url", ""),
                "description": job.get("description", "")[:3000],
                "posted_date": job.get("publication_date", ""),
                "source": "remotive",
                "search_keyword": keyword or category or "all",
                "tags": job.get("tags", [])
            })

        return jobs

    except Exception as e:
        print(f"Error searching Remotive: {e}")
        return []


def search_arbeitnow(keyword: str = "") -> List[Dict]:
    """
    Search Arbeitnow - FREE, no API key needed.
    Good for EU and remote jobs.
    """
    url = "https://www.arbeitnow.com/api/job-board-api"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        jobs = []
        keyword_lower = keyword.lower() if keyword else ""

        for job in data.get("data", [])[:50]:
            title = job.get("title", "")
            company = job.get("company_name", "")
            description = job.get("description", "")
            tags = " ".join(job.get("tags", []))

            # Filter by keyword if provided
            if keyword_lower:
                searchable = f"{title} {company} {description} {tags}".lower()
                if keyword_lower not in searchable:
                    continue

            jobs.append({
                "title": title,
                "company": company,
                "location": job.get("location", "Remote"),
                "salary_min": None,
                "salary_max": None,
                "salary_text": "",
                "job_url": job.get("url", ""),
                "description": description[:3000],
                "posted_date": job.get("created_at", ""),
                "source": "arbeitnow",
                "search_keyword": keyword or "all",
                "tags": tags
            })

        return jobs

    except Exception as e:
        print(f"Error searching Arbeitnow: {e}")
        return []


def search_findwork(keyword: str = "") -> List[Dict]:
    """
    Search FindWork.dev - FREE tier, no API key for basic search.
    Tech/startup focused.
    """
    url = "https://findwork.dev/api/jobs/"

    params = {}
    if keyword:
        params["search"] = keyword

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        jobs = []
        for job in data.get("results", [])[:50]:
            jobs.append({
                "title": job.get("role", ""),
                "company": job.get("company_name", ""),
                "location": job.get("location", "Remote"),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "salary_text": f"${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}" if job.get("salary_min") else "",
                "job_url": job.get("url", ""),
                "description": job.get("text", "")[:3000],
                "posted_date": job.get("date_posted", ""),
                "source": "findwork",
                "search_keyword": keyword or "all",
                "tags": ", ".join(job.get("keywords", []))
            })

        return jobs

    except Exception as e:
        print(f"Error searching FindWork: {e}")
        return []


def search_all_free_sources(keyword: str = "", limit_per_source: int = 30) -> List[Dict]:
    """
    Search all free job APIs and combine results.
    No API keys needed!
    """
    all_jobs = []

    # RemoteOK - great for tech
    print(f"Searching RemoteOK for '{keyword}'...")
    remoteok_jobs = search_remoteok(keyword, limit_per_source)
    all_jobs.extend(remoteok_jobs)
    time.sleep(0.5)  # Be nice to the APIs

    # Remotive - good variety
    print(f"Searching Remotive for '{keyword}'...")
    remotive_jobs = search_remotive(keyword)
    all_jobs.extend(remotive_jobs)
    time.sleep(0.5)

    # Arbeitnow
    print(f"Searching Arbeitnow for '{keyword}'...")
    arbeitnow_jobs = search_arbeitnow(keyword)
    all_jobs.extend(arbeitnow_jobs)

    # Deduplicate by job URL
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        url = job.get("job_url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_jobs.append(job)
        elif not url:
            unique_jobs.append(job)

    return unique_jobs


def parse_remoteok_salary(job: Dict) -> tuple:
    """Parse salary from RemoteOK job data."""
    salary_text = job.get("salary", "")
    if salary_text:
        return parse_salary_text(salary_text)

    # Try min/max fields
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")

    if salary_min or salary_max:
        return (
            int(salary_min) if salary_min else None,
            int(salary_max) if salary_max else None
        )

    return None, None


def parse_salary_text(salary_text: str) -> tuple:
    """
    Parse salary text to extract min/max values.
    Returns (min, max)
    """
    if not salary_text:
        return None, None

    # Clean and normalize
    text = salary_text.replace(",", "").replace("$", "").lower()

    # Try to find salary numbers
    numbers = re.findall(r'(\d+(?:\.\d+)?)\s*k?', text)

    if not numbers:
        return None, None

    # Convert to integers (handle 'k' suffix)
    values = []
    for num in numbers:
        val = float(num)
        if val < 1000:  # Likely in thousands (e.g., "150k")
            val *= 1000
        values.append(int(val))

    if len(values) >= 2:
        return min(values), max(values)
    elif len(values) == 1:
        return values[0], values[0]

    return None, None


def filter_by_salary(jobs: List[Dict], min_salary: int = MIN_SALARY) -> List[Dict]:
    """Filter jobs by minimum salary."""
    filtered = []
    for job in jobs:
        # Include if salary meets minimum OR if no salary listed (might still be good)
        if job.get("salary_max") is None or job.get("salary_max", 0) >= min_salary:
            filtered.append(job)
    return filtered


def add_job_manually(url: str, title: str = "", company: str = "", description: str = "") -> Dict:
    """
    Create a job entry from a manually provided URL.
    User can paste LinkedIn/Indeed/any job URLs.
    """
    return {
        "title": title,
        "company": company,
        "location": "",
        "salary_min": None,
        "salary_max": None,
        "salary_text": "",
        "job_url": url,
        "description": description,
        "posted_date": "",
        "source": "manual",
        "search_keyword": "manual_entry",
    }


# For backwards compatibility
def search_google_jobs(*args, **kwargs):
    """Deprecated: Use search_all_free_sources instead."""
    return search_all_free_sources(args[0] if args else "", 20)


def search_indeed(*args, **kwargs):
    """Deprecated: Use search_all_free_sources instead."""
    return search_all_free_sources(args[0] if args else "", 20)
