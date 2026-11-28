
import json
import hashlib
from pathlib import Path
from datetime import datetime

import streamlit as st
import plotly.express as px
from fpdf import FPDF

# Use the current PyMuPDF package name
try:
    import pymupdf
except ImportError:
    pymupdf = None

from auth_ui import render_login, render_admin_panel
from agent.lab8_parallel_swarm_agent import ParallelSwarmAgent
from tools.valuation_tool import ValuationTool
from tools.analysis_tool import AnalysisTool
from agent.difficulty_coverage_agent import DifficultyCoverageAgent


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Question Paper OBE Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
LESSON_PLAN_DIR = ROOT_DIR / "data" / "lesson_plans"
AGENT_DIR = ROOT_DIR / "agent"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# 2. PAGE DEFINITIONS
# ==========================================================


AVAILABLE_PAGES = [
    "Configure Examination",
    "Generate Scheme of Valuation",
    "Coverage & Quality Report",
    "Previous Question Papers",
    "Generated Documents",
    "Labs 1–14"
]



# ==========================================================
# 3. SESSION STATE
# ==========================================================


DEFAULT_STATE = {
    "authenticated": False,
    "active_page": "Home",
    "navigation_page": "Choose a page",
    "selected_subject": None
}


for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


def get_available_pages():
    pages = AVAILABLE_PAGES.copy()

    if st.session_state.get("user_role") == "admin":
        pages.append("Faculty Management")

    return pages


def navigate_to(page):
    """
    Queue navigation for the next Streamlit run.

    Do not directly modify navigation_page after its radio
    widget has been instantiated.
    """
    st.session_state.pending_page = page


def sync_navigation():
    """Synchronize sidebar selection with the active page."""
    selected = st.session_state.get(
        "navigation_page",
        "Choose a page"
    )

    if selected == "Choose a page":
        st.session_state.active_page = "Home"
    else:
        st.session_state.active_page = selected


def apply_pending_navigation():
    """
    Apply navigation before creating the sidebar radio widget.
    This prevents StreamlitAPIException.
    """
    if "pending_page" not in st.session_state:
        return

    target = st.session_state.pop("pending_page")
    pages = get_available_pages()

    if target == "Home":
        st.session_state.active_page = "Home"
        st.session_state.navigation_page = "Choose a page"

    elif target in pages:
        st.session_state.active_page = target
        st.session_state.navigation_page = target

    else:
        st.session_state.active_page = "Home"
        st.session_state.navigation_page = "Choose a page"


# ==========================================================
# 4. CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

/* ---------- Main application ---------- */

.stApp {
    background: linear-gradient(
        135deg,
        #f5f0ff 0%,
        #efe7fb 50%,
        #faf7ff 100%
    );
}

.block-container {
    max-width: 1500px;
    padding-top: 1.7rem;
    padding-bottom: 3rem;
}

h1 {
    color: #35204f !important;
    font-weight: 800 !important;
}

h2 {
    color: #4b2f6f !important;
    font-weight: 750 !important;
}

h3 {
    color: #533779 !important;
    font-weight: 700 !important;
}

p, label, li {
    color: #3c3150;
}

/* ---------- Sidebar ---------- */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #302044 0%,
        #493064 55%,
        #5c3e7d 100%
    );
}

[data-testid="stSidebar"] * {
    color: #ffffff;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] label {
    color: #f8fafc !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #dce7ff;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 8px 12px;
    margin-bottom: 6px;
    transition: 0.2s ease;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.17);
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.2);
}

/* ---------- Buttons ---------- */

.stButton > button {
    background: linear-gradient(
        110deg,
        #7953b5,
        #684099
    );
    color: #ffffff !important;
    border: none;
    border-radius: 11px;
    min-height: 44px;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(
        110deg,
        #603d91,
        #4f2f7b
    );
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(70,80,180,0.2);
}

/* ---------- Download buttons ---------- */

.stDownloadButton > button {
    background: #f1eafb;
    color: #4b2f6f !important;
    border: 1px solid #d5c3ed;
    border-radius: 10px;
    font-weight: 700;
}

.stDownloadButton > button:hover {
    background: #e7d9f7;
    color: #35204f !important;
}

/* ---------- Forms and inputs ---------- */

[data-testid="stForm"] {
    background: rgba(255,255,255,0.94);
    border: 1px solid #ddcfee;
    border-radius: 16px;
    padding: 22px;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    border-radius: 9px;
}

[data-testid="stSelectbox"] > div > div {
    border-radius: 9px;
}

/* ---------- Expanders ---------- */

[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #ddcfee;
    border-radius: 13px;
    margin-bottom: 10px;
}

/* ---------- Hero section ---------- */

.hero {
    background: linear-gradient(
        120deg,
        #302044 0%,
        #493064 55%,
        #7953b5 100%
    );
    padding: 40px;
    border-radius: 22px;
    color: white;
    margin-bottom: 26px;
    box-shadow: 0 12px 30px rgba(36,45,100,0.18);
}

.hero h1 {
    color: white !important;
    font-size: 36px;
    margin-bottom: 10px;
}

.hero p {
    color: #e0e8ff;
    font-size: 15px;
}

.hero-tag {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    padding: 7px 14px;
    border-radius: 30px;
    color: white;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 15px;
}

/* ---------- Feature cards ---------- */

.feature-card {
    background: #ffffff;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e4d8f2;
    min-height: 135px;
    box-shadow: 0 4px 15px rgba(37,59,115,0.06);
    margin-bottom: 12px;
    transition: 0.2s ease;
}

.feature-card:hover {
    border-color: #b69bd5;
    box-shadow: 0 8px 22px rgba(37,59,115,0.11);
}

