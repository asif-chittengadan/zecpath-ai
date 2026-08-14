from scoring.fairness_masker import FairnessMasker


resume = {
    "Others": [
        "ASIF C",
        "asifsifuoz6@gmail.com",
        "+91 8137876025",
        "linkedin",
        "github"
    ],
    "Skills": {
        "technical": [
            {
                "skill": "Python",
                "confidence": 1.0
            }
        ]
    }
}


masker = FairnessMasker()

masked = masker.mask(resume)

print("Original Others:")
print(resume["Others"])

print("\nMasked Others:")
print(masked["Others"])

print("\nSkills:")
print(masked["Skills"])