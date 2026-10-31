from main_candidate_ranking import extract_candidate_skills


def test_candidate_ranking_extracts_skills_from_legacy_list_format():
    resume = {
        "Skills": ["Python", {"skill": "SQL"}, "Python"],
    }

    assert extract_candidate_skills(resume) == ["Python", "SQL"]


def test_candidate_ranking_extracts_skills_from_categorized_format():
    resume = {
        "Skills": {
            "technical": [{"skill": "Python"}, "SQL"],
            "business": ["Communication"],
        },
    }

    assert extract_candidate_skills(resume) == [
        "Python",
        "SQL",
        "Communication",
    ]


def test_candidate_ranking_treats_missing_skills_as_empty():
    assert extract_candidate_skills({"Skills": None}) == []
