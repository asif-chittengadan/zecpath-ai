import json
import re
import spacy
from datetime import datetime
from rapidfuzz import fuzz


class ResumeExperienceExtractor:

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

        with open(
            "data/roles.json",
            "r",
            encoding="utf-8"
        ) as file:
            self.roles = json.load(file)

        self.roles = sorted(
            self.roles,
            key=len,
            reverse=True
        )

    def extract_companies(self, section_lines):
        companies = []

        for line in section_lines:
            line = line.strip()

            if not line:
                continue

            if line.startswith("-") or line.startswith("•"):
                continue

            matched_role = None

            for role in self.roles:
                pattern = (
                    r"^"
                    + re.escape(role)
                    + r"\b"
                )

                if re.search(
                    pattern,
                    line,
                    re.IGNORECASE
                ):
                    matched_role = role
                    break

            if not matched_role:
                continue

            company = line[
                len(matched_role):
            ].strip()

            company = re.sub(
                r"^[,|:\-–—]+",
                "",
                company
            ).strip()

            if not company:
                continue

            if company not in companies:
                companies.append(company)

        return companies

    def extract_roles(self, section_lines):
        roles = []

        for line in section_lines:
            line = line.strip()

            if not line:
                continue

            if line.startswith("-") or line.startswith("•"):
                continue

            for role in self.roles:
                pattern = r"^" + re.escape(role) + r"\b"

                if re.search(pattern, line, re.IGNORECASE):
                    if role not in roles:
                        roles.append(role)

                    break

        return roles
    def extract_dates(self, section_lines):
        dates = []

        pattern = (
            r"(?i)"
            r"\b("
            r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
            r")[a-z]*\s+\d{4}"
            r"\s*[-–—]\s*"
            r"(Present|"
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*\s+\d{4})"
        )

        for line in section_lines:
            line = line.strip()

            if not line:
                continue

            match = re.search(pattern, line)

            if not match:
                continue

            dates.append({
                "start_date": match.group(1),
                "end_date": match.group(2),
                "text": match.group(0)
            })

        return dates

    def extract_durations(self, section_lines):
        durations = []

        patterns = [
            r"\b\d+(?:\.\d+)?\+?\s*years?\s+\d+\s*months?\b",
            r"\b\d+(?:\.\d+)?\+?\s*years?\b",
            r"\b\d+\s*months?\b"
        ]

        for line in section_lines:
            line = line.strip()

            if not line:
                continue

            for pattern in patterns:
                matches = re.findall(
                    pattern,
                    line,
                    re.IGNORECASE
                )

                for match in matches:
                    duration = re.sub(
                        r"\s+",
                        " ",
                        match
                    ).strip()

                    if duration not in durations:
                        durations.append(duration)

        return durations

    def calculate_total_experience(self, dates, durations):
        total_months = 0

        if dates:
            for date in dates:
                start = self.__parse_month_year(date["start_date"])

                if date["end_date"].lower() == "present":
                    end = datetime.now()
                else:
                    end = self.__parse_month_year(date["end_date"])

                if start is None or end is None:
                    continue

                months = (
                    (end.year - start.year) * 12
                    + (end.month - start.month)
                    + 1
                )

                if months > 0:
                    total_months += months

        elif durations:
            for duration in durations:
                total_months += self.__duration_to_months(duration)

        years = total_months // 12
        months = total_months % 12

        return {
            "total_months": total_months,
            "years": years,
            "months": months,
            "formatted": f"{years} years {months} months"
        }

    def __duration_to_months(self, duration):
        years = 0
        months = 0

        year_match = re.search(
            r"(\d+(?:\.\d+)?)\+?\s*years?",
            duration,
            re.IGNORECASE
        )

        month_match = re.search(
            r"(\d+)\s*months?",
            duration,
            re.IGNORECASE
        )

        if year_match:
            years = float(year_match.group(1))

        if month_match:
            months = int(month_match.group(1))

        return round(years * 12) + months
    
    def detect_gaps(self, dates):
        if len(dates) < 2:
            return []

        parsed_dates = []

        for date in dates:
            start = self.__parse_month_year(
                date["start_date"]
            )

            if date["end_date"].lower() == "present":
                end = datetime.now()
            else:
                end = self.__parse_month_year(
                    date["end_date"]
                )

            if start is None or end is None:
                continue

            parsed_dates.append({
                "start": start,
                "end": end
            })

        if len(parsed_dates) < 2:
            return []

        parsed_dates.sort(
            key=lambda item: item["start"]
        )

        gaps = []

        for index in range(1, len(parsed_dates)):
            previous = parsed_dates[index - 1]
            current = parsed_dates[index]

            previous_end = previous["end"]
            current_start = current["start"]

            gap_months = (
                (current_start.year - previous_end.year) * 12
                + (current_start.month - previous_end.month)
                - 1
            )

            if gap_months > 0:
                gaps.append({
                    "from": (
                        previous_end.strftime("%B %Y")
                    ),
                    "to": (
                        current_start.strftime("%B %Y")
                    ),
                    "months": gap_months
                })

        return gaps

    def detect_overlaps(self, dates):
        if len(dates) < 2:
            return []

        parsed_dates = []

        for date in dates:
            start = self.__parse_month_year(
                date["start_date"]
            )

            if date["end_date"].lower() == "present":
                end = datetime.now()
            else:
                end = self.__parse_month_year(
                    date["end_date"]
                )

            if start is None or end is None:
                continue

            parsed_dates.append({
                "start": start,
                "end": end
            })

        overlaps = []

        for i in range(len(parsed_dates)):
            for j in range(i + 1, len(parsed_dates)):
                first = parsed_dates[i]
                second = parsed_dates[j]

                if (
                    first["start"] <= second["end"]
                    and second["start"] <= first["end"]
                ):
                    overlap_start = max(
                        first["start"],
                        second["start"]
                    )

                    overlap_end = min(
                        first["end"],
                        second["end"]
                    )

                    overlap_months = (
                        (overlap_end.year - overlap_start.year) * 12
                        + (overlap_end.month - overlap_start.month)
                        + 1
                    )

                    if overlap_months > 0:
                        overlaps.append({
                            "from": overlap_start.strftime(
                                "%B %Y"
                            ),
                            "to": overlap_end.strftime(
                                "%B %Y"
                            ),
                            "months": overlap_months
                        })

        return overlaps

    def calculate_role_relevance(self, candidate_role, required_role):
        if not candidate_role or not required_role:
            return {
                "score": 0.0,
                "matched": False
            }

        candidate = candidate_role.strip().lower()
        required = required_role.strip().lower()

        if candidate == required:
            return {
                "score": 1.0,
                "matched": True
            }

        score = fuzz.token_set_ratio(
            candidate,
            required
        ) / 100

        return {
            "score": round(score, 2),
            "matched": score >= 0.70
        }
    
    def calculate_experience_relevance(self, experience, responsibilities):
        if not experience or not responsibilities:
            return {
                "score": 0.0,
                "matched": False
            }

        experience_text = " ".join([
            experience.get("role", ""),
            *experience.get("description", [])
        ]).strip().lower()

        if not experience_text:
            return {
                "score": 0.0,
                "matched": False
            }

        scores = []

        for responsibility in responsibilities:
            responsibility = responsibility.strip()

            if not responsibility:
                continue

            score = fuzz.token_set_ratio(
                experience_text,
                responsibility.lower()
            ) / 100

            scores.append(score)

        if not scores:
            return {
                "score": 0.0,
                "matched": False
            }

        best_score = max(scores)

        return {
            "score": round(best_score, 2),
            "matched": best_score >= 0.70
        }
    
    def calculate_role_similarity(self, role_one, role_two):
        if not role_one or not role_two:
            return {
                "role_one": role_one or "",
                "role_two": role_two or "",
                "score": 0.0,
                "similar": False
            }

        score = fuzz.token_set_ratio(
            role_one.lower().strip(),
            role_two.lower().strip()
        ) / 100

        return {
            "role_one": role_one,
            "role_two": role_two,
            "score": round(score, 2),
            "similar": score >= 0.70
        }
    
    def build_experience_output(
        self,
        companies,
        roles,
        dates,
        durations
    ):
        experiences = []

        count = max(
            len(companies),
            len(roles),
            len(dates),
            len(durations)
        )

        for index in range(count):
            experience = {
                "company": companies[index] if index < len(companies) else "",
                "role": roles[index] if index < len(roles) else "",
                "start_date": "",
                "end_date": "",
                "duration": durations[index] if index < len(durations) else "",
                "description": []
            }

            if index < len(dates):
                experience["start_date"] = dates[index]["start_date"]
                experience["end_date"] = dates[index]["end_date"]

            experiences.append(experience)

        return {
            "experiences": experiences,
            "total_experience": {
                "years": 0,
                "months": 0,
                "total_months": 0
            },
            "gaps": [],
            "overlaps": []
        }