class EligibilityDecisionEngine:

    def evaluate(self, candidate, rules):
        ats_score = candidate.get("ats_score", 0)

        mandatory_skills = rules.get("mandatory_skills", [])
        candidate_skills = candidate.get("skills", [])

        experience_rules = rules.get("experience", {})
        candidate_experience = candidate.get("experience")

        location_rules = rules.get("location", [])
        candidate_location = candidate.get("location")

        availability_rules = rules.get("availability", [])
        candidate_availability = candidate.get("availability")

        minimum_ats_score = rules.get("minimum_ats_score", 0)

        failed_rules = []
        review_rules = []

        # ATS score check
        if ats_score < minimum_ats_score:
            failed_rules.append("ATS score below minimum")

        # Mandatory skills check
        candidate_skills_lower = {
            skill.lower() for skill in candidate_skills
        }

        missing_skills = [
            skill for skill in mandatory_skills
            if skill.lower() not in candidate_skills_lower
        ]

        if missing_skills:
            failed_rules.append(
                f"Missing mandatory skills: {', '.join(missing_skills)}"
            )

        # Experience check
        minimum_experience = experience_rules.get(
            "minimum"
        )

        maximum_experience = experience_rules.get(
            "maximum"
        )

        if candidate_experience is None:
            review_rules.append(
                "Experience information unavailable"
            )

        else:

            if minimum_experience is not None:

                if candidate_experience < minimum_experience:

                    failed_rules.append(
                        "Experience below minimum requirement"
                    )

            if maximum_experience is not None:

                if candidate_experience > maximum_experience:

                    failed_rules.append(
                        "Experience above maximum requirement"
                    )

        # Location check
        if location_rules:
            if not candidate_location:
                review_rules.append("Location information unavailable")
            elif candidate_location not in location_rules:
                failed_rules.append("Location requirement not satisfied")

        # Availability check
        if availability_rules:
            if not candidate_availability:
                review_rules.append("Availability information unavailable")
            elif candidate_availability not in availability_rules:
                failed_rules.append("Availability requirement not satisfied")

        # Final decision
        if failed_rules:
            decision = "Rejected"
        elif review_rules:
            decision = "Review"
        else:
            decision = "Eligible"

        return {
            "decision": decision,
            "ats_score": ats_score,
            "failed_rules": failed_rules,
            "review_rules": review_rules,
            "missing_mandatory_skills": missing_skills
        }