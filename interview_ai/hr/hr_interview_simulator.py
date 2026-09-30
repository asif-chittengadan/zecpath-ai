class HRInterviewSimulator:
    """
    Simulates HR interview sessions for different
    candidate behavior profiles.
    """

    CANDIDATE_TYPES = {
        "confident",
        "hesitant",
        "inexperienced",
        "overqualified"
    }

    DEFAULT_RESPONSES = {
        "confident": [
            "I have strong communication skills and can explain my approach clearly.",
            "I would identify the problem, analyze the options, and implement the most suitable solution.",
            "I am comfortable working independently and collaborating with a team."
        ],
        "hesitant": [
            "I think I could probably explain the situation, although I may need some time.",
            "I would first try to understand the problem and then maybe consider a few options.",
            "I can work with a team, but sometimes I need additional time to respond."
        ],
        "inexperienced": [
            "I have limited professional experience, but I have worked on academic projects.",
            "I would try to understand the problem and ask for guidance if necessary.",
            "I am willing to learn and improve my technical and communication skills."
        ],
        "overqualified": [
            "I have extensive experience solving similar problems and leading technical teams.",
            "I would evaluate the architecture, identify the root cause, and implement a scalable solution.",
            "I can independently handle complex responsibilities and mentor other team members."
        ]
    }

    def simulate(
        self,
        candidate_type,
        candidate_name="Test Candidate",
        responses=None
    ):
        candidate_type = (
            candidate_type.lower().strip()
            if isinstance(candidate_type, str)
            else ""
        )

        if candidate_type not in self.CANDIDATE_TYPES:
            raise ValueError(
                f"Unsupported candidate type: {candidate_type}"
            )

        if responses is None:
            responses = self.DEFAULT_RESPONSES[
                candidate_type
            ]

        if not isinstance(responses, list):
            responses = []

        return {
            "candidate_name": candidate_name,
            "candidate_type": candidate_type,
            "responses": responses,
            "response_count": len(responses)
        }

    def simulate_all(
        self,
        candidate_name_prefix="Test Candidate"
    ):
        sessions = []

        for candidate_type in sorted(
            self.CANDIDATE_TYPES
        ):
            sessions.append(
                self.simulate(
                    candidate_type=candidate_type,
                    candidate_name=(
                        f"{candidate_name_prefix} "
                        f"({candidate_type})"
                    )
                )
            )

        return sessions