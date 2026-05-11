import logging
from .extract import extract_text_from_file
from .structure import parse_sections, parse_profile_sections
from .scoring import calculate_scores
from .llm import generate_explanation

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


def analyze_cv(path: str) -> dict:
    logger.info("Začínám analýzu souboru %s", path)
    raw_text = extract_text_from_file(path)
    sections = parse_sections(raw_text)
    profile = parse_profile_sections(sections)
    scores = calculate_scores(profile)
    explanation = generate_explanation(profile, scores, scores["salary_estimate"])
    result = {
        "seniority_score": scores["seniority_score"],
        "salary_estimate": scores["salary_estimate"],
        "scores": scores,
        "profile": profile,
        "summary_insights": _build_summary_insights(profile, scores, scores["salary_estimate"]),
        "explanation": explanation,
    }
    logger.info("Analýza dokončena: Seniority %s, Mzda %s-%s", scores["seniority_score"], scores["salary_estimate"]["min"], scores["salary_estimate"]["max"])
    return result
