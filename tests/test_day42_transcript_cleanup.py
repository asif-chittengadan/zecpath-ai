from screening_ai.transcript_normalizer import TranscriptNormalizer


def test_meaningful_like_is_preserved():
    normalizer = TranscriptNormalizer()

    result = normalizer.normalize(
        "I like Python and Django."
    )

    assert "like" in result
    assert "Python" in result
    assert "Django" in result


def test_filler_word_is_still_removed():
    normalizer = TranscriptNormalizer()

    result = normalizer.normalize(
        "Um, I am a Python developer."
    )

    assert "um" not in result.lower()
    assert "Python" in result
    assert "developer" in result