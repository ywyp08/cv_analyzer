import math
import re
from typing import Dict, Tuple


def _extract_years_from_text(text: str) -> float:
    if not text:
        return 0.0
    numbers = re.findall(r"(\d+(?:\.\d+)?)\s*(?:years|yrs|let|year)", text, flags=re.I)
    if numbers:
        return sum(float(value) for value in numbers)

    ranges = re.findall(r"(20\d{2})\s*[–-]\s*(20\d{2})", text)
    if ranges:
        total = 0
        for start, end in ranges:
            total += max(0, int(end) - int(start))
        return total

    return 0.0


def _education_score(level: str) -> int:
    if not level:
        return 4
    if "phd" in level.lower() or "doctor" in level.lower():
        return 15
    if "master" in level.lower() or "msc" in level.lower():
        return 12
    if "bachelor" in level.lower() or "bs" in level.lower() or "ba" in level.lower():
        return 8
    return 4


def _role_score(profile: Dict[str, object]) -> int:
    senior_roles = profile.get("senior_roles", [])
    if not senior_roles:
        return 8
    count = len(senior_roles)
    return min(15, 8 + count * 3)


def _skills_score(skills: list) -> int:
    if not skills:
        return 5
    score = min(30, 10 + len(skills) * 3)
    return score


def _potential_score(text: str) -> int:
    if not text:
        return 5
    keywords = ["strategic", "mentor", "coaching", "leadership", "innovation", "cross-functional", "scalable"]
    count = sum(1 for keyword in keywords if keyword in text.lower())
    return min(15, 5 + count * 2)


def calculate_scores(profile: Dict[str, object]) -> Dict[str, object]:
    years = _extract_years_from_text(profile.get("experience_text", ""))
    experience_score = min(30, int(years * 3.5) + 5)
    experience_score = max(0, experience_score)

    skills_score = _skills_score(profile.get("skills", []))
    education_score = _education_score(profile.get("education_level", ""))
    role_score = _role_score(profile)
    potential_score = _potential_score(profile.get("summary", ""))

    total = experience_score + skills_score + education_score + role_score + potential_score
    total = min(100, max(0, total))

    return {
        "seniority_score": total,
        "experience_years": round(years, 1),
        "experience_score": experience_score,
        "skills_score": skills_score,
        "education_score": education_score,
        "role_score": role_score,
        "potential_score": potential_score,
    }
