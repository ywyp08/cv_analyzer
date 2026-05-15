import argparse
import logging
from pipeline.pipeline import analyze_cv


def main():
    parser = argparse.ArgumentParser(description="AI CV Seniority & Salary Estimator")
    parser.add_argument("file", help="Path to CV file (PDF or DOCX)")
    args = parser.parse_args()

    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    result = analyze_cv(args.file)

    print("=== Seniority & Salary Estimator ===")
    print(f"Name: {result.get('name', 'Unknown')}")
    print(f"Seniority Score: {result['seniority_score']}/100")
    print(f"Salary estimate: {result['salary_estimate']['min']}–{result['salary_estimate']['max']} CZK / měsíc")
    print("\nLLM Explanation:")
    print(result['explanation'])


if __name__ == "__main__":
    main()
