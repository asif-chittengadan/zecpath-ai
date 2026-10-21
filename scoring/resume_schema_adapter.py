"""Normalize structured resume parser output for ATS scoring."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any, Dict, Iterable, List, Optional


class ResumeSchemaAdapter:
    """Convert parser and legacy resume shapes to the ATS scoring schema."""

    @classmethod
    def to_ats_schema(cls, resume: Any) -> Dict[str, Any]:
        if not isinstance(resume, Mapping):
            raise TypeError("resume must be a dictionary-like object.")

        personal_info = cls._mapping(
            cls._get(resume, "personal_information", "personal_info")
        )
        name = cls._text(
            cls._get(personal_info, "name", "full_name")
        )
        other_values = cls._texts(
            cls._get(resume, "Others", "others")
        )
        if name:
            other_values = [
                value for value in other_values
                if value.casefold() != name.casefold()
            ]
            other_values.insert(0, name)

        return {
            "Summary": cls._texts(cls._get(resume, "Summary", "summary")),
            "Skills": cls._skills(cls._get(resume, "Skills", "skills")),
            "Experience": cls._experience(
                cls._get(resume, "Experience", "experience")
            ),
            "Education": cls._education(
                cls._get(resume, "Education", "education")
            ),
            "Projects": cls._projects(
                cls._get(resume, "Projects", "projects")
            ),
            "Others": other_values,
        }

    @classmethod
    def _skills(cls, value: Any) -> Dict[str, List[str]]:
        result = {"technical": [], "business": [], "creative": []}
        if isinstance(value, Mapping):
            category_aliases = {
                "technical": "technical",
                "tech": "technical",
                "technicalskills": "technical",
                "business": "business",
                "soft": "business",
                "softskills": "business",
                "businessskills": "business",
                "creative": "creative",
                "creativeskills": "creative",
            }
            found_category = False
            for key, items in value.items():
                normalized_key = cls._key(key)
                category = category_aliases.get(normalized_key)
                if category:
                    result[category].extend(cls._skill_texts(items))
                    found_category = True
                elif normalized_key in {"skills", "items", "values"}:
                    result["technical"].extend(cls._skill_texts(items))
                    found_category = True

            if not found_category:
                result["technical"].extend(cls._skill_texts(value))
        else:
            result["technical"].extend(cls._skill_texts(value))

        for category, items in result.items():
            result[category] = cls._dedupe(items)
        return result

    @classmethod
    def _skill_texts(cls, value: Any) -> List[str]:
        if isinstance(value, Mapping):
            skill = cls._get(value, "skill", "skill_name", "name", "value")
            if skill is not None:
                return cls._texts(skill)
            return []
        if isinstance(value, (list, tuple, set)):
            result: List[str] = []
            items = value
            if isinstance(value, set):
                items = sorted(value, key=lambda item: str(item).casefold())
            for item in items:
                result.extend(cls._skill_texts(item))
            return result
        return cls._texts(value)

    @classmethod
    def _experience(cls, value: Any) -> Dict[str, Any]:
        experience = cls._mapping(value)
        total = cls._mapping(
            cls._get(experience, "total_experience", "totalExperience")
        )
        if not total:
            total = experience

        total_months = cls._number(
            cls._get(total, "total_months", "totalMonths", "months_total")
        )
        years = cls._years(
            cls._get(total, "years", "total_years", "experience_years")
        )
        if total_months is not None and total_months < 0:
            total_months = None
        if years is not None and years < 0:
            years = None
        if total_months is not None:
            total_months = int(round(total_months))
            years = total_months / 12
        elif years is not None:
            remainder_months = cls._number(
                cls._get(total, "months", "remaining_months")
            )
            if remainder_months is not None and remainder_months < 0:
                remainder_months = None
            if remainder_months is not None and years.is_integer():
                years += remainder_months / 12
            total_months = int(round(years * 12))
        else:
            years = 0.0
            total_months = 0

        return {
            "total_experience": {
                "years": years,
                "months": total_months % 12,
                "total_months": total_months,
            }
        }

    @classmethod
    def _education(cls, value: Any) -> Dict[str, str]:
        if isinstance(value, Mapping):
            degree = cls._first_text(
                cls._get(value, "degree", "degrees", "degree_types", "qualification")
            )
            field = cls._first_text(
                cls._get(
                    value,
                    "field_of_study",
                    "fields_of_study",
                    "field",
                    "major",
                )
            )
            if not degree and not field:
                entries = cls._texts(
                    cls._get(value, "education", "entries", "qualifications")
                )
                degree = entries[0] if entries else ""
        elif isinstance(value, (list, tuple)):
            entries = cls._texts(value)
            degree = entries[0] if entries else ""
            field = ""
        else:
            degree = cls._text(value)
            field = ""

        return {"degree": degree, "field_of_study": field}

    @classmethod
    def _projects(cls, value: Any) -> List[str]:
        if isinstance(value, Mapping):
            value = [value]
        if not isinstance(value, (list, tuple, set)):
            return cls._texts(value)

        result: List[str] = []
        projects = value
        if isinstance(value, set):
            projects = sorted(value, key=lambda item: str(item).casefold())
        for project in projects:
            if isinstance(project, Mapping):
                parts: List[str] = []
                for key in ("title", "name", "description", "summary", "technologies"):
                    parts.extend(cls._texts(cls._get(project, key)))
                result.extend(parts)
            else:
                result.extend(cls._texts(project))
        return cls._dedupe(result)

    @classmethod
    def _texts(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            text = value.strip()
            return [text] if text else []
        if isinstance(value, Mapping):
            for key in ("text", "value", "name", "title", "description", "summary"):
                nested = cls._get(value, key)
                if nested is not None:
                    return cls._texts(nested)
            return []
        if isinstance(value, (list, tuple, set)):
            result: List[str] = []
            items = value
            if isinstance(value, set):
                items = sorted(value, key=lambda item: str(item).casefold())
            for item in items:
                result.extend(cls._texts(item))
            return result
        return []

    @classmethod
    def _first_text(cls, value: Any) -> str:
        values = cls._texts(value)
        return values[0] if values else ""

    @classmethod
    def _text(cls, value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, (int, float)):
            return str(value)
        return ""

    @classmethod
    def _years(cls, value: Any) -> Optional[float]:
        numeric = cls._number(value)
        if numeric is not None:
            return numeric
        if not isinstance(value, str):
            return None
        year_match = re.search(r"(-?\d+(?:\.\d+)?)\s*years?", value, re.I)
        month_match = re.search(r"(-?\d+)\s*months?", value, re.I)
        if year_match:
            years = float(year_match.group(1))
            months = int(month_match.group(1)) if month_match else 0
            if years < 0 or months < 0:
                return None
            return years + months / 12
        if month_match:
            months = int(month_match.group(1))
            return months / 12 if months >= 0 else None
        return None

    @staticmethod
    def _number(value: Any) -> Optional[float]:
        if isinstance(value, bool) or value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return None
        return number if math.isfinite(number) else None

    @classmethod
    def _get(cls, mapping: Any, *keys: str) -> Any:
        if not isinstance(mapping, Mapping):
            return None
        wanted = {cls._key(key) for key in keys}
        for key, value in mapping.items():
            if cls._key(key) in wanted:
                return value
        return None

    @staticmethod
    def _key(value: Any) -> str:
        return re.sub(r"[^a-z0-9]", "", str(value).lower())

    @staticmethod
    def _mapping(value: Any) -> Mapping:
        return value if isinstance(value, Mapping) else {}

    @staticmethod
    def _dedupe(values: Iterable[str]) -> List[str]:
        result: List[str] = []
        seen = set()
        for value in values:
            text = str(value).strip()
            key = text.casefold()
            if text and key not in seen:
                result.append(text)
                seen.add(key)
        return result
