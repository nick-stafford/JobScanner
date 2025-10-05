"""
JobScanner - AI-Powered Job Search & Application Assistant
Streamlit App for Nick Stafford
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Add src to path
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.database import (
    get_connection, add_job, update_job, get_job, get_all_jobs,
    get_jobs_by_status, get_job_stats, search_jobs, delete_job, log_search
)
from src.utils.config import SEARCH_KEYWORDS, JOB_STATUSES, GROQ_API_KEY
from src.services.job_search import search_all_free_sources, search_remoteok, search_remotive, add_job_manually, filter_by_salary
from src.services.ai_matcher import score_job_match, generate_cover_letter, analyze_job_requirements, suggest_talking_points
from src.services.pdf_generator import generate_cover_letter_pdf

# Page config
st.set_page_config(
    page_title="JobScanner - Nick Stafford",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #888;
        font-size: 1.1rem;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .score-high { color: #00c853; font-weight: bold; }
    .score-medium { color: #ffc107; font-weight: bold; }
    .score-low { color: #ff5252; font-weight: bold; }
    .status-new { background-color: #e3f2fd; padding: 2px 8px; border-radius: 4px; }
    .status-applied { background-color: #e8f5e9; padding: 2px 8px; border-radius: 4px; }
    .status-interview { background-color: #fff3e0; padding: 2px 8px; border-radius: 4px; }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Sidebar navigation
    st.sidebar.markdown("## 🎯 JobScanner")
    st.sidebar.markdown("*AI-Powered Job Search*")
    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "🔍 Search Jobs", "📋 All Jobs", "➕ Add Job", "⚙️ Settings"],
        label_visibility="collapsed"
    )

    # API Status indicators
    st.sidebar.divider()
    st.sidebar.markdown("### Status")
    if GROQ_API_KEY:
        st.sidebar.success("✅ Groq AI Connected")
    else:
        st.sidebar.error("❌ Groq API Key Missing")

    st.sidebar.info("🆓 Free Job APIs Active")

    # Route to page
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🔍 Search Jobs":
        show_search()
    elif page == "📋 All Jobs":
        show_all_jobs()
    elif page == "➕ Add Job":
        show_add_job()
    elif page == "⚙️ Settings":
        show_settings()


def show_dashboard():
    """Main dashboard with stats and top jobs."""
    st.markdown('<p class="main-header">JobScanner Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered job matching for Nick Stafford</p>', unsafe_allow_html=True)

    conn = get_connection()
    stats = get_job_stats(conn)

    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Jobs", stats.get("total", 0))
    with col2:
        st.metric("New", stats.get("new", 0))
    with col3:
        st.metric("Applied", stats.get("applied", 0))
    with col4:
        st.metric("Interviews", stats.get("interview", 0))
    with col5:
        st.metric("Avg Match Score", f"{stats.get('avg_score', 0):.0f}%")

    st.divider()

    # Two columns: Top Matches and Recent Activity
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎯 Top Matching Jobs")
        top_jobs = get_all_jobs(conn, min_score=70)[:10]

        if top_jobs:
            for job in top_jobs:
                with st.expander(f"**{job['title']}** at {job['company']} - {job['match_score']}% match"):
                    st.write(f"📍 {job['location']}")
                    st.write(f"💰 {job['salary_text'] or 'Not specified'}")
                    st.write(f"🔗 [View Job]({job['job_url']})")
                    st.write("**Match Reasons:**")
                    st.write(job['match_reasons'] or "No analysis yet")

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("Generate Cover Letter", key=f"cl_{job['id']}"):
                            with st.spinner("Generating..."):
                                letter = generate_cover_letter(job)
                                pdf_path = generate_cover_letter_pdf(
                                    letter, job['company'], job['title']
                                )
                                update_job(conn, job['id'], {"cover_letter_path": pdf_path})
                                st.success(f"Saved to: {pdf_path}")
                                st.text_area("Preview:", letter, height=200)
                    with col_b:
                        new_status = st.selectbox(
                            "Status",
                            JOB_STATUSES,
                            index=JOB_STATUSES.index(job['status']),
                            key=f"status_{job['id']}"
                        )
                        if new_status != job['status']:
                            update_job(conn, job['id'], {"status": new_status})
                            st.rerun()
                    with col_c:
                        if st.button("Delete", key=f"del_{job['id']}"):
                            delete_job(conn, job['id'])
                            st.rerun()
        else:
            st.info("No high-matching jobs yet. Try searching for jobs!")

    with col2:
        st.subheader("📈 Status Breakdown")
        status_data = {s: stats.get(s, 0) for s in JOB_STATUSES if stats.get(s, 0) > 0}
        if status_data:
            st.bar_chart(status_data)
        else:
            st.info("No jobs tracked yet")

        st.subheader("🚀 Quick Actions")
        if st.button("🔍 Run Quick Search", use_container_width=True):
            st.session_state.page = "search"
            st.rerun()

        if st.button("➕ Add Job Manually", use_container_width=True):
            st.session_state.page = "add"
            st.rerun()

    conn.close()


def show_search():
    """Job search page using FREE APIs (no account needed)."""
    st.header("🔍 Search Jobs")

    st.success("🆓 Using free job APIs - no account needed!")
    st.caption("Sources: RemoteOK, Remotive, Arbeitnow (mostly remote/tech jobs)")

    # Search options
    search_mode = st.radio(
        "Search Mode",
        ["🚀 Quick Search (All Sources)", "🔎 Custom Keyword Search", "📋 Browse by Category"],
        horizontal=True
    )

    if search_mode == "🚀 Quick Search (All Sources)":
        st.info("Searches RemoteOK, Remotive, and Arbeitnow for AI, Finance, and Automation jobs")

        col1, col2 = st.columns(2)
        with col1:
            keywords_to_search = st.multiselect(
                "Keywords to search",
                ["AI", "Machine Learning", "Finance", "Automation", "Python", "Data Engineer", "FinTech", "RPA"],
                default=["AI", "Finance", "Automation"]
            )
        with col2:
            score_jobs = st.checkbox("AI Score each job (slower but better matching)", value=True)

        if st.button("🚀 Start Search", type="primary"):
            conn = get_connection()
            all_results = []
            progress = st.progress(0)
            status = st.empty()

            for i, keyword in enumerate(keywords_to_search):
                status.text(f"Searching for '{keyword}'...")
                progress.progress((i + 1) / len(keywords_to_search))

                jobs = search_all_free_sources(keyword, limit_per_source=20)
                all_results.extend(jobs)
                log_search(conn, keyword, "Remote", len(jobs))

            # Deduplicate
            seen_urls = set()
            unique_jobs = []
            for job in all_results:
                url = job.get("job_url", "")
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_jobs.append(job)

            status.text("Processing jobs...")

            # Score and save
            saved_count = 0
            for i, job in enumerate(unique_jobs):
                if score_jobs:
                    status.text(f"AI scoring job {i+1}/{len(unique_jobs)}...")
                    score, reasons, resume = score_job_match(job)
                    job['match_score'] = score
                    job['match_reasons'] = reasons
                    job['recommended_resume'] = resume
                else:
                    job['match_score'] = 50
                    job['match_reasons'] = "Not AI scored yet"
                    job['recommended_resume'] = "main"

                add_job(conn, job)
                saved_count += 1

            progress.progress(1.0)
            status.text("")
            st.success(f"Found {len(all_results)} jobs, {saved_count} unique jobs saved!")
            st.balloons()
            conn.close()

    elif search_mode == "🔎 Custom Keyword Search":
        custom_query = st.text_input("Search Query", placeholder="e.g., AI Engineer, Python Developer, etc.")

        if st.button("Search", type="primary") and custom_query:
            conn = get_connection()
            with st.spinner(f"Searching for '{custom_query}'..."):
                jobs = search_all_free_sources(custom_query, limit_per_source=30)

                saved = 0
                for job in jobs:
                    score, reasons, resume = score_job_match(job)
                    job['match_score'] = score
                    job['match_reasons'] = reasons
                    job['recommended_resume'] = resume
                    add_job(conn, job)
                    saved += 1

                log_search(conn, custom_query, "Remote", len(jobs))

            st.success(f"Found and saved {saved} jobs!")
            conn.close()

    else:  # Browse by Category
        st.subheader("Browse Remotive Categories")
        categories = {
            "Software Development": "software-dev",
            "Data / Analytics": "data",
            "Finance / Legal": "finance-legal",
            "DevOps / Sysadmin": "devops",
            "Product": "product",
            "Marketing": "marketing",
            "Sales": "sales",
            "Customer Support": "customer-support",
            "All Jobs": ""
        }

        selected_cat = st.selectbox("Category", list(categories.keys()))

        if st.button("Browse Category", type="primary"):
            conn = get_connection()
            with st.spinner(f"Fetching {selected_cat} jobs..."):
                jobs = search_remotive(category=categories[selected_cat])

                saved = 0
                for job in jobs:
                    score, reasons, resume = score_job_match(job)
                    job['match_score'] = score
                    job['match_reasons'] = reasons
                    job['recommended_resume'] = resume
                    add_job(conn, job)
                    saved += 1

            st.success(f"Found and saved {saved} jobs in {selected_cat}!")
            conn.close()


def show_all_jobs():
    """View and manage all jobs."""
    st.header("📋 All Jobs")

    conn = get_connection()

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + JOB_STATUSES)
    with col2:
        min_score = st.slider("Minimum Match Score", 0, 100, 0)
    with col3:
        search_query = st.text_input("Search", placeholder="Title, company...")
    with col4:
        sort_by = st.selectbox("Sort by", ["Match Score", "Date Added", "Company"])

    # Get jobs
    if search_query:
        jobs = search_jobs(conn, search_query)
    elif status_filter != "All":
        jobs = get_jobs_by_status(conn, status_filter)
    else:
        jobs = get_all_jobs(conn, min_score=min_score)

    # Sort
    if sort_by == "Match Score":
        jobs = sorted(jobs, key=lambda x: x.get('match_score', 0), reverse=True)
    elif sort_by == "Date Added":
        jobs = sorted(jobs, key=lambda x: x.get('scraped_date', ''), reverse=True)
    elif sort_by == "Company":
        jobs = sorted(jobs, key=lambda x: x.get('company', ''))

    st.write(f"**{len(jobs)} jobs found**")

    # Display as table with actions
    if jobs:
        for job in jobs:
            score = job.get('match_score', 0)
            score_class = "score-high" if score >= 70 else "score-medium" if score >= 50 else "score-low"

            with st.expander(
                f"**{job['title']}** | {job['company']} | "
                f"<span class='{score_class}'>{score}%</span> | {job['status']}",
                expanded=False
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"📍 **Location:** {job['location']}")
                    st.write(f"💰 **Salary:** {job['salary_text'] or 'Not specified'}")
                    st.write(f"🔗 **URL:** [{job['job_url'][:50]}...]({job['job_url']})")
                    st.write(f"📅 **Added:** {job['scraped_date']}")
                    st.write(f"📄 **Recommended Resume:** {job['recommended_resume']}")

                    st.write("**Match Analysis:**")
                    st.write(job['match_reasons'] or "Not analyzed yet")

                    if job.get('description'):
                        with st.expander("Full Description"):
                            st.write(job['description'])

                with col2:
                    # Status update
                    new_status = st.selectbox(
                        "Update Status",
                        JOB_STATUSES,
                        index=JOB_STATUSES.index(job['status']),
                        key=f"st_{job['id']}"
                    )
                    if new_status != job['status']:
                        update_job(conn, job['id'], {"status": new_status})
                        st.rerun()

                    # Notes
                    notes = st.text_area(
                        "Notes",
                        value=job.get('notes') or "",
                        key=f"notes_{job['id']}"
                    )
                    if st.button("Save Notes", key=f"save_notes_{job['id']}"):
                        update_job(conn, job['id'], {"notes": notes})
                        st.success("Saved!")

                    st.divider()

                    # Actions
                    if st.button("📝 Generate Cover Letter", key=f"gen_{job['id']}"):
                        with st.spinner("Generating with AI..."):
                            letter = generate_cover_letter(job)
                            pdf_path = generate_cover_letter_pdf(
                                letter, job['company'], job['title']
                            )
                            update_job(conn, job['id'], {"cover_letter_path": pdf_path})
                            st.success(f"Saved: {pdf_path}")
                            st.text_area("Cover Letter:", letter, height=300)

                    if st.button("🎤 Interview Prep", key=f"prep_{job['id']}"):
                        with st.spinner("Generating talking points..."):
                            points = suggest_talking_points(job)
                            st.markdown(points)

                    if st.button("🔄 Re-analyze", key=f"re_{job['id']}"):
                        with st.spinner("Re-scoring..."):
                            score, reasons, resume = score_job_match(job)
                            update_job(conn, job['id'], {
                                "match_score": score,
                                "match_reasons": reasons,
                                "recommended_resume": resume
                            })
                            st.rerun()

                    if st.button("🗑️ Delete", key=f"del_{job['id']}"):
                        delete_job(conn, job['id'])
                        st.rerun()

    conn.close()


def show_add_job():
    """Manually add a job."""
    st.header("➕ Add Job Manually")
    st.write("Paste a job URL from LinkedIn, Indeed, or any job board")

    with st.form("add_job_form"):
        url = st.text_input("Job URL*", placeholder="https://www.linkedin.com/jobs/view/...")
        title = st.text_input("Job Title*", placeholder="AI Financial Systems Engineer")
        company = st.text_input("Company*", placeholder="Acme Corp")
        location = st.text_input("Location", placeholder="Remote")
        salary = st.text_input("Salary (if known)", placeholder="$150,000 - $200,000")
        description = st.text_area("Job Description", placeholder="Paste the full job description here...", height=200)

        submitted = st.form_submit_button("Add & Analyze Job", type="primary")

        if submitted:
            if not url or not title or not company:
                st.error("Please fill in URL, Title, and Company")
            else:
                conn = get_connection()

                job_data = {
                    "title": title,
                    "company": company,
                    "location": location,
                    "salary_text": salary,
                    "job_url": url,
                    "description": description,
                    "source": "manual",
                    "search_keyword": "manual_entry"
                }

                # Score the job
                with st.spinner("Analyzing job match..."):
                    score, reasons, resume = score_job_match(job_data)
                    job_data['match_score'] = score
                    job_data['match_reasons'] = reasons
                    job_data['recommended_resume'] = resume

                job_id = add_job(conn, job_data)
                conn.close()

                st.success(f"Job added with {score}% match score!")
                st.write("**Match Analysis:**")
                st.write(reasons)
                st.write(f"**Recommended Resume:** {resume}")


def show_settings():
    """Settings page."""
    st.header("⚙️ Settings")

    st.subheader("API Configuration")
    st.info("🆓 Job search uses FREE APIs (no key needed). Only Groq needs a key for AI features.")

    with st.form("api_settings"):
        groq_key = st.text_input(
            "Groq API Key",
            value=GROQ_API_KEY or "",
            type="password",
            help="Get FREE from https://console.groq.com"
        )

        if st.form_submit_button("Save to .env"):
            env_content = f"""# JobScanner API Keys
# Groq is FREE - get key at https://console.groq.com
GROQ_API_KEY={groq_key}
"""
            with open(".env", "w") as f:
                f.write(env_content)
            st.success("Saved! Restart the app to apply changes.")

    st.divider()

    st.subheader("Database")
    conn = get_connection()
    stats = get_job_stats(conn)
    st.write(f"Total jobs in database: {stats.get('total', 0)}")

    if st.button("Export Jobs to CSV"):
        jobs = get_all_jobs(conn)
        if jobs:
            df = pd.DataFrame(jobs)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "jobs_export.csv",
                "text/csv"
            )

    if st.button("Clear All Jobs", type="secondary"):
        if st.checkbox("I understand this will delete all job data"):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM jobs")
            conn.commit()
            st.success("All jobs deleted")
            st.rerun()

    conn.close()

    st.divider()

    st.subheader("Search Keywords")
    st.write("These keywords are used for quick search:")
    for i, kw in enumerate(SEARCH_KEYWORDS, 1):
        st.write(f"{i}. {kw}")


if __name__ == "__main__":
    main()
