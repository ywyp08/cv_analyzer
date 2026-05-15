import logging
from .processing import extract_text_from_file, parse_sections, parse_profile_sections
from .processing.structure import parse_candidate_name
from .scoring import calculate_scores
from .scoring.salary import estimate_salary
from .explaining import generate_explanation

logger = logging.getLogger(__name__)


def _build_summary_insights(profile: dict, scores: dict, salary: dict) -> list:
    items = []
    items.append(f"Experience: {scores['experience_years']} let")
    if profile.get("senior_roles"):
        items.append(f"Senior roles: {', '.join(profile['senior_roles'])}")
    if profile.get("skills"):
        items.append(f"Klíčové dovednosti: {', '.join(profile['skills'][:8])}")
    items.append(f"Vzdělání: {profile.get('education_level', 'N/A')}")
    items.append(f"Odhad mzdy: {salary['min']}–{salary['max']} CZK / měsíc")
    return items


def _validate_result(result: dict) -> list:
    warnings = []
    score = result.get("seniority_score", 0)
    if score < 0 or score > 100:
        warnings.append("Seniority score is outside the expected 0-100 range.")

    years = result.get("scores", {}).get("experience_years", 0)
    if years < 0:
        warnings.append("Extracted experience years are negative.")
    if years > 40:
        warnings.append("Experience looks unusually high; verify CV date parsing.")

    salary = result.get("salary_estimate", {})
    if salary.get("min", 0) > salary.get("max", 0):
        warnings.append("Salary range is invalid: min > max.")
    if salary.get("min", 0) < 30000:
        warnings.append("Estimated salary is very low; check data extraction.")
    if salary.get("max", 0) > 300000:
        warnings.append("Estimated salary is very high; verify seniority and skill detection.")

    if not result.get("profile", {}).get("skills"):
        warnings.append("No skills were extracted from the CV.")
    if not result.get("profile", {}).get("experience_text"):
        warnings.append("No experience section was detected.")
    return warnings


def analyze_cv(path: str) -> dict:
    logger.info("Začínám analýzu souboru %s", path)
    raw_text = extract_text_from_file(path)
    candidate_name = parse_candidate_name(raw_text)
    sections = parse_sections(raw_text)
    profile = parse_profile_sections(sections)
    scores = calculate_scores(profile)
    salary_estimate = estimate_salary(scores["seniority_score"], profile)
    scores["salary_estimate"] = salary_estimate
    explanation = generate_explanation(profile, scores, salary_estimate)
    result = {
        "name": candidate_name,
        "seniority_score": scores["seniority_score"],
        "salary_estimate": salary_estimate,
        "scores": scores,
        "profile": profile,
        "summary_insights": _build_summary_insights(profile, scores, salary_estimate),
        "explanation": explanation,
    }
    result["warnings"] = _validate_result(result)
    if result["warnings"]:
        logger.warning("Sanity check warnings: %s", "; ".join(result["warnings"]))
    logger.info("Analýza dokončena: Seniority %s, Mzda %s-%s", scores["seniority_score"], salary_estimate["min"], salary_estimate["max"])
    return result
