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

SKILL_BLACKLIST = {
    "skills", "technical skills", "experience", "education", "summary", "certifications", "profile"
}

KNOWN_HEADER_PHRASES = [
    *[phrase for values in SECTION_KEYWORDS.values() for phrase in values],
    "curriculum vitae", "cv", "životopis", "resume"
]


def _normalize_line(line: str) -> str:
    return line.strip().lower()


def parse_candidate_name(text: str) -> str:
    for line in (line.strip() for line in text.splitlines() if line.strip()):
        normalized = _normalize_line(line)
        if any(phrase in normalized for phrase in KNOWN_HEADER_PHRASES):
            continue
        if re.search(r"\d", line):
            continue
        words = [word for word in line.replace(".", "").replace(",", "").split() if word]
        if 1 < len(words) <= 4 and all(word[0].isupper() or word.isupper() for word in words if word[0].isalpha()):
            return line
        if 1 < len(words) <= 5 and len(line) < 40:
            return line
    return "Unknown"


def _is_section_header(line: str, key: str) -> bool:
    if len(line.split()) > 5:
        return False
    pattern = rf"(^|\s){re.escape(key)}(\s|$|[\.:,;\-])"
    return re.search(pattern, line) is not None


def parse_sections(text: str) -> Dict[str, str]:
    sections = {key: [] for key in SECTION_KEYWORDS}
    current = "summary"
    for line in text.splitlines():
        normalized = _normalize_line(line)
        if not normalized:
            continue

        section_header = None
        for section, keys in SECTION_KEYWORDS.items():
            if any(_is_section_header(normalized, key) for key in keys):
                section_header = section
                break
        if section_header:
            current = section_header
            continue

        sections[current].append(line.strip())
    return {key: "\n".join(value) for key, value in sections.items()}


def parse_skills(text: str) -> List[str]:
    if not text:
        return []
    raw = re.sub(r"[•\n\r]+", ",", text)
    tokens = re.split(r"[,;/\\]| and | & ", raw, flags=re.I)
    skills = []
    for token in tokens:
        token = token.strip(" .\t").lower()
        if len(token) < 2 or token in SKILL_BLACKLIST:
            continue
        if token.isdigit():
            continue
        skills.append(token)
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
