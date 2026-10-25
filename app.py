import os

import streamlit as st

from copilot.cv_parser import read_cv_bytes
from copilot.graph import MIN_FIT_SCORE, run_agent
from copilot.report import format_report

MAX_RUNS = int(os.getenv("MAX_RUNS_PER_SESSION", "5"))  # protects the free API quota
MAX_CHARS = 12000

STEP_LABELS = {
    "parse_cv": "Read your CV",
    "analyze_job": "Analyzed the job description",
    "research_company": "Researched the company",
    "score_match": "Scored the match",
    "cv_tips": "Wrote CV improvement tips",
    "cover_letter": "Wrote your cover letter",
}

st.set_page_config(page_title="Job Application Copilot", page_icon=":briefcase:", layout="wide")
st.session_state.setdefault("runs", 0)
st.session_state.setdefault("result", None)


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {i}" for i in items) if items else "_None_"


def render_results(state) -> None:
    job, match, tips = state["job"], state["match"], state["tips"]
    must, nice = state["overlap"]["must_have"], state["overlap"]["nice_to_have"]
    letter = state.get("cover_letter")

    st.divider()
    title = job.title + (f" at {job.company}" if job.company else "")
    st.subheader(f"Result: {title}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Match score", f"{match.overall_score}/100")
    c2.metric("Must-have skills covered", f"{must['coverage_pct']}%")
    c3.metric("Cover letter", "Written" if letter else "Skipped")

    t_match, t_skills, t_tips, t_letter, t_report = st.tabs(
        ["Match", "Skills check", "CV tips", "Cover letter", "Full report"]
    )

    with t_match:
        st.write(match.reasoning)
        a, b = st.columns(2)
        a.markdown("**Strengths**\n\n" + bullets(match.strengths))
        b.markdown("**Gaps**\n\n" + bullets(match.gaps))

    with t_skills:
        a, b = st.columns(2)
        a.markdown("**Must-have: found in your CV**\n\n" + bullets(must["matched"]))
        b.markdown("**Must-have: missing**\n\n" + bullets(must["missing"]))
        st.markdown("**Nice-to-have found:** " + (", ".join(nice["matched"]) or "none"))
        st.caption("This check is rule-based (word matching), so the score is backed by evidence, not just an LLM opinion.")

    with t_tips:
        st.markdown(bullets(tips.tips))
        st.markdown("**Keywords to add (only if they are true):** " + (", ".join(tips.keywords_to_add) or "none"))
        st.markdown("**Tailored summary**")
        st.code(tips.rewritten_summary, language=None, wrap_lines=True)

    with t_letter:
        if letter:
            st.markdown(f"**Subject:** {letter.subject}")
            st.text_area("Edit before sending", letter.body, height=380, key="letter_box")
            st.download_button(
                "Download cover letter (.txt)",
                f"Subject: {letter.subject}\n\n{letter.body}",
                file_name="cover_letter.txt",
            )
            st.caption("Always read it and fix anything that is not true for you.")
        else:
            st.info(
                f"Skipped: the match score is below {MIN_FIT_SCORE}, so a letter would be misleading. "
                "Work on the gaps first."
            )

    with t_report:
        report = format_report(state)
        st.download_button("Download full report (.md)", report, file_name="application_report.md")
        st.markdown(report)


# ---------------- page ----------------
st.title("Job Application Copilot")
st.caption("Add your CV and a job description. Get a match score, CV tips and a tailored cover letter.")

with st.sidebar:
    st.header("How it works")
    st.markdown(
        "1. Reads your CV and the job\n"
        "2. Searches the web for the company\n"
        "3. Scores the match (rules + LLM)\n"
        "4. Suggests CV improvements\n"
        "5. Writes a cover letter if you are a fair fit"
    )
    st.header("Privacy")
    st.write(
        "Your CV and the job text are sent to the AI provider to produce the result. "
        "This app does not save them to a file or database."
    )
    st.write(f"Runs left in this session: {max(MAX_RUNS - st.session_state.runs, 0)}")
    st.caption("Built with LangGraph, Pydantic and free LLM APIs.")

left, right = st.columns(2)

with left:
    st.subheader("1. Your CV")
    mode = st.radio("How do you want to add your CV?", ["Upload a file", "Paste text"], horizontal=True)
    cv_text, cv_error = "", None
    if mode == "Upload a file":
        uploaded = st.file_uploader("CV file (PDF, TXT or MD)", type=["pdf", "txt", "md"])
        if uploaded is not None:
            try:
                cv_text = read_cv_bytes(uploaded.getvalue(), uploaded.name)
            except Exception as e:
                cv_error = str(e)
    else:
        cv_text = st.text_area("Paste your CV text", height=300, key="cv_paste")
    if cv_error:
        st.error(cv_error)

with right:
    st.subheader("2. The job")
    job_text = st.text_area("Paste the job description", height=340, key="job_text")

st.caption(f"Only the first {MAX_CHARS:,} characters of each input are used.")

if st.button("Analyze my application", type="primary"):
    if not cv_text.strip():
        st.warning("Please add your CV first.")
    elif len(job_text.strip()) < 50:
        st.warning("Please paste a longer job description.")
    elif st.session_state.runs >= MAX_RUNS:
        st.warning("You reached the run limit for this session. Refresh the page to start again.")
    else:
        st.session_state.runs += 1
        status = st.status("Running the agent...", expanded=True)

        def on_step(node, _state):
            status.write(f"Done: {STEP_LABELS.get(node, node)}")

        try:
            result = run_agent(cv_text[:MAX_CHARS], job_text[:MAX_CHARS], on_step=on_step)
            status.update(label="Finished", state="complete", expanded=False)
            st.session_state.result = result
        except Exception as e:
            status.update(label="Something went wrong", state="error")
            st.session_state.result = None
            message = str(e).lower()
            if "429" in message or "rate" in message:
                st.error("The free AI quota is busy right now. Please wait a minute and try again.")
            else:
                st.error("The agent hit an error. Please try again.")
            with st.expander("Technical details"):
                st.code(str(e)[:500])

if st.session_state.result:
    render_results(st.session_state.result)
