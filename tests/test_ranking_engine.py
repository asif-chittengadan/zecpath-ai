from scoring.ranking_engine import RankingEngine
from scoring.shortlisting_module import ShortlistingModule


engine = RankingEngine()
shortlisting = ShortlistingModule()


candidates = [
    {
        "candidate": "Asif C",
        "score": 52.36
    },
    {
        "candidate": "Rahul",
        "score": 81.20
    },
    {
        "candidate": "Akhil",
        "score": 67.50
    },
    {
        "candidate": "Vishnu",
        "score": 91.40
    }
]


ranked = engine.rank_candidates(
    candidates
)

output = engine.build_recruiter_output(
    ranked,
    shortlisting
)


print("\n===== RECRUITER-FRIENDLY OUTPUT =====\n")

for candidate in output:

    print(
        f'Rank {candidate["rank"]}: '
        f'{candidate["candidate"]} | '
        f'Score: {candidate["score"]}% | '
        f'Status: {candidate["status"]}'
    )