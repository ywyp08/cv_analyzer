from typing import Dict, List


def _skill_salary_premium(skills: List[str]) -> int:
    skill_text = " ".join(skills).lower()
    premium = 0
    if any(term in skill_text for term in ["cloud", "aws", "azure", "gcp", "kubernetes", "docker", "terraform", "devops"]):
        premium += 5000
    if any(term in skill_text for term in ["data", "ml", "machine learning", "nlp", "sql", "nosql"]):
        premium += 4000
    if any(term in skill_text for term in ["security", "architecture", "architect"]):
        premium += 3000
    return min(premium, 9000)


def estimate_salary(score: int, profile: Dict[str, object]) -> Dict[str, int]:
    base = 30000 + int(score * 700)
    skill_bonus = _skill_salary_premium(profile.get("skills", []))
    base += skill_bonus

    min_salary = int(max(28000, base * 0.88) // 1000 * 1000)
    max_salary = int((base * 1.25 + 2000) // 1000 * 1000)
    min_salary = max(25000, min_salary)
    max_salary = max(min_salary, max_salary)

    return {
        "min": min_salary,
        "max": max_salary,
        "currency": "CZK",
        "confidence": "heuristic",
        "score_basis": "seniority + skills",
    }
