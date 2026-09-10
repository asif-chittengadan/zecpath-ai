from screening_ai.availability_extractor import AvailabilityExtractor


def test_immediate_availability():
    extractor = AvailabilityExtractor()

    result = extractor.extract("I can join immediately.")

    assert result["available"] is True
    assert result["availability_type"] == "immediate"
    assert result["notice_period_days"] == 0


def test_notice_period():
    extractor = AvailabilityExtractor()

    result = extractor.extract(
        "I am currently serving a 30-day notice period."
    )

    assert result["available"] is True
    assert result["availability_type"] == "notice_period"
    assert result["notice_period_days"] == 30


def test_days_until_joining():
    extractor = AvailabilityExtractor()

    result = extractor.extract("I can start after 15 days.")

    assert result["available"] is True
    assert result["availability_type"] == "notice_period"
    assert result["notice_period_days"] == 15


def test_future_availability():
    extractor = AvailabilityExtractor()

    result = extractor.extract("I can join next month.")

    assert result["available"] is True
    assert result["availability_type"] == "future"
    assert result["notice_period_days"] is None


def test_unavailable():
    extractor = AvailabilityExtractor()

    result = extractor.extract("I am not available right now.")

    assert result["available"] is False
    assert result["availability_type"] == "unavailable"


def test_unknown_availability():
    extractor = AvailabilityExtractor()

    result = extractor.extract(
        "I am interested in this opportunity."
    )

    assert result["available"] is None
    assert result["availability_type"] == "unknown"


if __name__ == "__main__":
    test_immediate_availability()
    test_notice_period()
    test_days_until_joining()
    test_future_availability()
    test_unavailable()
    test_unknown_availability()

    print("Day 25 availability extraction tests passed.")