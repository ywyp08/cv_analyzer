import argparse
import json
import logging
from cv_analyzer.pipeline import analyze_cv

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    parser = argparse.ArgumentParser(description="AI CV Seniority & Salary Estimator")
    parser.add_argument("file", help="Path to CV file (PDF or DOCX)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    result = analyze_cv(args.file)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print("=== Seniority & Salary Estimator ===")
    print(f"File: {args.file}")
    print(f"Seniority Score: {result['seniority_score']}/100")
    print(f"Salary estimate: {result['salary_estimate']['min']}–{result['salary_estimate']['max']} CZK / měsíc")
    print("\nHighlights:")
    for item in result['summary_insights']:
        print(f"- {item}")
    print("\nLLM Explanation:\n")
    print(result['explanation'])


if __name__ == "__main__":
    main()
