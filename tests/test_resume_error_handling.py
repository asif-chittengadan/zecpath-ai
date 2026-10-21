import pytest

import parsers.resume_engine as resume_engine_module
from parsers.resume_engine import ResumeEngine
from parsers.resume_errors import (
    ResumeExtractionError,
    ResumeInputError,
    ResumeOutputError,
    UnsupportedResumeFormatError,
)
from parsers.resume_section_parser import ResumeSectionParser


class StubReader:
    def __init__(self, text=None, error=None):
        self.text = text
        self.error = error

    def extract_text(self, file_path):
        if self.error:
            raise self.error
        return self.text


def test_resume_engine_reports_missing_and_unsupported_inputs(tmp_path):
    engine = ResumeEngine()

    with pytest.raises(ResumeInputError, match="path is required"):
        engine.process("")

    with pytest.raises(FileNotFoundError, match="Resume file not found"):
        engine.process(tmp_path / "missing.pdf")

    unsupported = tmp_path / "resume.txt"
    unsupported.write_text("resume", encoding="utf-8")
    with pytest.raises(UnsupportedResumeFormatError, match="PDF and DOCX"):
        engine.process(unsupported)


def test_section_parser_uses_same_input_errors(tmp_path):
    parser = ResumeSectionParser.__new__(ResumeSectionParser)
    unsupported = tmp_path / "resume.txt"
    unsupported.write_text("resume", encoding="utf-8")

    with pytest.raises(UnsupportedResumeFormatError):
        parser.parse(unsupported)


def test_resume_engine_wraps_reader_errors_and_rejects_empty_text(
    monkeypatch,
    tmp_path,
):
    resume_path = tmp_path / "resume.pdf"
    resume_path.write_bytes(b"test fixture")
    reader_error = OSError("low-level parser detail")
    monkeypatch.setattr(
        resume_engine_module,
        "PDFReader",
        lambda: StubReader(error=reader_error),
    )

    with pytest.raises(ResumeExtractionError, match="Could not read resume") as error:
        ResumeEngine().process(resume_path)
    assert error.value.__cause__ is reader_error

    monkeypatch.setattr(
        resume_engine_module,
        "PDFReader",
        lambda: StubReader(text=" \n "),
    )
    with pytest.raises(ResumeExtractionError, match="No readable text"):
        ResumeEngine().process(resume_path)


def test_resume_engine_wraps_output_errors_and_preserves_complete_stem(
    monkeypatch,
    tmp_path,
):
    resume_path = tmp_path / "resume.version2.pdf"
    resume_path.write_bytes(b"test fixture")
    monkeypatch.setattr(
        resume_engine_module,
        "PDFReader",
        lambda: StubReader(text="Summary\nBackend engineer with Python experience."),
    )

    class FailingWriter:
        def save(self, filename, text):
            raise OSError("permission denied")

    monkeypatch.setattr(
        resume_engine_module,
        "OutputWriter",
        FailingWriter,
    )
    with pytest.raises(ResumeOutputError, match="Could not save"):
        ResumeEngine().process(resume_path)

    saved = {}

    class RecordingWriter:
        def save(self, filename, text):
            saved["filename"] = filename
            saved["text"] = text

    monkeypatch.setattr(
        resume_engine_module,
        "OutputWriter",
        RecordingWriter,
    )
    result = ResumeEngine().process(resume_path)

    assert saved["filename"] == "resume.version2.txt"
    assert saved["text"] == result
