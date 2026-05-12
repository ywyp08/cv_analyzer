from typing import Dict


def estimate_salary(score: int, profile: Dict[str, object]) -> Dict[str, int]:
    base = 39000 + int(score * 850)
    if any(term in " ".join(profile.get("skills", [])).lower() for term in ["cloud", "data", "ml", "devops", "architecture", "security"]):
        base += 4000
    if any(role in profile.get("senior_roles", []) for role in ["manager", "lead", "architect"]):
        base += 6000
    base = max(35000, base)
    min_salary = int(max(30000, base * 0.85) // 1000 * 1000)
    max_salary = int((base * 1.15 + 5000) // 1000 * 1000)
    return {
        "min": min_salary,
        "max": max_salary,
        "currency": "CZK",
        "confidence": "heuristic",
    }
