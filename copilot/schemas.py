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