.feature-card h3 {
    color: #533779 !important;
    font-size: 18px;
    margin-bottom: 8px;
}

.feature-card p {
    color: #554966;
    font-size: 13px;
    line-height: 1.6;
}

/* ---------- Small labels ---------- */

.section-label {
    color: #604582;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.3px;
    text-transform: uppercase;
}

/* ---------- Footer ---------- */

.footer {
    text-align: center;
    color: #685b78;
    font-size: 12px;
    padding: 30px 0 5px;
}

/* ---------- Metric cards ---------- */

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e4d8f2;
    border-radius: 13px;
    padding: 15px;
}

/* ---------- Alerts ---------- */

[data-testid="stAlert"] {
    border-radius: 11px;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/* ---------- Updated academic theme ---------- */

@keyframes app-rise-in {
    from {
        opacity: 0;
        transform: translateY(14px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes app-gradient-drift {
    0%, 100% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
}

.stApp {
    background: #f5f0ff;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stAppToolbar"],
.stApp > header {
    background: #f5f0ff !important;
    color: #4b2f6f !important;
}

[data-testid="stHeader"] *,
[data-testid="stToolbar"] *,
[data-testid="stAppToolbar"] * {
    color: #4b2f6f !important;
}

[data-testid="stAlert"] {
    background: #eee4fa !important;
    border: 1px solid #d5c3ed !important;
    color: #3c2454 !important;
}

[data-testid="stAlert"] *,
[data-testid="stAlert"] > div {
    color: #3c2454 !important;
    -webkit-text-fill-color: #3c2454 !important;
    background-color: transparent !important;
}

[data-testid="stMain"] {
    color: #2f1e43 !important;
}

[data-testid="stMain"] [data-testid="stMarkdownContainer"],
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] [data-testid="stWidgetLabel"],
[data-testid="stMain"] label,
[data-testid="stMain"] [data-testid="stMetricLabel"],
[data-testid="stMain"] [data-testid="stMetricValue"] {
    color: #2f1e43 !important;
}

[data-testid="stMain"] input,
[data-testid="stMain"] textarea,
[data-testid="stMain"] [role="combobox"] {
    color: #2f1e43 !important;
    background-color: #ffffff !important;
}

[data-testid="stMain"] input::placeholder,
[data-testid="stMain"] textarea::placeholder {
    color: #64748b !important;
    opacity: 1;
}

h1 {
    color: #35204f !important;
}

h2, h3 {
    color: #533779 !important;
}

[data-testid="stMain"] [data-testid="stButton"] > button,
[data-testid="stMain"] [data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(110deg, #7953b5, #684099) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stMain"] [data-testid="stButton"] > button *,
[data-testid="stMain"] [data-testid="stFormSubmitButton"] > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stMain"] [data-testid="stButton"] > button:hover,
[data-testid="stMain"] [data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(110deg, #603d91, #4f2f7b) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.stButton > button {
    background: linear-gradient(110deg, #7953b5, #684099);
    color: white !important;
    border: none;
    border-radius: 12px;
    min-height: 46px;
    font-weight: 700;
    transition: transform 180ms ease, box-shadow 180ms ease,
        background-color 180ms ease;
}

.stButton > button:hover {
    background: linear-gradient(110deg, #603d91, #4f2f7b);
    color: white !important;
    box-shadow: 0 5px 15px rgba(79, 47, 123, 0.24);
    transform: translateY(-2px);
}

.stButton > button,
.stButton > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(110deg, #7953b5, #684099) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: none !important;
    border-radius: 12px;
    min-height: 46px;
    font-weight: 700;
    opacity: 1 !important;
    box-shadow: 0 5px 14px rgba(79, 47, 123, 0.2);
}

[data-testid="stFormSubmitButton"] button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(110deg, #603d91, #4f2f7b) !important;
    color: #ffffff !important;
}

[data-testid="stFormSubmitButton"] button:disabled {
    background: #70558f !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    cursor: not-allowed;
}

.stDownloadButton > button {
    background: #f1eafb;
    color: #4b2f6f !important;
    border: 1px solid #d5c3ed;
    border-radius: 10px;
}

[data-testid="stForm"] {
    background: #ffffff;
    border: 1px solid #dce8ed;
    border-radius: 16px;
}

.subject-card {
    background: white;
    border: 1px solid #e4d8f2;
    border-radius: 16px;
    padding: 20px 16px;
    min-height: 150px;
    box-shadow: 0 4px 14px rgba(21, 52, 72, 0.06);
    margin-bottom: 10px;
    animation: app-rise-in 560ms ease-out both;
    transition: transform 200ms ease, box-shadow 200ms ease,
        border-color 200ms ease;
}

.subject-card:hover {
    transform: translateY(-4px);
    border-color: #b69bd5;
    box-shadow: 0 10px 24px rgba(21, 52, 72, 0.13);
}

.subject-card h3 {
    color: #533779 !important;
    font-size: 17px;
    margin-bottom: 8px;
}

.subject-card p {
    color: #554966;
    font-size: 13px;
    line-height: 1.5;
}

.page-hero {
    background: linear-gradient(120deg, #302044, #624184);
    background-size: 180% 180%;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 25px;
    color: white;
    animation:
        app-rise-in 560ms ease-out both,
        app-gradient-drift 20s ease-in-out infinite;
    transition: transform 200ms ease, box-shadow 200ms ease;
}

.page-hero:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 28px rgba(21, 52, 72, 0.14);
}

.page-hero h1 {
    color: white !important;
    font-size: 32px;
}

.page-hero p {
    color: #e1f2f1;
    margin-bottom: 0;
}

[data-testid="stMain"] .page-hero p {
    color: #e1f2f1 !important;
}

.step-label {
    color: #604582;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.2px;
}

@media (prefers-reduced-motion: reduce) {
    .page-hero,
    .subject-card,
    .stButton > button {
        animation: none !important;
        transition: none !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# 5. AUTHENTICATION
# ==========================================================

if not st.session_state.get("authenticated", False):

    render_login()
    st.stop()


# ==========================================================
# 6. HELPER FUNCTIONS
# ==========================================================

def resolve_path(path):
    """Resolve project-relative paths."""
    path = Path(path)

    if not path.is_absolute():
        path = ROOT_DIR / path

    return path


def get_generated_papers():
    """Read generated question paper JSON files."""
    papers = []

    for file_path in sorted(OUTPUT_DIR.glob("*_Paper.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            papers.append({
                "filename": file_path.name,
                "path": file_path,
                "data": data
            })

        except (json.JSONDecodeError, OSError):
            continue

    return papers


def get_all_questions(paper):
    """Extract all subquestions from a generated paper."""
    questions = []

    for section in paper.get("sections", []):
        for main_question in section.get("questions", []):
            questions.extend(
                main_question.get("sub_questions", [])
            )

    return questions


def get_bloom_distribution(questions):
    """Use the existing Bloom analysis tool."""
    analysis_tool = AnalysisTool()

    distribution = {level: 0 for level in analysis_tool.BLOOM_LEVELS}
    for question in questions:
        level = question.get("bloom")
        if level not in distribution:
            level = analysis_tool.classify_bloom(question.get("text", ""))
        distribution[level] += 1
    return distribution


def get_co_distribution(questions):
    """Calculate CO distribution."""
    distribution = {
        f"CO{i}": 0 for i in range(1, 6)
    }

    for question in questions:
        co = question.get("CO", "CO2")

        if co in distribution:
            distribution[co] += 1

    return distribution


def get_unit_distribution(paper):
    """Calculate unit-wise question distribution."""
    distribution = {}

    for section in paper.get("sections", []):
        unit = section.get("unit", "Unknown")

        count = sum(
            len(question.get("sub_questions", []))
            for question in section.get("questions", [])
        )

        distribution[unit] = count

    return distribution


def get_lesson_plan(subject):
    """Locate the lesson plan for a selected subject."""
    lesson_plans = {
        "Cloud Computing": "Cloud_Computing_LP.pdf",
        "Cyber Security": "Cyber_Security_LP.pdf",
        "Deep Learning": "Deep_Learning_LP.pdf",
        "Gen AI": "Gen_AI_LP.pdf"
    }

    filename = lesson_plans.get(subject)

    if not filename:
        return None

    path = LESSON_PLAN_DIR / filename

    return path if path.exists() else None


def get_pdf_path(json_filename):
    return OUTPUT_DIR / json_filename.replace(".json", ".pdf")


def get_valuation_path(json_filename):
    return OUTPUT_DIR / json_filename.replace(
        "_Paper.json",
        "_Valuation.pdf"
    )


def get_preview_key(pdf_path):
    return hashlib.md5(
        str(Path(pdf_path).resolve()).encode("utf-8")
    ).hexdigest()


# ==========================================================
# 7. PDF PREVIEW
# ==========================================================

def display_pdf_preview(pdf_path, download_label="Download PDF"):
    """
    Render a PDF page as an image using PyMuPDF.
    This avoids browser PDF iframe restrictions.
    """

    pdf_path = resolve_path(pdf_path)

    if not pdf_path.exists():
        st.error(f"PDF file not found: {pdf_path.name}")
        return

    if pymupdf is None:
        st.warning(
            "PDF image preview requires PyMuPDF. "
            "Run: pip install --upgrade pymupdf"
        )

        try:
            pdf_bytes = pdf_path.read_bytes()

            st.download_button(
                download_label,
                data=pdf_bytes,
                file_name=pdf_path.name,
                mime="application/pdf",
                key=f"download_{get_preview_key(pdf_path)}"
            )
        except OSError as error:
            st.error(f"Unable to read PDF: {error}")

        return

    try:
        pdf_bytes = pdf_path.read_bytes()

        with pymupdf.open(str(pdf_path)) as document:

            if document.page_count == 0:
                st.warning("This PDF has no pages.")
                return

            st.caption(
                f"{pdf_path.name} | {document.page_count} page(s)"
            )

            key = get_preview_key(pdf_path)

            selected_page = st.selectbox(
                "Choose page to preview",
                options=list(range(1, document.page_count + 1)),
                format_func=lambda number: (
                    f"Page {number} of {document.page_count}"
                ),
                key=f"pdf_page_{key}"
            )

            page = document.load_page(selected_page - 1)

            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(1.5, 1.5),
                alpha=False
            )

            image_bytes = pixmap.tobytes("png")

            st.image(
                image_bytes,
                use_container_width=True
            )

        st.download_button(
            label=f"⬇ {download_label}",
            data=pdf_bytes,
            file_name=pdf_path.name,
            mime="application/pdf",
            use_container_width=True,
            key=f"pdf_download_{key}"
        )

    except Exception as error:
        st.error(f"Unable to preview PDF: {error}")


# ==========================================================
# 8. QUALITY REPORT PDF
# ==========================================================

def generate_quality_report(paper, output_path):

    questions = get_all_questions(paper)
    bloom = get_bloom_distribution(questions)
    co = get_co_distribution(questions)
    units = get_unit_distribution(paper)
    difficulty = DifficultyCoverageAgent().analyze(
        questions, paper.get("blueprint")
    )["difficulty_distribution"]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def safe_text(value):
        return str(value).encode(
            "latin-1",
            errors="replace"
        ).decode("latin-1")

    def add_line(value, height=8):
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(
            w=pdf.w - pdf.l_margin - pdf.r_margin,
            h=height,
            text=safe_text(value)
        )

    pdf.set_font("Arial", "B", 16)
    add_line("QUESTION PAPER OBE AGENT", 12)

    pdf.set_font("Arial", "B", 13)
    add_line("Coverage and Quality Report", 10)

    pdf.ln(4)
    pdf.set_font("Arial", "", 11)

    add_line(f"Subject: {paper.get('subject', 'N/A')}")
    add_line(f"Examination: {paper.get('exam_type', 'N/A')}")
    add_line(f"Maximum Marks: {paper.get('total_marks', 'N/A')}")
    add_line(f"Total Subquestions: {len(questions)}")

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    add_line("1. Bloom's Taxonomy Distribution")

    pdf.set_font("Arial", "", 10)

    for level, count in bloom.items():
        add_line(f"{level}: {count} questions")

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    add_line("2. Estimated Difficulty Distribution")

    pdf.set_font("Arial", "", 10)
    for level in ("Easy", "Medium", "Hard"):
        add_line(f"{level}: {difficulty.get(level, 0)} questions")

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    add_line("3. Course Outcome Distribution")

    pdf.set_font("Arial", "", 10)

    for outcome, count in co.items():
        percentage = (
            count / len(questions) * 100
            if questions else 0
        )

        add_line(
            f"{outcome}: {count} questions ({percentage:.1f}%)"
        )

    covered = [
        outcome for outcome, count in co.items()
        if count > 0
    ]

    uncovered = [
        outcome for outcome, count in co.items()
        if count == 0
    ]

    pdf.ln(3)
    add_line(
        "Covered COs: " +
        (", ".join(covered) if covered else "None")
    )

    add_line(
        "Unmapped COs: " +
        (", ".join(uncovered) if uncovered else "None")
    )

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    add_line("4. Unit-wise Distribution")

    pdf.set_font("Arial", "", 10)

    for unit, count in units.items():
        add_line(f"{unit}: {count} subquestions")

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    add_line("5. Quality Notes")

    pdf.set_font("Arial", "", 10)

    add_line(
        "Bloom, difficulty, and CO classifications are estimates produced "
        "by rules or optional LLM tagging."
    )

    add_line(
        "Unit distribution is calculated from the generated paper's "
        "section structure."
    )

    add_line(
        "Faculty should review syllabus alignment and mappings "
        "before approving the paper."
    )

    output_path = resolve_path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pdf.output(str(output_path))

    return output_path


# ==========================================================
# 9. SAFE NAVIGATION INITIALIZATION
# ==========================================================

available_pages = get_available_pages()

# Apply queued navigation BEFORE creating the radio widget.
apply_pending_navigation()

# Handle pages no longer available to this account.
if st.session_state.active_page not in (
    ["Home"] + available_pages
):
    st.session_state.active_page = "Home"
    st.session_state.navigation_page = "Choose a page"

if st.session_state.navigation_page not in (
    ["Choose a page"] + available_pages
):
    st.session_state.navigation_page = "Choose a page"


# ==========================================================
# 10. SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown("""
    <div style="text-align:center; padding:18px 5px 22px;">
        <div style="font-size:48px;">🎓</div>
        <h2 style="
            color:white !important;
            margin:5px 0;
            font-size:25px;
        ">OBE AGENT</h2>
        <div style="
            font-size:10px;
            color:#c8d7ff;
            letter-spacing:1px;
        ">INTELLIGENT ASSESSMENT SYSTEM</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### WORKSPACE")

    st.radio(
        "Navigation",
        options=["Choose a page"] + available_pages,
        key="navigation_page",
        on_change=sync_navigation,
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### ACCOUNT")

    st.write(f"**{st.session_state.get('user_name', 'User')}**")
    st.caption(
        st.session_state.get("user_role", "faculty").title()
    )

    if st.button("↩ Back to Home", use_container_width=True):
        navigate_to("Home")
        st.rerun()

    if st.button("Logout", use_container_width=True):

        keys_to_clear = [
            "authenticated",
            "user_role",
            "user_id",
            "user_name",
            "active_page",
            "navigation_page",
            "pending_page",
            "latest_generation_results",
            "latest_valuation_path",
            "latest_quality_report"

            "selected_subject",
            "latest_generation_subject",
            "latest_generation_exam",
            "latest_generation_source"
        ]

        for key in keys_to_clear:
            st.session_state.pop(key, None)

        st.rerun()

    st.divider()

    st.markdown("""
    <div style="
        text-align:center;
        color:#b8c8ec;
        font-size:11px;
        margin-top:20px;
    ">
        Agentic AI Project<br>
        Question Paper OBE Agent
    </div>
    """, unsafe_allow_html=True)


page = st.session_state.active_page


# ==========================================================
# 11. ADMIN FACULTY MANAGEMENT
# ==========================================================

if page == "Faculty Management":

    if st.session_state.get("user_role") == "admin":
        render_admin_panel()
    else:
        st.error("Administrator access required.")

    st.stop()



# ==========================================================
# 12. HOME — SUBJECT SELECTION
# ==========================================================

if page == "Home":

    st.markdown("""
    <div class="page-hero">
        <div style="
            font-size:12px;
            letter-spacing:1.5px;
            font-weight:800;
            color:#bce9e5;
        ">
            QUESTION PAPER OBE AGENT
        </div>
        <h1>Academic Assessment Workspace</h1>
        <p>
            Select a subject to configure your examination
            and generate question papers using Agentic AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Choose Your Subject")
    st.caption(
        "Select one of the available subjects to continue."
    )

    subjects = [
        {
            "name": "Cloud Computing",
            "icon": "☁️",
            "description": "Cloud architecture, services and deployment."
        },
        {
            "name": "Cyber Security",
            "icon": "🔐",
            "description": "Security concepts, threats and protection."
        },
        {
            "name": "Deep Learning",
            "icon": "🧠",
            "description": "Neural networks and deep learning methods."
        },
        {
            "name": "Gen AI",
            "icon": "✨",
            "description": "Generative AI concepts and applications."
        }
    ]

    columns = st.columns(4, gap="medium")

    for index, subject_info in enumerate(subjects):

        with columns[index]:

            st.markdown(
                f"""
                <div class="subject-card" style="animation-delay: {index * 70}ms;">
                    <div style="font-size:34px;">
                        {subject_info["icon"]}
                    </div>
                    <h3>{subject_info["name"]}</h3>
                    <p>{subject_info["description"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                "Select Subject →",
                key=f"subject_{index}",
                use_container_width=True
            ):
                st.session_state.selected_subject = (
                    subject_info["name"]
                )
                navigate_to("Configure Examination")
                st.rerun()

    st.divider()

    st.markdown("### Your Academic Tools")

    tool_col1, tool_col2, tool_col3 = st.columns(3)

    with tool_col1:
        st.markdown("**📋 Scheme of Valuation**")
        st.caption("Create evaluation schemes for generated papers.")

        if st.button(
            "Open Valuation",
            key="home_valuation",
            use_container_width=True
        ):
            navigate_to("Generate Scheme of Valuation")
            st.rerun()

    with tool_col2:
        st.markdown("**📊 Coverage & Quality**")
        st.caption("Review Bloom levels, CO mapping and unit coverage.")

        if st.button(
            "Open Quality Report",
            key="home_quality",
            use_container_width=True
        ):
            navigate_to("Coverage & Quality Report")
            st.rerun()

    with tool_col3:
        st.markdown("**📁 Generated Documents**")
        st.caption("Preview and download your generated PDFs.")

        if st.button(
            "Open Documents",
            key="home_documents",
            use_container_width=True
        ):
            navigate_to("Generated Documents")
            st.rerun()

    st.divider()

    previous_col, lab_col = st.columns(2)

    with previous_col:
        if st.button(
            "📚 Previous Question Papers",
            use_container_width=True
        ):
            navigate_to("Previous Question Papers")
            st.rerun()

    with lab_col:
        if st.button(
            "🧪 Agentic AI Labs 1–14",
            use_container_width=True
        ):
            navigate_to("Labs 1–14")
            st.rerun()



# ==========================================================
# 13. EXAMINATION CONFIGURATION AND GENERATION
# ==========================================================

elif page == "Configure Examination":

    subject = st.session_state.get("selected_subject")

    st.markdown("""
    <div class="step-label">STEP 2 OF 3</div>
    """, unsafe_allow_html=True)

    st.title("Configure Your Examination")

    if not subject:

        st.warning("Please select a subject first.")

        if st.button("← Back to Subject Selection"):
            navigate_to("Home")
            st.rerun()

        st.stop()

    st.markdown(f"""
    <div class="page-hero">
        <div style="color:#bce9e5; font-size:12px;
                    font-weight:800; letter-spacing:1px;">
            SELECTED SUBJECT
        </div>
        <h1>{subject}</h1>
        <p>Configure the examination details below.</p>
    </div>
    """, unsafe_allow_html=True)

    back_col, subject_col = st.columns([1, 3])

    with back_col:
        if st.button("← Change Subject"):
            st.session_state.selected_subject = None
            navigate_to("Home")
            st.rerun()

    lesson_plan = get_lesson_plan(subject)

    if lesson_plan:
        st.success(f"Lesson plan available: {lesson_plan.name}")
    else:
        st.error(
            f"Lesson plan not found for {subject}. "
            "Please check the data/lesson_plans folder."
        )

    st.divider()

    st.markdown("### Examination Details")

    exam_type = st.selectbox(
        "Examination Type",
        ["ISA1", "ISA2", "ESA"],
        key="question_paper_exam_type",
        help="Choose the examination for which the paper is required."
    )

    marks_options = (
        [30, 40]
        if exam_type in ["ISA1", "ISA2"]
        else [60, 100]
    )
    total_marks_key = "question_paper_total_marks"
    if st.session_state.get(total_marks_key) not in marks_options:
        st.session_state[total_marks_key] = marks_options[0]

    with st.form("question_paper_form"):

        col1, col2 = st.columns(2)

        with col1:

            total_marks = st.selectbox(
                "Total Marks",
                marks_options,
                key=total_marks_key
            )

        with col2:

            target_batch = st.text_input(
                "Target Batch",
                placeholder="Example: 2023-2027"
            )

            num_sets = st.selectbox(
                "Number of Question Papers",
                [1, 2, 3],
                format_func=lambda n: (
                    f"{n} Paper Set" if n == 1
                    else f"{n} Paper Sets"
                )
            )

        st.divider()

        st.markdown("#### Generation Summary")

        summary1, summary2, summary3 = st.columns(3)

        summary1.metric("Subject", subject)
        summary2.metric("Exam Type", exam_type)
        summary3.metric("Maximum Marks", total_marks)

        st.info(
            "Each paper set is generated using the existing "
            "Lab 8 Parallel Swarm Agent. Separate valuation PDFs "
            "will also be prepared when the generated paper data is available."
        )

        submitted = st.form_submit_button(
            "🚀 Generate Question Papers",
            use_container_width=True
        )

    if submitted:

        if not target_batch.strip():
            st.error("Please enter the target batch.")

        elif lesson_plan is None:
            st.error("The selected subject's lesson plan is missing.")

        else:

            st.session_state.pop(
                "latest_generation_results",
                None
            )

            try:

                with st.spinner(
                    f"Generating {num_sets} paper set(s). "
                    "Please wait..."
                ):

                    swarm = ParallelSwarmAgent()

                    results = swarm.run_swarm(
                        subject=subject,
                        exam_type=exam_type,
                        target_batch=target_batch.strip(),
                        lesson_plan_path=str(lesson_plan),
                        total_marks=total_marks,
                        num_sets=num_sets
                    )

                if not isinstance(results, list):
                    raise ValueError(
                        "The generation agent did not return "
                        "a valid list of results."
                    )

                st.session_state.latest_generation_results = results
                st.session_state.latest_generation_subject = subject
                st.session_state.latest_generation_exam = exam_type

                successful = [
                    result for result in results
                    if isinstance(result, dict)
                    and result.get("status") == "success"
                ]

                failed = len(results) - len(successful)

                if successful:
                    st.success(
                        f"Successfully generated {len(successful)} "
                        f"of {num_sets} paper set(s)."
                    )

                if failed:
                    st.warning(
                        f"{failed} paper set(s) were unsuccessful. "
                        "Check the details below."
                    )

                if not successful:
                    st.error(
                        "No question papers were generated successfully."
                    )

            except Exception as error:
                st.error(f"Question paper generation failed: {error}")

    # ------------------------------------------------------
    # DISPLAY GENERATED PAPERS AND SEPARATE DOWNLOADS
    # ------------------------------------------------------

    latest_results = st.session_state.get(
        "latest_generation_results",
        []
    )

    if latest_results:

        st.divider()

        st.markdown("""
        <div class="step-label">STEP 3 OF 3</div>
        """, unsafe_allow_html=True)

        st.title("Generated Documents")

        st.caption(
            "Preview and download each question paper and its "
            "corresponding scheme of valuation separately."
        )

        for index, result in enumerate(latest_results):

            if not isinstance(result, dict):
                continue

            set_name = result.get(
                "set_name",
                f"Paper {index + 1}"
            )

            successful = result.get("status") == "success"

            with st.expander(
                f"{'✅' if successful else '❌'} {set_name}",
                expanded=True
            ):

                if not successful:

                    st.error(
                        result.get(
                            "error",
                            "This paper set could not be generated."
                        )
                    )
                    continue

                st.caption(
                    f"Generation time: "
                    f"{result.get('time_taken', 0):.2f} seconds"
                )

                # Locate the generated question paper PDF.
                pdf_path = None

                if result.get("pdf_path"):
                    pdf_path = resolve_path(result["pdf_path"])

                if pdf_path is not None and pdf_path.exists():

                    st.markdown("#### 📝 Question Paper")

                    display_pdf_preview(
                        pdf_path,
                        "Download Question Paper PDF"
                    )

                else:
                    st.warning(
                        "The question paper PDF path was not found "
                        "in the agent result."
                    )

                # Find the JSON created by the coordinator.
                json_path = None

                if result.get("json_path"):
                    candidate = resolve_path(result["json_path"])

                    if candidate.exists():
                        json_path = candidate

                if json_path is None:

                    subject_prefix = subject.replace(" ", "_")
                    set_suffix = f"_{set_name}" if set_name else ""

                    expected_json = (
                        OUTPUT_DIR /
                        f"{subject_prefix}_{exam_type}"
                        f"{set_suffix}_Paper.json"
                    )

                    if expected_json.exists():
                        json_path = expected_json

                # Fallback: match the latest paper JSON for this set.
                if json_path is None:

                    candidates = list(
                        OUTPUT_DIR.glob(
                            f"{subject.replace(' ', '_')}_"
                            f"{exam_type}*_Paper.json"
                        )
                    )

                    if set_name:
                        matching = [
                            path for path in candidates
                            if set_name in path.name
                        ]

                        if matching:
                            candidates = matching

                    if candidates:
                        json_path = max(
                            candidates,
                            key=lambda path: path.stat().st_mtime
                        )

                # Generate valuation PDF if required.
                valuation_path = None

                if json_path and json_path.exists():

                    valuation_path = get_valuation_path(
                        json_path.name
                    )

                    try:

                        if not valuation_path.exists():

                            with open(
                                json_path,
                                "r",
                                encoding="utf-8"
                            ) as file:
                                paper_data = json.load(file)

                            ValuationTool().generate(
                                paper_data,
                                str(valuation_path)
                            )

                        if valuation_path.exists():

                            st.markdown("#### 📋 Scheme of Valuation")

                            display_pdf_preview(
                                valuation_path,
                                "Download Scheme of Valuation PDF"
                            )

                    except Exception as error:
                        st.warning(
                            f"Unable to generate valuation PDF: {error}"
                        )

                else:
                    st.warning(
                        "The generated paper JSON was not found. "
                        "The valuation PDF cannot be generated without it."
                    )


# ==========================================================
# 14. SCHEME OF VALUATION
# ==========================================================

elif page == "Generate Scheme of Valuation":

    st.title("📋 Scheme of Valuation")

    st.write(
        "Select an existing question paper and generate its valuation PDF."
    )

    st.divider()

    papers = get_generated_papers()

    if papers:

        selected = st.selectbox(
            "Select Generated Question Paper",
            papers,
            format_func=lambda item: item["filename"]
        )

        data = selected["data"]

        st.markdown("### Selected Paper")

        st.write(f"**Subject:** {data.get('subject', 'N/A')}")
        st.write(f"**Examination:** {data.get('exam_type', 'N/A')}")
        st.write(f"**Maximum Marks:** {data.get('total_marks', 'N/A')}")

        if st.button(
            "📄 Generate Scheme of Valuation",
            use_container_width=True
        ):

            try:

                output_path = get_valuation_path(selected["filename"])

                with st.spinner("Generating valuation PDF..."):
                    ValuationTool().generate(
                        data,
                        str(output_path)
                    )

                if output_path.exists():

                    st.success(
                        "Scheme of Valuation generated successfully."
                    )

                    st.session_state.latest_valuation_path = str(
                        output_path
                    )

                    st.session_state.latest_valuation_source = (
                        selected["filename"]
                    )

            except Exception as error:
                st.error(f"Valuation generation failed: {error}")

        existing_valuation = get_valuation_path(selected["filename"])

        latest_path = st.session_state.get("latest_valuation_path")
        latest_source = st.session_state.get("latest_valuation_source")

        if latest_path and latest_source == selected["filename"]:
            valuation_path = resolve_path(latest_path)
        else:
            valuation_path = existing_valuation

        if valuation_path.exists():

            st.divider()
            st.subheader("Scheme of Valuation Preview")

            display_pdf_preview(
                valuation_path,
                "Download Scheme of Valuation"
            )

    else:
        st.warning("No generated question papers are available.")


# ==========================================================
# 15. COVERAGE & QUALITY REPORT
# ==========================================================

elif page == "Coverage & Quality Report":

    st.title("📊 Coverage & Quality Report")

    st.write(
        "Analyze Bloom's Taxonomy, estimated difficulty, CO mapping and "
        "unit-wise distribution."
    )

    st.divider()

    papers = get_generated_papers()

    if papers:

        selected = st.selectbox(
            "Select Question Paper",
            papers,
            format_func=lambda item: item["filename"]
        )

        paper = selected["data"]

        questions = get_all_questions(paper)
        bloom_data = get_bloom_distribution(questions)
        co_data = get_co_distribution(questions)
        unit_data = get_unit_distribution(paper)
        difficulty_data = DifficultyCoverageAgent().analyze(
            questions, paper.get("blueprint")
        )["difficulty_distribution"]

        st.markdown("### Selected Paper")

        st.write(
            f"**{paper.get('subject', 'Unknown')}** | "
            f"{paper.get('exam_type', 'Unknown')} | "
            f"{paper.get('total_marks', 0)} Marks"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Subquestions", len(questions))

        col2.metric(
            "Covered COs",
            sum(1 for value in co_data.values() if value > 0)
        )

        col3.metric("Units", len(unit_data))

        st.divider()
        st.subheader("⚖️ Estimated Difficulty Distribution")
        difficulty_fig = px.bar(
            x=["Easy", "Medium", "Hard"],
            y=[difficulty_data.get(level, 0) for level in ("Easy", "Medium", "Hard")],
            labels={"x": "Estimated Difficulty", "y": "Question Count"},
            color=["Easy", "Medium", "Hard"],
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        difficulty_fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white", showlegend=False
        )
        st.plotly_chart(difficulty_fig, use_container_width=True)

        st.divider()
        st.subheader("🧠 Bloom's Taxonomy Distribution")

        if bloom_data and any(bloom_data.values()):

            bloom_fig = px.bar(
                x=list(bloom_data.keys()),
                y=list(bloom_data.values()),
                labels={
                    "x": "Bloom Level",
                    "y": "Question Count"
                },
                color=list(bloom_data.keys()),
                color_discrete_sequence=px.colors.sequential.Purples
            )

            bloom_fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                showlegend=False
            )

            st.plotly_chart(
                bloom_fig,
                use_container_width=True
            )

        else:
            st.info("No Bloom distribution data is available.")

        left, right = st.columns(2)

        with left:

            st.subheader("🎯 Course Outcome Distribution")

            if any(co_data.values()):

                co_fig = px.pie(
                    names=list(co_data.keys()),
                    values=list(co_data.values()),
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )

                st.plotly_chart(
                    co_fig,
                    use_container_width=True
                )

            else:
                st.info("No CO mapping data is available.")

        with right:

            st.subheader("📚 Unit-wise Distribution")

            if unit_data and any(unit_data.values()):

                unit_fig = px.bar(
                    x=list(unit_data.keys()),
                    y=list(unit_data.values()),
                    labels={
                        "x": "Unit",
                        "y": "Subquestion Count"
                    },
                    color=list(unit_data.keys()),
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )

                unit_fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    showlegend=False
                )

                st.plotly_chart(
                    unit_fig,
                    use_container_width=True
                )

            else:
                st.info("No unit distribution data is available.")

        st.divider()
        st.subheader("CO Coverage Details")

        for outcome, count in co_data.items():

            percentage = (
                count / len(questions) * 100
                if questions else 0
            )

            st.write(
                f"**{outcome}: {count} questions ({percentage:.1f}%)**"
            )

            st.progress(percentage / 100)

        st.divider()

        if st.button(
            "📄 Generate Coverage & Quality Report PDF",
            use_container_width=True
        ):

            try:

                report_path = OUTPUT_DIR / selected["filename"].replace(
                    "_Paper.json",
                    "_Quality_Report.pdf"
                )

                with st.spinner("Generating quality report..."):
                    generate_quality_report(paper, report_path)

                st.session_state.latest_quality_report = str(report_path)
                st.session_state.latest_quality_source = selected["filename"]

                st.success("Coverage and Quality Report generated.")

            except Exception as error:
                st.error(f"Report generation failed: {error}")

        report_path = st.session_state.get("latest_quality_report")
        report_source = st.session_state.get("latest_quality_source")

        expected_report = OUTPUT_DIR / selected["filename"].replace(
            "_Paper.json",
            "_Quality_Report.pdf"
        )

        if report_path and report_source == selected["filename"]:
            report_to_show = resolve_path(report_path)
        else:
            report_to_show = expected_report

        if report_to_show.exists():

            st.divider()
            st.subheader("Quality Report Preview")

            display_pdf_preview(
                report_to_show,
                "Download Quality Report PDF"
            )

        st.info(
            "Bloom, difficulty, and CO classifications are automated "
            "estimates based on rules or optional LLM tagging. "
            "Faculty review is required before academic approval."
        )

    else:
        st.warning(
            "Generate a question paper before viewing its report."
        )


# ==========================================================
# 16. PREVIOUS QUESTION PAPERS
# ==========================================================

elif page == "Previous Question Papers":

    st.title("📚 Previous Question Papers")

    st.write(
        "Browse previously generated question papers, preview pages "
        "and download the original PDFs."
    )

    st.divider()

    previous_papers = sorted(
        OUTPUT_DIR.glob("*_Paper.pdf"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    if previous_papers:

        st.success(
            f"{len(previous_papers)} previous question paper(s) found."
        )

        for index, pdf_path in enumerate(previous_papers):

            with st.expander(
                f"📄 {pdf_path.stem}",
                expanded=(index == 0)
            ):

                col1, col2 = st.columns(2)

                with col1:
                    st.caption(
                        f"File size: "
                        f"{pdf_path.stat().st_size / 1024:.2f} KB"
                    )

                with col2:
                    modified = datetime.fromtimestamp(
                        pdf_path.stat().st_mtime
                    )

                    st.caption(
                        f"Modified: {modified.strftime('%d %b %Y, %I:%M %p')}"
                    )

                display_pdf_preview(
                    pdf_path,
                    "Download Question Paper PDF"
                )

    else:
        st.info(
            "No previous question paper PDFs are available yet. "
            "Generate a question paper first."
        )


# ==========================================================
# 17. GENERATED DOCUMENTS
# ==========================================================

elif page == "Generated Documents":

    st.title("📁 Generated Documents")

    st.write(
        "Browse, preview and download all generated academic PDF documents."
    )

    st.divider()

    pdf_files = sorted(
        OUTPUT_DIR.glob("*.pdf"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    if pdf_files:

        st.success(f"{len(pdf_files)} PDF document(s) available.")

        for pdf_path in pdf_files:

            with st.expander(f"📄 {pdf_path.name}"):

                modified = datetime.fromtimestamp(
                    pdf_path.stat().st_mtime
                )

                st.caption(
                    f"File size: {pdf_path.stat().st_size / 1024:.2f} KB"
                )

                st.caption(
                    f"Modified: {modified.strftime('%d %b %Y, %I:%M %p')}"
                )

                display_pdf_preview(
                    pdf_path,
                    "Download PDF"
                )

    else:
        st.info("No PDF documents have been generated yet.")


# ==========================================================
# 18. LABS 1–14
# ==========================================================

elif page == "Labs 1–14":

    st.title("🧪 Agentic AI Laboratory")

    st.write(
        "Explore the laboratory components included in this project."
    )

    st.divider()

    lab_details = [
        (1, "Basic Agent Concepts", [
            "runtime/openclaw_runtime.py",
            "skills/question_paper_skill.py"
        ]),
        (2, "Agent Tools", [
            "runtime/openclaw_runtime.py",
            "tools/question_bank_tool.py"
        ]),
        (3, "Agent Memory", [
            "runtime/openclaw_runtime.py",
            "memory/memory_manager.py"
        ]),
        (4, "Multi-Agent Workflow", [
            "agent/coordinator.py"
        ]),
        (5, "Agent Communication", [
            "agent/coordinator.py"
        ]),
        (6, "Agentic AI Applications", [
            "main.py"
        ]),
        (7, "Node Graph Agent", [
            "agent/lab7_node_graph_agent.py"
        ]),
        (8, "Parallel Swarm Agent", [
            "agent/lab8_parallel_swarm_agent.py"
        ]),
        (9, "Deep Research Agent", [
            "agent/lab9_deep_research_agent.py"
        ]),
        (10, "Cloud Operations Agent", [
            "agent/lab10_cloud_ops_agent.py"
        ]),
        (11, "SDLC Factory", [
            "agent/lab11_sdlc_factory.py"
        ]),
        (12, "Safety and Governance", [
            "agent/lab12_safety_governance.py"
        ]),
        (13, "Discipline Agents", [
            "agent/lab13_discipline_agents.py"
        ]),
        (14, "Capstone Studio", [
            "agent/lab14_capstone_studio.py"
        ])
    ]

    for number, title, source_files in lab_details:

        with st.expander(f"Lab {number} — {title}"):

            missing_files = [
                filename
                for filename in source_files
                if not (ROOT_DIR / filename).is_file()
            ]

            if missing_files:
                st.error(
                    "Source file(s) not found: "
                    + ", ".join(missing_files)
                )

            else:
                st.success("Implementation source available")
                st.code("\n".join(source_files))

            st.caption(
                "Source availability does not by itself confirm that "
                "a lab's workflow has been executed or fully tested."
            )

    st.divider()

    st.info(
        "Lab 8 parallel question-paper generation is connected "
        "to the Generate Question Paper page. This page checks for "
        "source files; other labs still need individual workflow "
        "checks before integration."
    )


# ==========================================================
# 19. FOOTER
# ==========================================================

st.markdown("""
<div class="footer">
    <b>QUESTION PAPER OBE AGENT</b><br>
    Agentic AI | Outcome-Based Education | Intelligent Assessment<br>
    KLE Technological University
</div>
""", unsafe_allow_html=True)
