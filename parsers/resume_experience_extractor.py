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

            parts = [
                part.strip()
                for part in re.split(
                    r"\s*\|\s*",
                    line
                )
                if part.strip()
            ]

            # -----------------------------
            # Role | Company | Location
            # -----------------------------

            if len(parts) >= 2:

                role_part = parts[0]

                matched_role = None

                for role in self.roles:

                    if re.match(
                        r"^" + re.escape(role) + r"\b",
                        role_part,
                        re.IGNORECASE
                    ):
                        matched_role = role
                        break

                if matched_role:

                    company = parts[1].strip()

                    if company and company not in companies:
                        companies.append(company)

                    continue

            # -----------------------------
            # PDF text without |
            # Role Company Location
            # -----------------------------

            matched_role = None

            for role in self.roles:

                if re.match(
                    r"^" + re.escape(role) + r"\b",
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

            # Remove ONLY the final "City, State"
            # Example:
            # TechNova Analytics Pvt. Ltd. Bengaluru, Karnataka
            # -> TechNova Analytics Pvt. Ltd.
            company = re.sub(
                r"\s+[A-Z][A-Za-z]+,\s+[A-Z][A-Za-z]+$",
                "",
                company
            ).strip()

            if company and company not in companies:
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

            parts = [
                part.strip()
                for part in re.split(
                    r"\s*\|\s*",
                    line
                )
                if part.strip()
            ]

            role_text = parts[0] if parts else line

            for role in self.roles:

                if re.match(
                    r"^" + re.escape(role) + r"\b",
                    role_text,
                    re.IGNORECASE
                ):

                    if role not in roles:
                        roles.append(role)

                    break

        return roles

    def extract_dates(self, section_lines):

        dates = []

        pattern = re.compile(
            r"\b("
            r"January|February|March|April|May|June|July|August|"
            r"September|October|November|December|"
            r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
            r")"
            r"\s+"
            r"((?:19|20)\d{2})"
            r"\s*(?:[-–—|]|to)?\s*"
            r"(Present|"
            r"(?:January|February|March|April|May|June|July|August|"
            r"September|October|November|December|"
            r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\s+(?:19|20)\d{2})",
            re.IGNORECASE
        )

        for line in section_lines:

            line = line.strip()

            if not line:
                continue

            match = pattern.search(line)

            if not match:
                continue

            start_date = (
                match.group(1)
                + " "
                + match.group(2)
            )

            end_date = match.group(3).strip()

            dates.append({
                "start_date": start_date,
                "end_date": end_date,
                "text": match.group(0)
            })

        return dates

    def extract_durations(self, section_lines):
        durations = []

        patterns = [
            r"(?<![-\d])\d+(?:\.\d+)?\+?\s*years?\s+\d+\s*months?\b",
            r"(?<![-\d])\d+(?:\.\d+)?\+?\s*years?\b",
            r"(?<![-\d])\d+\s*months?\b"
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

    def __parse_month_year(self, value):

        if not isinstance(value, str) or not value.strip():
            return None

        value = value.strip()

        formats = [
            "%B %Y",
            "%b %Y"
        ]

        for date_format in formats:

            try:
                return datetime.strptime(
                    value,
                    date_format
                )

            except ValueError:
                continue

        return None

    def calculate_total_experience(self, dates, durations):
        intervals = self.__validated_intervals(dates)
        total_months = 0
        if intervals:
            intervals = [
                (interval["start"], interval["end"])
                for interval in intervals
            ]
            intervals.sort()
            merged_start, merged_end = intervals[0]
            for start, end in intervals[1:]:
                start_month = start.year * 12 + start.month
                end_month = end.year * 12 + end.month
                merged_end_month = merged_end.year * 12 + merged_end.month
                if start_month <= merged_end_month + 1:
                    if end_month > merged_end_month:
                        merged_end = end
                else:
                    total_months += merged_end_month - (
                        merged_start.year * 12 + merged_start.month
                    ) + 1
                    merged_start, merged_end = start, end
            total_months += (
                merged_end.year * 12 + merged_end.month
                - (merged_start.year * 12 + merged_start.month)
                + 1
            )
        else:
            if isinstance(durations, str):
                durations = [durations]
            for duration in durations or []:
                total_months += self.__duration_to_months(duration)

        years = total_months // 12
        months = total_months % 12

        return {
            "total_months": total_months,
            "years": years,
            "months": months,
            "formatted": f"{years} years {months} months"
        }

    def __validated_intervals(self, dates):
        now = datetime.now()
        intervals = []
        if not isinstance(dates, (list, tuple)):
            return intervals
        for date in dates:
            if not isinstance(date, dict):
                continue

            start = self.__parse_month_year(date.get("start_date"))
            end_value = date.get("end_date")
            if isinstance(end_value, str) and end_value.strip().lower() == "present":
                end = now
            else:
                end = self.__parse_month_year(end_value)

            if start is None or end is None:
                continue
            if end > now:
                end = now
            if end < start:
                continue
            intervals.append({"start": start, "end": end})
        return intervals

    def extract(self, section_lines):
        """Parse experience lines into a stable structured section."""
        if isinstance(section_lines, str):
            lines = section_lines.splitlines()
        else:
            lines = [str(line) for line in (section_lines or []) if line is not None]

        companies = self.extract_companies(lines)
        roles = self.extract_roles(lines)
        dates = self.extract_dates(lines)
        durations = self.extract_durations(lines)
        result = self.build_experience_output(
            companies,
            roles,
            dates,
            durations,
        )
        result["total_experience"] = self.calculate_total_experience(
            dates,
            durations,
        )
        result["gaps"] = self.detect_gaps(dates)
        result["overlaps"] = self.detect_overlaps(dates)
        return result

    def __duration_to_months(self, duration):
        if not isinstance(duration, str):
            return 0

        years = 0
        months = 0

        year_match = re.search(
            r"(-?\d+(?:\.\d+)?)\+?\s*years?",
            duration,
            re.IGNORECASE
        )

        month_match = re.search(
            r"(-?\d+)\s*months?",
            duration,
            re.IGNORECASE
        )

        if year_match:
            years = float(year_match.group(1))

        if month_match:
            months = int(month_match.group(1))

        if years < 0 or months < 0:
            return 0

        return round(years * 12) + months

    def calculate_experience_duration(self, start_date, end_date):

        start = self.__parse_month_year(start_date)

        if not start:
            return ""

        if isinstance(end_date, str) and end_date.strip().lower() == "present":
            end = datetime.now()
        else:
            end = self.__parse_month_year(end_date)

        if not end:
            return ""

        now = datetime.now()
        if end > now:
            end = now
        if end < start:
            return ""

        months = (
            (end.year - start.year) * 12
            + (end.month - start.month)
            + 1
        )

        if months <= 0:
            return ""

        years = months // 12
        remaining_months = months % 12

        if years and remaining_months:
            return f"{years} years {remaining_months} months"

        if years:
            return f"{years} years"

        return f"{remaining_months} months"
    
    def detect_gaps(self, dates):
        if not dates or len(dates) < 2:
            return []

        parsed_dates = self.__validated_intervals(dates)

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
        if not dates or len(dates) < 2:
            return []

        parsed_dates = self.__validated_intervals(dates)

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

            start_date = ""
            end_date = ""

            if index < len(dates):
                start_date = dates[index]["start_date"]
                end_date = dates[index]["end_date"]

            duration = ""

            if start_date and end_date:
                duration = self.calculate_experience_duration(
                    start_date,
                    end_date
                )
            elif index < len(durations):
                duration = durations[index]

            experience = {
                "company": (
                    companies[index]
                    if index < len(companies)
                    else ""
                ),
                "role": (
                    roles[index]
                    if index < len(roles)
                    else ""
                ),
                "start_date": start_date,
                "end_date": end_date,
                "duration": duration
            }

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
