"""Build JSON and Markdown hiring profile exports from Day 53 demo inputs."""

import json
from pathlib import Path

from scoring.reports import HiringIntelligenceReportGenerator


ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "data" / "hiring_reports" / "day53_demo_inputs.json"
OUTPUT_DIRECTORY = ROOT / "data" / "hiring_reports"


def main():
    with INPUT_PATH.open("r", encoding="utf-8") as file:
        inputs = json.load(file)

    generator = HiringIntelligenceReportGenerator()
    final_recommendation = inputs.pop("final_recommendation", None)
    report = generator.generate_report(
        **inputs,
        final_recommendation=final_recommendation,
    )
    report["notice"] = (
        "Demonstration only: all values are illustrative and do not describe "
        "a real candidate."
    )
    exports = generator.save_exports(
        report,
        output_directory=OUTPUT_DIRECTORY,
        basename="day53_demo_candidate_profile",
    )

    print(f"JSON report: {exports['json']}")
    print(f"Markdown report: {exports['markdown']}")


if __name__ == "__main__":
    main()
