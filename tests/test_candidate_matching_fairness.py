from scoring.candidate_matching_service import (
    CandidateMatchingService,
)


def test_candidate_matching_service_uses_fairness_masker():
    service = CandidateMatchingService()

    assert hasattr(
        service,
        "fairness_masker"
    )

    assert service.fairness_masker is not None


def test_original_resume_is_not_modified():
    service = CandidateMatchingService()

    resume = {
        "Others": [
            "Candidate A"
        ],
        "personal_details": {
            "age": 25,
            "gender": "Male"
        },
        "contact": {
            "email": "candidate@example.com"
        },
        "Skills": {
            "technical": [
                "Python",
                "SQL"
            ]
        },
        "Experience": {
            "total_experience": {
                "years": 2
            }
        }
    }

    original_resume = {
        "Others": [
            "Candidate A"
        ],
        "personal_details": {
            "age": 25,
            "gender": "Male"
        },
        "contact": {
            "email": "candidate@example.com"
        },
        "Skills": {
            "technical": [
                "Python",
                "SQL"
            ]
        },
        "Experience": {
            "total_experience": {
                "years": 2
            }
        }
    }

    service.fairness_masker.mask_candidate(
        resume
    )

    assert resume == original_resume


def test_masked_resume_contains_job_relevant_data():
    service = CandidateMatchingService()

    resume = {
        "Others": [
            "Candidate A"
        ],
        "personal_details": {
            "age": 25,
            "gender": "Male"
        },
        "Skills": {
            "technical": [
                "Python",
                "SQL"
            ]
        },
        "Experience": {
            "total_experience": {
                "years": 2
            }
        },
        "Education": {
            "degree": "B.Tech",
            "field_of_study": "Information Technology"
        }
    }

    masked = service.fairness_masker.mask_candidate(
        resume
    )

    assert "age" not in masked.get(
        "personal_details",
        {}
    )

    assert "gender" not in masked.get(
        "personal_details",
        {}
    )

    assert masked["Skills"]["technical"] == [
        "Python",
        "SQL"
    ]

    assert masked["Experience"][
        "total_experience"
    ]["years"] == 2

    assert masked["Education"][
        "degree"
    ] == "B.Tech"