import json
import os


CV_FOLDER = "data/labeled_resumes"
JD_FOLDER = "data/parsed_jd"
TEST_CASES = "tests/day17_test_cases.json"


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    cases = load_json(
        TEST_CASES
    )

    for case in cases:

        cv_path = os.path.join(
            CV_FOLDER,
            case["cv_file"]
        )

        jd_path = os.path.join(
            JD_FOLDER,
            case["jd_file"]
        )

        cv = load_json(cv_path)
        jd = load_json(jd_path)

        print("\n" + "=" * 70)

        print(
            f'{case["test_id"]} | '
            f'{case["cv_file"]} | '
            f'{case["jd_file"]}'
        )

        print("\nCV:")

        others = cv.get(
            "Others",
            []
        )

        print(
            "Candidate:",
            others[0] if others else "Unknown"
        )

        skills = cv.get(
            "Skills",
            {}
        )

        technical = [
            item.get("skill", "")
            for item in skills.get(
                "technical",
                []
            )
        ]

        print(
            "Technical Skills:",
            technical
        )

        education = cv.get(
            "Education",
            {}
        )

        print(
            "Education:",
            education
        )

        experience = cv.get(
            "Experience",
            {}
        )

        print(
            "Experience:",
            experience.get(
                "total_experience",
                {}
            )
        )

        print("\nJD:")

        print(
            "Role:",
            jd.get(
                "role",
                ""
            )
        )

        print(
            "Skills:",
            jd.get(
                "skills",
                []
            )
        )

        print(
            "Experience:",
            jd.get(
                "experience",
                {}
            )
        )

        print(
            "Education:",
            jd.get(
                "education",
                []
            )
        )


if __name__ == "__main__":
    main()