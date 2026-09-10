from parsers.experience_extractor import ExperienceExtractor


def test_years_of_experience():
    extractor = ExperienceExtractor()

    result = extractor.extract(
        "I have 3 years of experience working as a Python developer."
    )

    assert result["minimum"] == 3
    assert result["text"] == "3 years"


def test_plus_years_experience():
    extractor = ExperienceExtractor()

    result = extractor.extract(
        "I have 5+ years of experience in software development."
    )

    assert result["minimum"] == 5
    assert result["text"] == "5+ years"


def test_fresher():
    extractor = ExperienceExtractor()

    result = extractor.extract(
        "I am a fresher and I recently graduated."
    )

    assert result["minimum"] == 0
    assert result["maximum"] == 0
    assert result["text"] == "Freshers"


def test_experience_range():
    extractor = ExperienceExtractor()

    result = extractor.extract(
        "I have around 2-4 years of professional experience."
    )

    assert result["minimum"] == 2
    assert result["maximum"] == 4


def test_no_experience_information():
    extractor = ExperienceExtractor()

    result = extractor.extract(
        "I am interested in this position and would like to learn more."
    )

    assert result["minimum"] is None
    assert result["maximum"] is None
    assert result["text"] == ""


if __name__ == "__main__":
    test_years_of_experience()
    test_plus_years_experience()
    test_fresher()
    test_experience_range()
    test_no_experience_information()

    print("Day 25 experience extraction tests passed.")