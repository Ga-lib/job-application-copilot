from copilot.graph import MIN_FIT_SCORE, MIN_MUST_HAVE_COVERAGE, AgentState


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {i}" for i in items) if items else "- (none)"


def format_report(state: AgentState) -> str:
    cv, job, match, tips = state["cv"], state["job"], state["match"], state["tips"]
    must = state["overlap"]["must_have"]
    nice = state["overlap"]["nice_to_have"]

    parts = [
        f"# Application report: {job.title}" + (f" at {job.company}" if job.company else ""),
        f"Candidate: **{cv.name}**",
        f"\n## Match score: {match.overall_score}/100",
        match.reasoning,
        f"\n**Must-have skills covered:** {must['coverage_pct']}%  "
        f"({len(must['matched'])}/{len(must['matched']) + len(must['missing'])})",
        f"\nMatched:\n{_bullets(must['matched'])}",
        f"\nMissing:\n{_bullets(must['missing'])}",
        f"\nNice-to-have matched:\n{_bullets(nice['matched'])}",
        f"\n## Strengths\n{_bullets(match.strengths)}",
        f"\n## Gaps\n{_bullets(match.gaps)}",
        f"\n## CV improvement tips\n{_bullets(tips.tips)}",
        f"\n**Keywords to add (only if true):** {', '.join(tips.keywords_to_add) or '(none)'}",
        f"\n**Tailored summary:**\n> {tips.rewritten_summary}",
    ]

    letter = state.get("cover_letter")
    if letter:
        parts.append(f"\n## Cover letter\n**Subject:** {letter.subject}\n\n{letter.body}")
    else:
        parts.append(
            f"\n## Cover letter\nSkipped: the match score is below {MIN_FIT_SCORE} or fewer than "
            f"{MIN_MUST_HAVE_COVERAGE}% of the must-have skills are covered, so a letter would be "
            "misleading. Work on the gaps above first."
        )
    return "\n".join(parts) + "\n"
