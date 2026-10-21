"""Typed errors and input validation for resume-processing entry points."""

from pathlib import Path
from typing import Union


class ResumeProcessingError(Exception):
    """Base class for safe, user-facing resume processing errors."""


class ResumeInputError(ResumeProcessingError, ValueError):
    """Raised when a supplied resume path or input is invalid."""


class UnsupportedResumeFormatError(ResumeInputError):
    """Raised when the resume file extension is unsupported."""


class ResumeExtractionError(ResumeProcessingError):
    """Raised when no usable text can be extracted from a resume."""


class ResumeParsingError(ResumeProcessingError):
    """Raised when extracted resume text cannot be structured."""


class ResumeOutputError(ResumeProcessingError):
    """Raised when processed resume output cannot be saved."""


def validate_resume_path(file_path: Union[str, Path]) -> Path:
    """Validate a resume file path and return its normalized Path."""
    if file_path is None:
        raise ResumeInputError("A resume file path is required.")
    if isinstance(file_path, str) and not file_path.strip():
        raise ResumeInputError("A resume file path is required.")

    try:
        path = Path(file_path)
    except (TypeError, ValueError, OSError) as exc:
        raise ResumeInputError("The resume file path is invalid.") from exc

    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {path.name or path}")
    if not path.is_file():
        raise ResumeInputError("The resume path must point to a file.")

    extension = path.suffix.lower()
    if extension not in {".pdf", ".docx"}:
        raise UnsupportedResumeFormatError(
            f"Unsupported resume format '{extension or 'unknown'}'. "
            "Supported formats are PDF and DOCX."
        )

    return path
