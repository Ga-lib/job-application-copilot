from copilot.tools import skill_overlap, web_search_company


def test_matches_skills_list():
    r = skill_overlap(["Python", "SQL"], ["Python", "SQL", "Docker"])
    assert r["matched"] == ["Python", "SQL"]
    assert r["missing"] == ["Docker"]
    assert r["coverage_pct"] == 67


def test_or_requirement_matches_either_side():
    r = skill_overlap(["TensorFlow"], ["PyTorch or TensorFlow"])
    assert r["matched"] == ["PyTorch or TensorFlow"]


def test_whole_word_matching():
    # 'java' must not match 'javascript', and 'c' must not match 'ci'
    assert skill_overlap(["JavaScript"], ["Java"])["missing"] == ["Java"]
    assert skill_overlap(["C"], ["CI/CD"])["missing"] == ["CI/CD"]


def test_falls_back_to_full_cv_text():
    r = skill_overlap([], ["Docker"], cv_text="Deployed apps with Docker on AWS")
    assert r["matched"] == ["Docker"]


def test_empty_required():
    assert skill_overlap(["Python"], [])["coverage_pct"] == 0


def test_web_search_without_company_returns_empty():
    assert web_search_company(None) == ""
