from parsers.certification_extractor import CertificationExtractor


extractor = CertificationExtractor()

text = [
    "Google Data Analytics Professional Certificate",
    "Coursera",
    "2025",
    "Credential ID: ABC123"
]

result = extractor.extract(text)

print("\nCertifications:")

for item in result:
    print(item)

test_names = [
    "aws certified cloud practitioner",
    "AWS  Certified   Cloud Practitioner",
    "Google Advanced Data Analytics Certificate"
]

print("\nNormalization:")

for name in test_names:

    print(
        name,
        "->",
        extractor.normalize_name(name)
    )