from parsers.jd_cleaner import JDCleaner
from parsers.jd_normalizer import JDNormalizer


def test_clean_jd():

    cleaner = JDCleaner()

    text = "Python      SQL *****"

    cleaned = cleaner.clean(text)

    assert "*****" not in cleaned


def test_normalizer():

    normalizer = JDNormalizer()

    text = """
Technical Skills

Python

Qualifications

B.Tech

Work Experience

2 Years
"""

    normalized = normalizer.normalize(text)

    assert "Skills" in normalized
    assert "Education" in normalized
    assert "Experience" in normalized