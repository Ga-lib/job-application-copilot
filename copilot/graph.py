"""The agent brain: a LangGraph workflow.

parse_cv -> analyze_job -> research_company -> score_match -> cv_tips -> (cover_letter | END)

The last step is a conditional edge: if the candidate is a very weak fit, the agent
skips the cover letter and says so instead of writing a misleading one. It also skips it when
less than half of the job's must-have skills are covered (found by the evaluation suite).
"""
import json
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from copilot.extractors import analyze_job, extract_cv_profile
from copilot.llm import chat_structured
from copilot.schemas import CoverLetter, CVProfile, CVTips, JobRequirements, MatchResult
from copilot.tools import skill_overlap, web_search_company

MIN_FIT_SCORE = 35  # below this score, no cover letter is written
MIN_MUST_HAVE_COVERAGE = 50  # ...and also none if fewer than this % of must-have skills are covered


class AgentState(TypedDict, total=False):
    cv_text: str
    job_text: str
    cv: CVProfile
    job: JobRequirements
    company_notes: str
    overlap: dict
    match: MatchResult
    tips: CVTips
    cover_letter: CoverLetter | None
    log: list[str]


def _log(state: AgentState, message: str) -> list[str]:
    return state.get("log", []) + [message]


# ---------- nodes ----------

def node_parse_cv(state: AgentState) -> dict:
    cv = extract_cv_profile(state["cv_text"])
    return {"cv": cv, "log": _log(state, f"Parsed CV for {cv.name}")}


def node_analyze_job(state: AgentState) -> dict:
    job = analyze_job(state["job_text"])
    return {"job": job, "log": _log(state, f"Analyzed job: {job.title}")}


def node_research_company(state: AgentState) -> dict:
    notes = web_search_company(state["job"].company)
    msg = "Searched the web for company info" if notes else "No company info used"
    return {"company_notes": notes, "log": _log(state, msg)}


SCORE_SYSTEM = (
    "You are a strict but fair recruiter. Score how well the candidate fits the job from 0 to 100. "
    "Use the rule-based skill_check as hard evidence. Do not inflate the score: "
    "missing must-have skills should lower it clearly. Use only facts in the input."
)


def node_score_match(state: AgentState) -> dict:
    cv, job = state["cv"], state["job"]
    overlap = {
        "must_have": skill_overlap(cv.skills, job.must_have_skills, state["cv_text"]),
        "nice_to_have": skill_overlap(cv.skills, job.nice_to_have_skills, state["cv_text"]),
    }
    payload = json.dumps(
        {"candidate": cv.model_dump(), "job": job.model_dump(), "skill_check": overlap}, indent=2
    )
    match = chat_structured(SCORE_SYSTEM, payload, MatchResult)
    return {
        "overlap": overlap,
        "match": match,
        "log": _log(state, f"Match score: {match.overall_score}/100"),
    }


TIPS_SYSTEM = (
    "You are a career coach. Give specific CV improvements for THIS job. "
    "Only suggest keywords the candidate genuinely has evidence for; never suggest lying or inventing experience."
)


def node_cv_tips(state: AgentState) -> dict:
    payload = json.dumps(
        {
            "candidate": state["cv"].model_dump(),
            "job": state["job"].model_dump(),
            "match": state["match"].model_dump(),
        },
        indent=2,
    )
    tips = chat_structured(TIPS_SYSTEM, payload, CVTips)
    return {"tips": tips, "log": _log(state, "Wrote CV improvement tips")}


COVER_SYSTEM = (
    "Write a tailored cover letter of 180-250 words. Use ONLY facts from the candidate profile; "
    "never invent employers, numbers or experience. Mention 2-3 of the most relevant skills or projects. "
    "If company notes are given and relevant, reference one fact; otherwise ignore them. "
    "Plain text, address 'Dear Hiring Manager', sign with the candidate's name."
)


def node_cover_letter(state: AgentState) -> dict:
    payload = json.dumps(
        {
            "candidate": state["cv"].model_dump(),
            "job": state["job"].model_dump(),
            "strengths": state["match"].strengths,
            "company_notes": state.get("company_notes", ""),
        },
        indent=2,
    )
    letter = chat_structured(COVER_SYSTEM, payload, CoverLetter)
    return {"cover_letter": letter, "log": _log(state, "Wrote cover letter")}


def route_after_tips(state: AgentState) -> str:
    if state["match"].overall_score < MIN_FIT_SCORE:
        return "skip"
    must = state["overlap"]["must_have"]
    total = len(must["matched"]) + len(must["missing"])
    if total and must["coverage_pct"] < MIN_MUST_HAVE_COVERAGE:
        return "skip"  # the job needs skills the candidate mostly lacks: a letter would not help
    return "cover_letter"


# ---------- graph ----------

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("parse_cv", node_parse_cv)
    g.add_node("analyze_job", node_analyze_job)
    g.add_node("research_company", node_research_company)
    g.add_node("score_match", node_score_match)
    g.add_node("cv_tips", node_cv_tips)
    g.add_node("cover_letter", node_cover_letter)

    g.add_edge(START, "parse_cv")
    g.add_edge("parse_cv", "analyze_job")
    g.add_edge("analyze_job", "research_company")
    g.add_edge("research_company", "score_match")
    g.add_edge("score_match", "cv_tips")
    g.add_conditional_edges("cv_tips", route_after_tips, {"cover_letter": "cover_letter", "skip": END})
    g.add_edge("cover_letter", END)
    return g.compile()


def run_agent(cv_text: str, job_text: str, verbose: bool = False, on_step=None) -> AgentState:
    """Run the whole workflow and return the final state.

    on_step(node_name, state) is called after each step (the web app uses it for live progress).
    """
    app = build_graph()
    state: AgentState = {"cv_text": cv_text, "job_text": job_text, "cover_letter": None}
    for chunk in app.stream(state, stream_mode="updates"):
        for node_name, update in chunk.items():
            state.update(update)
            if verbose:
                print(f"  done: {node_name}")
            if on_step:
                on_step(node_name, state)
    return state
