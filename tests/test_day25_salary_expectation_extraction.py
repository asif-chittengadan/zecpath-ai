from screening_ai.salary_expectation_extractor import (
    SalaryExpectationExtractor,
)


def test_single_lpa():
    extractor = SalaryExpectationExtractor()

    result = extractor.extract(
        "My expected salary is 8 LPA."
    )

    assert result["salary_mentioned"] is True
    assert result["currency"] == "INR"
    assert result["period"] == "annual"
    assert result["minimum_lpa"] == 8
    assert result["maximum_lpa"] == 8


def test_salary_range():
    extractor = SalaryExpectationExtractor()

    result = extractor.extract(
        "I am expecting 10-12 LPA."
    )

    assert result["salary_mentioned"] is True
    assert result["minimum_lpa"] == 10
    assert result["maximum_lpa"] == 12


def test_lakh_per_annum():
    extractor = SalaryExpectationExtractor()

    result = extractor.extract(
        "I would expect around 15 lakh per annum."
    )

    assert result["salary_mentioned"] is True
    assert result["minimum_lpa"] == 15
    assert result["maximum_lpa"] == 15


def test_monthly_salary():
    extractor = SalaryExpectationExtractor()

    result = extractor.extract(
        "My expectation is 80000 rupees per month."
    )

    assert result["salary_mentioned"] is True
    assert result["period"] == "monthly"
    assert result["monthly_amount"] == 80000
    assert result["minimum_lpa"] == 9.6
    assert result["maximum_lpa"] == 9.6


def test_rupee_lpa():
    extractor = SalaryExpectationExtractor()

    result = extractor.extract(
        "I am looking for ₹12 LPA."
    )

    assert result["salary_mentioned"] is True
    assert result["minimum_lpa"] == 12
    assert result["maximum_lpa"] == 12


def test_no_salary_information():
    extractor = SalaryExpectationExtractor()

    result = extractor.extract(
        "I am flexible regarding compensation."
    )

    assert result["salary_mentioned"] is False
    assert result["minimum_lpa"] is None
    assert result["maximum_lpa"] is None


if __name__ == "__main__":
    test_single_lpa()
    test_salary_range()
    test_lakh_per_annum()
    test_monthly_salary()
    test_rupee_lpa()
    test_no_salary_information()

    print("Day 25 salary expectation extraction tests passed.")