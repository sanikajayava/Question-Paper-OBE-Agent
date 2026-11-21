
import json
from pathlib import Path

import streamlit as st
import plotly.express as px

from tools.analysis_tool import AnalysisTool


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
AGENT_DIR = ROOT_DIR / "agent"

OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================================
# 2. CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background: linear-gradient(
        135deg,
        #f4f7ff 0%,
        #edf1ff 50%,
        #f8f4ff 100%
    );
}

/* Main page spacing */
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

/* Main headings */
h1 {
    color: #172554 !important;
    font-weight: 800 !important;
}

h2 {
    color: #253b73 !important;
    font-weight: 750 !important;
}

h3 {
    color: #344779 !important;
    font-weight: 700 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #101b35 0%,
        #1d2c55 55%,
        #343c78 100%
    );
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* Sidebar radio buttons */
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.055);
    padding: 10px 12px;
    border-radius: 9px;
    margin-bottom: 5px;
    transition: 0.2s;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.16);
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #dce5ff;
    padding: 19px;
    border-radius: 15px;
    box-shadow: 0 5px 18px rgba(37,59,115,0.07);
}

[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #253b73 !important;
    font-weight: 800;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #5267e8, #8758d6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    font-weight: 700;
    transition: 0.2s;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #354bd0, #7040bd);
    color: white;
    border: none;
}

/* Disabled buttons */
.stButton > button:disabled {
    background: #aeb8d0;
    color: white;
}

/* Download buttons */
.stDownloadButton > button {
    background: #e9efff;
    color: #253b73;
    border: 1px solid #cbd8ff;
    border-radius: 9px;
    font-weight: 600;
}

.stDownloadButton > button:hover {
    background: #dce5ff;
    color: #172554;
    border: 1px solid #aabcf5;
}

/* Expanders */
[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #dce5ff;
    border-radius: 12px;
    margin-bottom: 8px;
}

/* Inputs */
.stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 9px;
}

/* Alerts */
.stAlert {
    border-radius: 12px;
}

/* Divider */
hr {
    border-color: #d8e1fa;
}

/* Custom hero */
.hero {
    background: linear-gradient(
        120deg,
        #101b35 0%,
        #263c78 55%,
        #7653c8 100%
    );
    padding: 34px;
    border-radius: 20px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 28px rgba(36,45,100,0.18);
}

.hero h1 {
    color: white !important;
    font-size: 34px;
    margin-bottom: 8px;
}

.hero p {
    color: #dce7ff;
    font-size: 15px;
}

.hero-tag {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    padding: 6px 13px;
    border-radius: 30px;
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 15px;
}

/* Feature cards */
.feature-card {
    background: white;
    padding: 21px;
    border-radius: 15px;
    border: 1px solid #e0e7ff;
    min-height: 135px;
    box-shadow: 0 4px 15px rgba(37,59,115,0.055);
}

.feature-card h3 {
    margin-top: 5px;
    margin-bottom: 6px;
    font-size: 18px;
}

.feature-card p {
    color: #64748b;
    font-size: 13px;
    margin-bottom: 0;
}

.feature-icon {
    font-size: 27px;
}

