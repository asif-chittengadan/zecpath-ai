from copy import deepcopy

from parsers.resume_education_extractor import EducationExtractor
from parsers.resume_experience_extractor import ResumeExperienceExtractor
from scoring.candidate_matching_service import CandidateMatchingService
from scoring.fairness_masker import FairnessMasker
from scoring.resume_schema_adapter import ResumeSchemaAdapter


class RecordingSemanticEngine:
    def __init__(self):
        self.candidate_skills = None
        self.candidate_text = None

    def calculate_skill_similarity(self, candidate_skills, required_skills):
        self.candidate_skills = candidate_skills
        return {"score": 0.8}

    def calculate_similarity(self, candidate_text, job_text):
        self.candidate_text = candidate_text
        return 0.6


class RecordingScoreGenerator:
    def generate(self, **values):
        return values


def test_adapter_accepts_parser_output_and_legacy_skill_lists():
    parser_resume = {
        "personal_information": {"name": "Ada Lovelace"},
        "summary": ["Backend developer"],
        "skills": {
            "technical": [
                {"skill": "Python", "confidence": 0.98},
                {"skill": "SQL", "confidence": 0.95},
            ],
            "summary": {"technical_count": 2},
        },
        "experience": {
            "total_experience": {
                "years": 1,
                "months": 6,
                "total_months": 18,
            }
        },
        "education": {
            "degrees": ["Bachelor of Technology"],
            "fields_of_study": ["Computer Science"],
        },
        "projects": [
            {
                "title": "Inventory API",
                "description": ["Built a REST API"],
                "technologies": ["Python", "SQL"],
            }
        ],
    }

    normalized = ResumeSchemaAdapter.to_ats_schema(parser_resume)

    assert normalized["Others"] == ["Ada Lovelace"]
    assert normalized["Skills"]["technical"] == ["Python", "SQL"]
    assert normalized["Experience"]["total_experience"]["years"] == 1.5
    assert normalized["Education"] == {
        "degree": "Bachelor of Technology",
        "field_of_study": "Computer Science",
    }
    assert "Inventory API" in normalized["Projects"]
    assert "Built a REST API" in normalized["Projects"]

    legacy_list_resume = ResumeSchemaAdapter.to_ats_schema(
        {"Skills": ["Python", {"skill": "SQL"}]}
    )
    assert legacy_list_resume["Skills"]["technical"] == ["Python", "SQL"]

    partial_experience = ResumeSchemaAdapter.to_ats_schema(
        {"experience": {"total_experience": {"years": 2, "months": 6}}}
    )
    assert partial_experience["Experience"]["total_experience"]["years"] == 2.5


def test_candidate_matching_service_scores_parser_schema_without_mutating_it():
    service = CandidateMatchingService.__new__(CandidateMatchingService)
    service.semantic_engine = RecordingSemanticEngine()
    service.score_generator = RecordingScoreGenerator()
    service.fairness_masker = FairnessMasker()

    resume = {
        "personal_information": {"name": "Ada Lovelace", "age": 36},
        "summary": ["Backend developer"],
        "skills": {"technical": [{"skill": "Python"}, {"skill": "SQL"}]},
        "experience": {"total_experience": {"total_months": 18}},
        "education": {
            "degrees": ["Bachelor of Technology"],
            "fields_of_study": ["Computer Science"],
        },
        "projects": [{"title": "Inventory API", "description": ["REST API"]}],
    }
    original = deepcopy(resume)
    job_description = {
        "role": "Backend Developer",
        "skills": ["Python", "SQL"],
        "experience": {"minimum": 1, "maximum": 4, "text": "1 to 4 years"},
        "education": ["Computer Science"],
    }

    result = service.generate_score(resume, job_description)

    assert result["candidate_name"] == "Ada Lovelace"
    assert service.semantic_engine.candidate_skills == ["Python", "SQL"]
    assert "Ada Lovelace" not in service.semantic_engine.candidate_text
    assert "Inventory API" in service.semantic_engine.candidate_text
    assert resume == original


def test_resume_section_extractors_return_structured_results_and_merge_overlaps():
    education = EducationExtractor.__new__(EducationExtractor)
    education.degree_types = ["Bachelor of Technology"]
    education.fields_of_study = ["Computer Science"]
    education_result = education.extract(
        [
            "Bachelor of Technology in Computer Science | Example University | Bengaluru",
            "Graduated 2021",
        ]
    )

    assert education_result["degrees"] == ["Bachelor of Technology"]
    assert education_result["fields_of_study"] == ["Computer Science"]
    assert education_result["institutions"] == ["Example University"]
    assert education_result["graduation_year"] == 2021

    experience = ResumeExperienceExtractor.__new__(ResumeExperienceExtractor)
    experience.roles = ["Software Engineer", "Developer"]
    experience_result = experience.extract(
        [
            "Software Engineer | Acme Ltd",
            "January 2020 - December 2020",
            "Developer | Beta Labs",
            "June 2020 - May 2021",
        ]
    )

    assert experience_result["total_experience"]["total_months"] == 17
    assert experience_result["overlaps"][0]["months"] == 7
    assert len(experience_result["experiences"]) == 2
