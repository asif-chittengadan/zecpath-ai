from parsers.text_cleaner import TextCleaner


def test_clean_text():

    cleaner = TextCleaner()

    text = "Python     SQL *****"

    cleaned = cleaner.clean(text)

    assert "*****" not in cleaned