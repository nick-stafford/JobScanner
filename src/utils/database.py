"""
SQLite database operations for JobScanner
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DATABASE_PATH = "data/jobs.db"


def get_connection():
    """Get database connection, creating tables if needed."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    create_tables(conn)
    return conn


def create_tables(conn):
    """Create database tables if they don't exist."""
    cursor = conn.cursor()

    # Jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            salary_min INTEGER,
            salary_max INTEGER,
            salary_text TEXT,
            job_url TEXT UNIQUE,
            description TEXT,
            posted_date TEXT,
            scraped_date TEXT DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'indeed',
            search_keyword TEXT,
            match_score INTEGER DEFAULT 0,
            match_reasons TEXT,
            recommended_resume TEXT,
            status TEXT DEFAULT 'new',
            cover_letter_path TEXT,
            notes TEXT,
            applied_date TEXT,
            response_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Search history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            location TEXT,
            results_count INTEGER,
            searched_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()


def add_job(conn, job_data: Dict[str, Any]) -> int:
    """Add a new job to the database. Returns job ID."""
    cursor = conn.cursor()

    # Check if job URL already exists
    cursor.execute("SELECT id FROM jobs WHERE job_url = ?", (job_data.get("job_url"),))
    existing = cursor.fetchone()
    if existing:
        return existing["id"]

    columns = ", ".join(job_data.keys())
    placeholders = ", ".join(["?" for _ in job_data])
    values = list(job_data.values())

    cursor.execute(f"INSERT INTO jobs ({columns}) VALUES ({placeholders})", values)
    conn.commit()
    return cursor.lastrowid


def update_job(conn, job_id: int, updates: Dict[str, Any]):
    """Update a job record."""
    cursor = conn.cursor()
    updates["updated_at"] = datetime.now().isoformat()

    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [job_id]

    cursor.execute(f"UPDATE jobs SET {set_clause} WHERE id = ?", values)
    conn.commit()


def get_job(conn, job_id: int) -> Optional[Dict]:
    """Get a single job by ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_all_jobs(conn, status: Optional[str] = None, min_score: int = 0) -> List[Dict]:
    """Get all jobs, optionally filtered by status and minimum score."""
    cursor = conn.cursor()

    query = "SELECT * FROM jobs WHERE match_score >= ?"
    params = [min_score]

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY match_score DESC, scraped_date DESC"

    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]


def get_jobs_by_status(conn, status: str) -> List[Dict]:
    """Get jobs filtered by status."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM jobs WHERE status = ? ORDER BY match_score DESC",
        (status,)
    )
    return [dict(row) for row in cursor.fetchall()]


def get_job_stats(conn) -> Dict[str, int]:
    """Get job statistics by status."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM jobs
        GROUP BY status
    """)
    stats = {row["status"]: row["count"] for row in cursor.fetchall()}

    # Add total and average score
    cursor.execute("SELECT COUNT(*) as total, AVG(match_score) as avg_score FROM jobs")
    row = cursor.fetchone()
    stats["total"] = row["total"]
    stats["avg_score"] = round(row["avg_score"] or 0, 1)

    return stats


def search_jobs(conn, query: str) -> List[Dict]:
    """Search jobs by title, company, or description."""
    cursor = conn.cursor()
    search_term = f"%{query}%"
    cursor.execute("""
        SELECT * FROM jobs
        WHERE title LIKE ? OR company LIKE ? OR description LIKE ?
        ORDER BY match_score DESC
    """, (search_term, search_term, search_term))
    return [dict(row) for row in cursor.fetchall()]


def delete_job(conn, job_id: int):
    """Delete a job by ID."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()


def log_search(conn, keyword: str, location: str, results_count: int):
    """Log a search to history."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO search_history (keyword, location, results_count) VALUES (?, ?, ?)",
        (keyword, location, results_count)
    )
    conn.commit()


def get_top_companies(conn, limit: int = 10) -> List[Dict]:
    """Get companies with most job listings."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT company, COUNT(*) as job_count, AVG(match_score) as avg_score
        FROM jobs
        GROUP BY company
        ORDER BY job_count DESC
        LIMIT ?
    """, (limit,))
    return [dict(row) for row in cursor.fetchall()]
