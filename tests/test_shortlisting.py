from scoring.shortlisting_module import ShortlistingModule


module = ShortlistingModule()


test_scores = [
    91.4,
    81.2,
    67.5,
    52.36
]


print("\n===== SHORTLISTING RESULTS =====\n")


for score in test_scores:

    status = module.classify(score)

    print(
        f"Score: {score}% → {status}"
    )