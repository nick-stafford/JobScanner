"""
PDF Cover Letter Generator
"""
import os
from datetime import datetime
from fpdf import FPDF
from typing import Optional


class CoverLetterPDF(FPDF):
    """Custom PDF class for cover letters."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        """Add header with contact info."""
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, "Nick Stafford", ln=True, align="C")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, "nicholas.alexander.stafford@gmail.com | (303) 881-6022 | Seattle, WA", ln=True, align="C")
        self.cell(0, 5, "linkedin.com/in/nickastafford23", ln=True, align="C")
        self.set_text_color(0, 0, 0)
        self.ln(10)

    def footer(self):
        """Add page number footer."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_cover_letter_pdf(
    cover_letter_text: str,
    company: str,
    job_title: str,
    output_dir: str = "output/cover_letters"
) -> str:
    """
    Generate a PDF cover letter.
    Returns the path to the generated PDF.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Create filename
    safe_company = "".join(c for c in company if c.isalnum() or c in " -_")[:30]
    safe_title = "".join(c for c in job_title if c.isalnum() or c in " -_")[:30]
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"Cover_Letter_{safe_company}_{safe_title}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    # Create PDF
    pdf = CoverLetterPDF()
    pdf.add_page()

    # Date
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, datetime.now().strftime("%B %d, %Y"), ln=True)
    pdf.ln(5)

    # Hiring info
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, f"RE: {job_title}", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, company, ln=True)
    pdf.ln(8)

    # Salutation
    pdf.cell(0, 6, "Dear Hiring Manager,", ln=True)
    pdf.ln(5)

    # Body - split into paragraphs
    pdf.set_font("Helvetica", "", 11)
    paragraphs = cover_letter_text.split("\n\n")

    for para in paragraphs:
        # Clean up the paragraph
        para = para.strip()
        if not para:
            continue

        # Skip if it looks like a salutation we already added
        if para.lower().startswith("dear"):
            continue

        # Handle line breaks within paragraph
        para = para.replace("\n", " ")

        # Write paragraph with word wrap
        pdf.multi_cell(0, 6, para)
        pdf.ln(4)

    # Closing
    pdf.ln(5)
    pdf.cell(0, 6, "Sincerely,", ln=True)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Nick Stafford", ln=True)

    # Save PDF
    pdf.output(filepath)

    return filepath


def generate_quick_intro_pdf(
    company: str,
    job_title: str,
    key_points: list,
    output_dir: str = "output/cover_letters"
) -> str:
    """
    Generate a quick 1-page intro/pitch document.
    """
    os.makedirs(output_dir, exist_ok=True)

    safe_company = "".join(c for c in company if c.isalnum() or c in " -_")[:30]
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"Quick_Intro_{safe_company}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    pdf = CoverLetterPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"Why I'm a Great Fit for {job_title}", ln=True, align="C")
    pdf.cell(0, 8, f"at {company}", ln=True, align="C")
    pdf.ln(10)

    # Key points
    pdf.set_font("Helvetica", "", 11)
    for point in key_points:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(5, 6, chr(149))  # Bullet
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, f" {point}")
        pdf.ln(2)

    # Value proposition
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "My Unique Value:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6,
        "I bring a rare combination of Computer Science (B.S.), Accounting (B.S. & M.S.), "
        "and hands-on AI engineering experience. This allows me to bridge the gap between "
        "finance teams and engineering, building intelligent automation that truly understands "
        "business processes."
    )

    pdf.output(filepath)
    return filepath
