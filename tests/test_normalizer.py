from parsers.normalizer import Normalizer


normalizer = Normalizer()

test_headings = [
    "Professional Experience",
    "WORK EXPERIENCE:",
    "Technical Skills",
    "KEY SKILLS",
    "Academic Background",
    "Educational Qualifications",
    "Academic Projects",
    "Certificates",
    "Additional Information"
]

for heading in test_headings:

    print(
        heading,
        "->",
        normalizer.normalize(heading)
    )