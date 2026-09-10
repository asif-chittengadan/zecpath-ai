from parsers.skill_extractor import SkillExtractor


def test_technical_skills():
    extractor = SkillExtractor()

    answer = (
        "I have three years of experience working with "
        "Python, SQL, FastAPI and Machine Learning."
    )

    skills = extractor.extract(answer)

    assert "Python" in skills
    assert "SQL" in skills
    assert "FastAPI" in skills
    assert "Machine Learning" in skills


def test_multiple_skills():
    extractor = SkillExtractor()

    answer = (
        "My main skills are Python, JavaScript, React, "
        "Node.js and MongoDB."
    )

    skills = extractor.extract(answer)

    assert "Python" in skills
    assert "JavaScript" in skills
    assert "React" in skills
    assert "Node.js" in skills
    assert "MongoDB" in skills


def test_no_skills():
    extractor = SkillExtractor()

    answer = "I am looking forward to joining the company."

    skills = extractor.extract(answer)

    assert skills == []


if __name__ == "__main__":
    test_technical_skills()
    test_multiple_skills()
    test_no_skills()
    print("Day 25 skill extraction tests passed.")