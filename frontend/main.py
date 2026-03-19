import streamlit as st
import json
from utils import extract_text
from client import analyse

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.title(" AI Resume Analyzer & Job Coach")
st.caption("Upload your resume and paste a job description to get instant AI-powered feedback.")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("How it works")
    st.markdown("""
1. Upload your resume (PDF, DOCX, or TXT)
2. Paste the job description
3. Click **Analyze**
4. Get your ATS score, skill gaps, interview prep, and more!
""")
    st.divider()
    st.caption("Powered by LLaMA 3.3 via Groq")

# ── Input Section ──────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Your Resume")
    uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx", "txt"])
    resume_text = ""
    if uploaded_file:
        try:
            resume_text = extract_text(uploaded_file)
            st.success(f" Extracted {len(resume_text.split())} words")
            with st.expander("Preview extracted text"):
                st.text(resume_text[:500] + "..." if len(resume_text) > 500 else resume_text)
        except Exception as e:
            st.error(f"Failed to extract text: {e}")

with col2:
    st.subheader("Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=200,
        max_chars=5000,
        placeholder="Paste the full job description here..."
    )
    if job_description:
        st.caption(f"{len(job_description)} / 5000 characters")

# ── Analyze Button ─────────────────────────────────────────────────────────────
st.divider()
analyze_btn = st.button(" Analyze My Resume", type="primary", use_container_width=True)

if analyze_btn:
    if not resume_text:
        st.error("Please upload your resume first.")
    elif not job_description.strip():
        st.error("Please paste a job description.")
    else:
        with st.spinner("Analyzing your resume... this takes about 10–15 seconds "):
            result = analyse(resume_text, job_description)

        if "error" in result:
            st.error(f"Analysis failed: {result['error']}")
        else:
            st.session_state["result"] = result
            st.success(" Analysis complete!")

# ── Results ────────────────────────────────────────────────────────────────────
if "result" in st.session_state:
    result = st.session_state["result"]
    scores = result.get("scores", {})
    interview = result.get("interview_qa", {})
    rewrites = result.get("rewrites", {})
    report = result.get("report", {})

    st.divider()
    st.subheader(" Your Scores")

    m1, m2, m3 = st.columns(3)
    m1.metric("ATS Score", f"{scores.get('ats_score', 0)} / 100")
    m2.metric("Skill Match", f"{scores.get('skill_match_percent', 0)}%")
    m3.metric("Tone & Impact", f"{scores.get('tone_score', 0)} / 100")

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([" Skill Gap", " Interview Prep", " Bullet Rewrites", " Full Report"])

    # Tab 1 — Skill Gap
    with tab1:
        st.subheader("Matched Skills")
        matched = scores.get("matched_skills", [])
        if matched:
            cols = st.columns(min(len(matched), 4))
            for i, skill in enumerate(matched):
                cols[i % 4].success(f" {skill}")
        else:
            st.info("No matched skills found.")

        st.subheader("Skill Gaps & Suggestions")
        gaps = scores.get("skill_gaps", [])
        for gap in gaps:
            with st.expander(f" {gap.get('skill', '')}"):
                st.write(gap.get("suggestion", ""))

    # Tab 2 — Interview Prep
    with tab2:
        questions = interview.get("questions", [])
        if questions:
            for i, qa in enumerate(questions, 1):
                with st.expander(f"Q{i}: {qa.get('question', '')}"):
                    st.markdown(f"**Situation:** {qa.get('situation', '')}")
                    st.markdown(f"**Task:** {qa.get('task', '')}")
                    st.markdown(f"**Action:** {qa.get('action', '')}")
                    st.markdown(f"**Result:** {qa.get('result', '')}")
        else:
            st.info("No interview questions generated.")

    # Tab 3 — Bullet Rewrites
    with tab3:
        rewrites_list = rewrites.get("rewrites", [])
        if rewrites_list:
            for i, rw in enumerate(rewrites_list, 1):
                st.markdown(f"**Rewrite {i}**")
                c1, c2 = st.columns(2)
                with c1:
                    st.error(f"**Before:**\n{rw.get('before', '')}")
                with c2:
                    st.success(f"**After:**\n{rw.get('after', '')}")
                st.caption(f"💡 Why: {rw.get('why', '')}")
                st.divider()
        else:
            st.info("No rewrites generated.")

    # Tab 4 — Full Report
    with tab4:
        report_md = report.get("report_markdown", "")
        linkedin = report.get("linkedin_about", "")

        if report_md:
            st.markdown(report_md)

        if linkedin:
            st.subheader("💼 LinkedIn About Draft")
            st.text_area("Copy this to your LinkedIn profile:", value=linkedin, height=200)

    # Download button
    st.divider()
    st.download_button(
        label="Download Full Analysis (JSON)",
        data=json.dumps(result, indent=2),
        file_name="resume_analysis.json",
        mime="application/json",
        use_container_width=True
    )