/* Section labels */
.section-label {
    color: #64748b;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* Footer */
.footer {
    text-align: center;
    color: #7b879f;
    font-size: 12px;
    padding: 25px 0 5px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# 3. HELPER FUNCTIONS
# ==========================================================

def get_generated_papers():
    """Load previously generated question paper JSON files."""

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

            for question in main_question.get("sub_questions", []):
                questions.append(question)

    return questions


def get_bloom_distribution(questions):
    """Reuse existing Bloom analysis tool."""

    analysis_tool = AnalysisTool()

    analysis_questions = [
        {"question_text": q.get("text", "")}
        for q in questions
    ]

    return analysis_tool.analyze_bloom(analysis_questions)


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
            len(q.get("sub_questions", []))
            for q in section.get("questions", [])
        )

        distribution[unit] = count

    return distribution


def get_available_labs():
    """Check availability of Lab 7 to Lab 14 files."""

    labs = [
        (7, "Node Graph Agent", "lab7_node_graph_agent.py"),
        (8, "Parallel Swarm Agent", "lab8_parallel_swarm_agent.py"),
        (9, "Deep Research Agent", "lab9_deep_research_agent.py"),
        (10, "Cloud Operations Agent", "lab10_cloud_ops_agent.py"),
        (11, "SDLC Factory", "lab11_sdlc_factory.py"),
        (12, "Safety and Governance", "lab12_safety_governance.py"),
        (13, "Discipline Agents", "lab13_discipline_agents.py"),
        (14, "Capstone Studio", "lab14_capstone_studio.py")
    ]

    return [
        {
            "number": number,
            "title": title,
            "exists": (AGENT_DIR / filename).exists(),
            "filename": filename
        }
        for number, title, filename in labs
    ]


# ==========================================================
# 4. LOAD PROJECT DATA
# ==========================================================

papers = get_generated_papers()
labs = get_available_labs()


# ==========================================================
# 5. SIDEBAR NAVIGATION
# ==========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:15px 5px 22px;">
            <div style="font-size:43px;">🎓</div>
            <h2 style="color:white !important; margin:5px 0;">
                OBE AGENT
            </h2>
            <div style="font-size:11px; color:#c8d7ff;">
                INTELLIGENT ASSESSMENT SYSTEM
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### WORKSPACE")

    page = st.radio(
        "Navigation",
        [
            "Dashboard Overview",
            "Generate Question Paper",
            "Generate Scheme of Valuation",
            "Coverage & Quality Report",
            "Previous Generated Papers",
            "Labs 1–14"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### PROJECT STATUS")

    st.markdown(
        f"""
        <div style="
            background:rgba(255,255,255,0.09);
            border-radius:12px;
            padding:13px;
            font-size:13px;
            line-height:2;
        ">
            🟢 Dashboard Active<br>
            📄 {len(papers)} Papers Found<br>
            🧪 {sum(lab['exists'] for lab in labs)}/8 Lab Files Available
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            text-align:center;
            color:#b8c8ec;
            font-size:11px;
            margin-top:35px;
        ">
            Agentic AI Project<br>
            Question Paper OBE Agent
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# 6. DASHBOARD OVERVIEW
# ==========================================================

if page == "Dashboard Overview":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-tag">✦ AGENTIC AI POWERED WORKSPACE</div>
            <h1>Question Paper Intelligence</h1>
            <p>
                Intelligent Question Paper Generation,
                Outcome-Based Education Mapping and
                Academic Quality Analysis.
            </p>
            <div style="margin-top:20px; font-size:13px; color:#dce7ff;">
                GENERATE &nbsp; • &nbsp; VALIDATE &nbsp; • &nbsp;
                ANALYZE &nbsp; • &nbsp; EXPORT
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    total_papers = len(papers)

    total_questions = sum(
        len(get_all_questions(item["data"]))
        for item in papers
    )

    total_subjects = len({
        item["data"].get("subject", "Unknown")
        for item in papers
    })

    available_labs = sum(
        lab["exists"] for lab in labs
    )

    st.markdown('<div class="section-label">PROJECT OVERVIEW</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📄 Generated Papers", total_papers)
    c2.metric("❓ Total Questions", total_questions)
    c3.metric("📚 Subjects", total_subjects)
    c4.metric("🧪 Lab Files Available", f"{available_labs}/8")

    st.divider()

    st.markdown("### ⚡ Workspace")

    f1, f2 = st.columns(2)

    with f1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <h3>Question Paper Generation</h3>
            <p>Generate examination papers using faculty-defined settings.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Coverage & Quality Analytics</h3>
            <p>Analyze Bloom levels, Course Outcomes and unit coverage.</p>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h3>Scheme of Valuation</h3>
            <p>Create a separate valuation document for generated papers.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📁</div>
            <h3>Document Center</h3>
            <p>Access and download previously generated academic documents.</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 🕒 Recent Generated Papers")

    if papers:

        for item in papers[-5:][::-1]:

            data = item["data"]

            with st.expander(
                f"📄 {data.get('subject', 'Unknown')} | "
                f"{data.get('exam_type', 'Unknown')} | "
                f"{item['filename']}"
            ):

                a, b, c = st.columns(3)

                a.metric("Maximum Marks", data.get("total_marks", 0))
                b.metric("Questions", len(get_all_questions(data)))
                c.metric("Duration", data.get("duration", "N/A"))

    else:
        st.info("No generated papers found. Generate your first paper to get started.")

    st.divider()

    st.markdown("### 🔄 Agentic AI Workflow")

    st.markdown("""
    **01 — Faculty Input** → Subject, lesson plan and examination settings

    **02 — Intelligent Retrieval** → Retrieve relevant questions from available sources

    **03 — Multi-Agent Processing** → Analysis, Bloom classification and validation

    **04 — OBE Mapping** → Course Outcome and Program Outcome mapping

    **05 — Document Generation** → Question paper, valuation and quality reports
    """)


# ==========================================================
# 7. GENERATE QUESTION PAPER
# ==========================================================

elif page == "Generate Question Paper":

    st.title("📝 Generate Question Paper")

    st.write(
        "Configure the examination details before generating a question paper."
    )

    st.divider()

    st.subheader("Examination Configuration")

    col1, col2 = st.columns(2)

    with col1:

        subject_options = [
            "Cloud Computing",
            "Cyber Security",
            "Deep Learning",
            "Gen AI"
        ]

        subject = st.selectbox(
            "Select Subject",
            subject_options
        )

        exam_type = st.selectbox(
            "Examination Type",
            ["ISA1", "ISA2", "ESA"]
        )

        total_marks = st.selectbox(
            "Total Marks",
            [30, 40, 60, 100]
        )

    with col2:

        target_batch = st.text_input(
            "Target Batch",
            placeholder="Example: 2023-2027"
        )

        set_name = st.selectbox(
            "Question Paper Set",
            ["Set A", "Set B", "Set C"]
        )

        lesson_plan_files = sorted(
            (ROOT_DIR / "data" / "lesson_plans").glob("*.pdf")
        )

        if lesson_plan_files:

            selected_lesson_plan = st.selectbox(
                "Select Lesson Plan",
                lesson_plan_files,
                format_func=lambda f: f.name
            )

        else:
            selected_lesson_plan = None
            st.error("No lesson plan PDFs found.")

    st.divider()

    st.subheader("Generation Options")

    st.write("The faculty can generate the required documents independently.")

    st.button(
        "🚀 Generate Question Paper",
        disabled=True,
        use_container_width=True
    )

    st.caption(
        "Generation integration is pending. "
        "The next implementation step will connect this form "
        "to QuestionPaperCoordinator.run_workflow()."
    )


# ==========================================================
# 8. GENERATE SCHEME OF VALUATION
# ==========================================================

elif page == "Generate Scheme of Valuation":

    st.title("📋 Scheme of Valuation")

    st.write(
        "Select an existing question paper to generate its valuation scheme."
    )

    st.divider()

    if papers:

        selected = st.selectbox(
            "Select Generated Question Paper",
            papers,
            format_func=lambda item: item["filename"]
        )

        data = selected["data"]

        st.markdown("### Selected Paper")

        a, b, c = st.columns(3)

        a.metric("Subject", data.get("subject", "N/A"))
        b.metric("Examination", data.get("exam_type", "N/A"))
        c.metric("Total Marks", data.get("total_marks", 0))

        st.button(
            "📄 Generate Scheme of Valuation",
            disabled=True,
            use_container_width=True
        )

        st.caption(
            "ValuationTool integration will be connected next. "
            "The selected paper will remain unchanged."
        )

    else:

        st.warning("No generated question papers are available.")


# ==========================================================
# 9. COVERAGE & QUALITY REPORT
# ==========================================================

elif page == "Coverage & Quality Report":

    st.title("📊 Coverage & Quality Analytics")

    st.write(
        "Explore Bloom's Taxonomy, CO mapping and unit-wise question distribution."
    )

    st.divider()

    if papers:

        selected = st.selectbox(
            "Select Question Paper",
            papers,
            format_func=lambda item: item["filename"]
        )

        paper = selected["data"]
        questions = get_all_questions(paper)

        st.markdown("### Paper Information")

        st.write(
            f"**{paper.get('subject', 'Unknown')}** | "
            f"{paper.get('exam_type', 'Unknown')} | "
            f"{paper.get('total_marks', 0)} Marks"
        )

        co_data = get_co_distribution(questions)
        bloom_data = get_bloom_distribution(questions)
        unit_data = get_unit_distribution(paper)

        c1, c2, c3 = st.columns(3)

        c1.metric("Total Subquestions", len(questions))

        c2.metric(
            "Covered COs",
            sum(1 for value in co_data.values() if value > 0)
        )

        c3.metric(
            "Units Covered",
            len(unit_data)
        )

        st.divider()

        st.subheader("🧠 Bloom's Taxonomy Distribution")

        bloom_fig = px.bar(
            x=list(bloom_data.keys()),
            y=list(bloom_data.values()),
            labels={
                "x": "Bloom Level",
                "y": "Question Count"
            },
            color=list(bloom_data.keys()),
            color_discrete_sequence=px.colors.sequential.Purples,
            title="Distribution Across Six Cognitive Levels"
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

        st.divider()

        left, right = st.columns(2)

        with left:

            st.subheader("🎯 CO Distribution")

            co_fig = px.pie(
                names=list(co_data.keys()),
                values=list(co_data.values()),
                hole=0.48,
                title="Course Outcome Mapping",
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            co_fig.update_layout(
                paper_bgcolor="white"
            )

            st.plotly_chart(
                co_fig,
                use_container_width=True
            )

        with right:

            st.subheader("📚 Unit-wise Coverage")

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

        st.divider()

        st.subheader("CO Coverage Details")

        for co, count in co_data.items():

            percentage = (
                count / len(questions) * 100
                if questions else 0
            )

            st.write(f"**{co} — {count} questions ({percentage:.1f}%)**")

            st.progress(percentage / 100)

        st.info(
            "These charts are preliminary analytics based on the generated "
            "paper's existing question mappings. The full validation-based "
            "quality report and downloadable PDF are not connected yet."
        )

    else:

        st.warning("Generate a question paper before viewing analytics.")


# ==========================================================
# 10. PREVIOUS GENERATED PAPERS
# ==========================================================

elif page == "Previous Generated Papers":

    st.title("📁 Document Center")

    st.write(
        "Browse and download previously generated question papers."
    )

    st.divider()

    if papers:

        st.success(f"{len(papers)} generated paper files found.")

        for item in papers[::-1]:

            data = item["data"]

            with st.expander(
                f"📄 {data.get('subject', 'Unknown')} — "
                f"{data.get('exam_type', 'Unknown')} — "
                f"{item['filename']}"
            ):

                c1, c2, c3 = st.columns(3)

                c1.metric("Maximum Marks", data.get("total_marks", 0))
                c2.metric("Subquestions", len(get_all_questions(data)))
                c3.metric("Duration", data.get("duration", "N/A"))

                st.download_button(
                    "⬇ Download JSON",
                    data=json.dumps(
                        data,
                        indent=4
                    ).encode("utf-8"),
                    file_name=item["filename"],
                    mime="application/json",
                    key=f"json_{item['filename']}"
                )

                pdf_path = OUTPUT_DIR / item["filename"].replace(
                    ".json", ".pdf"
                )

                if pdf_path.exists():

                    st.download_button(
                        "⬇ Download Question Paper PDF",
                        data=pdf_path.read_bytes(),
                        file_name=pdf_path.name,
                        mime="application/pdf",
                        key=f"pdf_{item['filename']}"
                    )

                else:

                    st.caption("Question paper PDF not found.")

                valuation_path = OUTPUT_DIR / (
                    item["filename"].replace(
                        "_Paper.json",
                        "_Valuation.pdf"
                    )
                )

                if valuation_path.exists():

                    st.download_button(
                        "⬇ Download Valuation PDF",
                        data=valuation_path.read_bytes(),
                        file_name=valuation_path.name,
                        mime="application/pdf",
                        key=f"valuation_{item['filename']}"
                    )

    else:

        st.info("No previous generated papers found.")


# ==========================================================
# 11. LABS 1–14
# ==========================================================

elif page == "Labs 1–14":

    st.title("🧪 Agentic AI Laboratory")

    st.write(
        "Explore the laboratory components included in the project."
    )

    st.divider()

    lab_details = [
        (1, "Basic Agent Concepts", None),
        (2, "Agent Tools", None),
        (3, "Agent Memory", None),
        (4, "Multi-Agent Workflow", None),
        (5, "Agent Communication", None),
        (6, "Agentic AI Applications", None),
        (7, "Node Graph Agent", "lab7_node_graph_agent.py"),
        (8, "Parallel Swarm Agent", "lab8_parallel_swarm_agent.py"),
        (9, "Deep Research Agent", "lab9_deep_research_agent.py"),
        (10, "Cloud Operations Agent", "lab10_cloud_ops_agent.py"),
        (11, "SDLC Factory", "lab11_sdlc_factory.py"),
        (12, "Safety and Governance", "lab12_safety_governance.py"),
        (13, "Discipline Agents", "lab13_discipline_agents.py"),
        (14, "Capstone Studio", "lab14_capstone_studio.py")
    ]

    for number, title, filename in lab_details:

        with st.expander(f"Lab {number} — {title}"):

            if filename:

                exists = (AGENT_DIR / filename).exists()

                if exists:
                    st.success("Lab source file available")
                else:
                    st.error("Lab source file not found")

                st.code(f"agent/{filename}")

            else:

                st.info(
                    "Implementation and execution status need to be verified."
                )

            st.caption(
                "File availability does not necessarily mean "
                "the lab is fully integrated and tested."
            )


# ==========================================================
# 12. FOOTER
# ==========================================================

st.markdown(
    """
    <div class="footer">
        <b>QUESTION PAPER OBE AGENT</b><br>
        Agentic AI | Outcome-Based Education | Intelligent Assessment<br>
        KLE Technological University
    </div>
    """,
    unsafe_allow_html=True
)
