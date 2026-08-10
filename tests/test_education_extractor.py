from parsers.education_extractor import EducationExtractor


extractor = EducationExtractor()

text = """
Bachelor of Technology in Information Technology
Cochin University of Science and Technology
Graduated: April 2026
"""

degrees = extractor.extract_degree(text)
fields = extractor.extract_field_of_study(text)

print("Degree Types:")

for degree in degrees:
    print("-", degree)

print("\nFields of Study:")

for field in fields:
    print("-", field)

institution = extractor.extract_institution(text)

print("\nInstitutions:")

for item in institution:
    print("-", item)

graduation_year = extractor.extract_graduation_year(text)

print("\nGraduation Year:")

print("-", graduation_year)

text = """
Cochin University of Science and Technology
Bachelor of Technology In Information Technology
CGPA: 7.84/10
Graduated: April 2026
"""

print("\nInstitutions:")

institutions = extractor.extract_institution(text)

for institution in institutions:
    print("-", institution)