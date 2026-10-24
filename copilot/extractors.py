from copilot.llm import chat_structured
from copilot.schemas import CVProfile, JobRequirements


def extract_cv_profile(cv_text: str) -> CVProfile:
    system = (
        "You extract structured data from CVs. Use only facts present in the CV. "
        "Never invent skills, jobs or dates."
    )
    return chat_structured(system, cv_text, CVProfile)


def analyze_job(job_text: str) -> JobRequirements:
    system = (
        "You analyze job descriptions. Separate required skills from nice-to-have ones. "
        "Use only facts present in the text."
    )
    return chat_structured(system, job_text, JobRequirements)
