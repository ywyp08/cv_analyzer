import re
from typing import Dict, List

SECTION_KEYWORDS = {
    "experience": ["experience", "work history", "professional experience", "employment", "projects", "roles"],
    "education": ["education", "qualifications", "study", "academic"],
    "skills": ["skills", "technical skills", "technologies", "competences"],
    "certifications": ["certifications", "certificates", "licences", "licenses"],
    "summary": ["summary", "profile", "about me", "career objective"],
}

TECHNICAL_SKILLS = [
    "python", "java", "c#", "javascript", "react", "angular", "node", "aws", "azure", "gcp",
    "docker", "kubernetes", "sql", "nosql", "postgresql", "mongodb", "terraform", "ci/cd",
    "data engineering", "machine learning", "nlp", "devops", "cloud", "scrum", "agile", "leadership",
]

SENIORITY_KEYWORDS = [
    "senior", "lead", "architect", "manager", "director", "principal", "head of", "team lead",
]

EDUCATION_LEVELS = ["phd", "doctor", "master", "msc", "bachelor", "bs", "ba", "degree"]


def _normalize_line(line: str) -> str:
    return line.strip().lower()


def parse_sections(text: str) -> Dict[str, str]:
    sections = {key: [] for key in SECTION_KEYWORDS}
    current = "summary"
    for line in text.splitlines():
        normalized = _normalize_line(line)
        if not normalized:
            continue
        for section, keys in SECTION_KEYWORDS.items():
            if any(key in normalized for key in keys):
                current = section
                break
        sections[current].append(line.strip())
    return {key: "\n".join(value) for key, value in sections.items()}


def parse_skills(text: str) -> List[str]:
    if not text:
        return []
    raw = re.sub(r"[•\n\r]+", ",", text)
    tokens = re.split(r"[,;/\\]| and | & ", raw, flags=re.I)
    skills = []
    for token in tokens:
        token = token.strip(" .\t")
        if len(token) < 2:
            continue
        skills.append(token.lower())
    return sorted({skill for skill in skills if len(skill) > 1})


def parse_profile_sections(sections: Dict[str, str]) -> Dict[str, object]:
    skills = parse_skills(sections.get("skills", ""))
    experience_text = sections.get("experience", "")
    education_text = sections.get("education", "")
    summary_text = sections.get("summary", "")

    extracted_skills = []
    for keyword in TECHNICAL_SKILLS:
        if keyword in experience_text.lower() or keyword in skills:
            extracted_skills.append(keyword)
    extracted_skills = sorted(set(extracted_skills + skills))

    senior_roles = []
    for keyword in SENIORITY_KEYWORDS:
        if keyword in experience_text.lower() or keyword in summary_text.lower():
            senior_roles.append(keyword)

    education_level = "Other"
    for term in ["phd", "doctor", "master", "msc", "bachelor", "bs", "ba"]:
        if term in education_text.lower():
            education_level = term.title()
            break

    return {
        "summary": summary_text,
        "experience_text": experience_text,
        "education_text": education_text,
        "skills": extracted_skills,
        "raw_skills": skills,
        "senior_roles": senior_roles,
        "education_level": education_level,
    }
