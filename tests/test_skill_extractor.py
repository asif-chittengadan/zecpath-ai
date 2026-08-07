from parsers.resume_skill_extractor import SkillExtractor

sample = [
    "Python",
    "JS",
    "MERN",
    "PowerBI",
    "Leadership",
    "Figma",
    "Pythn"
]

extractor = SkillExtractor()

result = extractor.extract(sample)

import json
print(json.dumps(result, indent=4))