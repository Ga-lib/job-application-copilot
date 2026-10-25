from pydantic import BaseModel, Field


class CVProfile(BaseModel):
    name: str = Field(description="Candidate full name")
    email: str | None = None
    summary: str = Field(description="2-3 sentence professional summary")
    skills: list[str]
    experience: list[str] = Field(description="One short line per role or freelance job")
    projects: list[str] = Field(description="One short line per project")
    education: list[str]


class JobRequirements(BaseModel):
    title: str
    company: str | None = None
    seniority: str = Field(description="intern, junior, mid, senior, or unknown")
    must_have_skills: list[str]
    nice_to_have_skills: list[str]
    responsibilities: list[str]


class MatchResult(BaseModel):
    overall_score: int = Field(ge=0, le=100, description="Overall fit score from 0 to 100")
    strengths: list[str] = Field(description="Top reasons this candidate fits the job")
    gaps: list[str] = Field(description="Most important missing skills or experience")
    reasoning: str = Field(description="2-4 sentences explaining the score")


class CVTips(BaseModel):
    tips: list[str] = Field(description="5 concrete, specific improvements to the CV for THIS job")
    keywords_to_add: list[str] = Field(description="Job keywords the candidate truly has but the CV lacks")
    rewritten_summary: str = Field(description="A tailored 2-3 sentence professional summary")


class CoverLetter(BaseModel):
    subject: str
    body: str
