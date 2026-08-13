from parsers.education_extractor import EducationExtractor


extractor = EducationExtractor()


text = """
Eligibility & Qualifications

Education: BE / B.Tech in Computer Science or a closely related information technology discipline.
"""


education = extractor.extract(text)


print("Education:")

for item in education:
    print("-", item)