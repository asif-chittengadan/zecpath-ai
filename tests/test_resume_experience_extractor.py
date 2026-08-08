from parsers.pdf_reader import PDFReader
from parsers.text_cleaner import TextCleaner
from parsers.section_classifier import SectionClassifier
from parsers.resume_experience_extractor import ResumeExperienceExtractor
from parsers.requirement_extractor import RequirementExtractor

pdf_reader = PDFReader()
cleaner = TextCleaner()
classifier = SectionClassifier()
extractor = ResumeExperienceExtractor()

resume_path = "data/resumes/cv ASIF.pdf"

text = pdf_reader.extract_text(resume_path)
text = cleaner.clean(text)

sections = classifier.classify(text)

experience_lines = sections.get("Experience", [])

companies = extractor.extract_companies(experience_lines)

print("\nCompanies:")

for company in companies:
    print("-", company)

roles = extractor.extract_roles(experience_lines)

print("\nJob Titles:")

for role in roles:
    print("-", role)

dates = extractor.extract_dates(experience_lines)

print("\nEmployment Dates:")

for date in dates:
    print("-", date)

durations = extractor.extract_durations(experience_lines)

print("\nEmployment Durations:")

for duration in durations:
    print("-", duration)

total_experience = extractor.calculate_total_experience(
    dates,
    durations
)

print("\nTotal Experience:")

print(total_experience)

gaps = extractor.detect_gaps(dates)

print("\nEmployment Gaps:")

for gap in gaps:
    print("-", gap)

overlaps = extractor.detect_overlaps(dates)

print("\nOverlapping Roles:")

for overlap in overlaps:
    print("-", overlap)

if roles:
    required_role = "Data Analyst"

    relevance = extractor.calculate_role_relevance(
        roles[0],
        required_role
    )

    print("\nRole Relevance:")

    print(relevance)

    requirement_extractor = RequirementExtractor()

    job_text = """
    Responsibilities

    Analyze business data and create dashboards.
    Clean and transform datasets.
    Prepare reports and KPI analysis.
    """

    requirements = requirement_extractor.extract(job_text)

    print("\nJob Responsibilities:")

    for responsibility in requirements["responsibilities"]:
        print("-", responsibility)

    if roles:
        experience = {
            "role": roles[0],
            "description": []
        }

        relevance = extractor.calculate_experience_relevance(
            experience,
            requirements["responsibilities"]
        )

        print("\nRole Relevance:")

        print(relevance)

role_similarity = extractor.calculate_role_similarity(
    "Data Analytics Intern",
    "Data Analyst"
)

print("\nRole-to-Role Similarity:")

print(role_similarity)

structured_output = extractor.build_experience_output(
    companies,
    roles,
    dates,
    durations
)

print("\nStructured Experience Output:")

print(structured_output)