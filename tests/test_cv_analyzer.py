import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cv_analyzer.structure import parse_sections, parse_skills, parse_profile_sections
from cv_analyzer.scoring import calculate_scores, estimate_salary, _extract_years_from_text, _education_score, _skills_score
from cv_analyzer.llm import _fallback_explanation
from cv_analyzer.pipeline import analyze_cv


class TestStructure:
    def test_parse_sections_basic(self):
        text = """
        Jan Novák
        Experienced developer.
        
        Experience
        Senior Developer at ABC (2020–2024)
        
        Skills
        Python, AWS, Docker
        
        Education
        Master of Science
        """
        sections = parse_sections(text)
        assert "experience" in sections
        assert "skills" in sections
        assert "education" in sections
        assert "Senior Developer" in sections["experience"]

    def test_parse_skills_basic(self):
        skills_text = "Python, AWS, Docker / Kubernetes, and CI/CD"
        skills = parse_skills(skills_text)
        assert "python" in skills
        assert "aws" in skills
        assert "docker" in skills
        assert len(skills) > 0

    def test_parse_skills_empty(self):
        skills = parse_skills("")
        assert skills == []

    def test_parse_profile_sections(self):
        sections = {
            "experience": "Senior Python Developer at Acme (2018–2024). Led team of 5. AWS, Kubernetes, Docker.",
            "skills": "Python, AWS, Docker, Kubernetes",
            "education": "Master of Science in Computer Science",
            "summary": "Strategic thinker with mentoring experience"
        }
        profile = parse_profile_sections(sections)
        assert "python" in profile["skills"]
        assert "aws" in profile["skills"]
        assert profile["education_level"] == "Master"
        assert len(profile["senior_roles"]) > 0


class TestScoring:
    def test_extract_years_from_text_explicit(self):
        text = "Worked for 7 years in various roles"
        years = _extract_years_from_text(text)
        assert years == 7.0

    def test_extract_years_from_text_range(self):
        text = "Senior Developer (2018–2024)"
        years = _extract_years_from_text(text)
        assert years == 6

    def test_extract_years_from_text_empty(self):
        years = _extract_years_from_text("")
        assert years == 0.0

    def test_education_score_phd(self):
        score = _education_score("PhD")
        assert score == 15

    def test_education_score_master(self):
        score = _education_score("Master")
        assert score == 12

    def test_education_score_bachelor(self):
        score = _education_score("Bachelor")
        assert score == 8

    def test_education_score_other(self):
        score = _education_score("Other")
        assert score == 4

    def test_skills_score_few(self):
        score = _skills_score(["python", "aws"])
        assert score > 5

    def test_skills_score_many(self):
        score = _skills_score(["python", "aws", "docker", "k8s", "sql", "terraform"])
        assert score > 10

    def test_calculate_scores_basic(self):
        profile = {
            "experience_text": "Senior Developer (2018–2024)",
            "education_level": "Master",
            "skills": ["python", "aws", "docker"],
            "senior_roles": ["senior"],
            "summary": "Strategic leader with 6 years experience"
        }
        scores = calculate_scores(profile)
        assert scores["seniority_score"] > 0
        assert scores["seniority_score"] <= 100
        assert "min" in scores["salary_estimate"]
        assert "max" in scores["salary_estimate"]
        assert scores["salary_estimate"]["min"] > 0
        assert scores["salary_estimate"]["max"] > scores["salary_estimate"]["min"]

    def test_calculate_scores_junior(self):
        profile = {
            "experience_text": "Developer (2023–2024)",
            "education_level": "Other",
            "skills": ["python"],
            "senior_roles": [],
            "summary": "Junior developer learning"
        }
        scores = calculate_scores(profile)
        assert 0 <= scores["seniority_score"] <= 100

    def test_estimate_salary_with_cloud_skills(self):
        profile = {
            "skills": ["python", "aws", "cloud", "devops"],
            "senior_roles": []
        }
        salary = estimate_salary(50, profile)
        assert salary["min"] > 0
        assert salary["max"] > salary["min"]


class TestLLM:
    def test_fallback_explanation_strong_candidate(self):
        profile = {
            "skills": ["python", "aws", "docker", "leadership"],
            "senior_roles": ["senior", "lead"]
        }
        scores = {
            "experience_score": 25,
            "skills_score": 25,
            "education_score": 12,
            "role_score": 12,
            "potential_score": 10
        }
        salary = {"min": 100000, "max": 140000}
        explanation = _fallback_explanation(profile, scores, salary)
        assert "silné praktické zkušenosti" in explanation.lower()
        assert "100000" in explanation
        assert "140000" in explanation

    def test_fallback_explanation_junior_candidate(self):
        profile = {
            "skills": ["python"],
            "senior_roles": []
        }
        scores = {
            "experience_score": 5,
            "skills_score": 5,
            "education_score": 4,
            "role_score": 5,
            "potential_score": 5
        }
        salary = {"min": 40000, "max": 50000}
        explanation = _fallback_explanation(profile, scores, salary)
        assert len(explanation) > 0


class TestPipeline:
    @patch('cv_analyzer.pipeline.extract_text_from_file')
    def test_analyze_cv_mock(self, mock_extract):
        mock_extract.return_value = """
        John Developer
        Experienced Python developer with 5 years of AWS experience.
        
        Experience
        Senior Backend Developer at TechCorp (2019–2024)
        
        Skills
        Python, AWS, Docker, Kubernetes, PostgreSQL, CI/CD
        
        Education
        Bachelor of Science in Computer Science
        """
        result = analyze_cv("fake_cv.docx")
        assert "seniority_score" in result
        assert "salary_estimate" in result
        assert "explanation" in result
        assert result["seniority_score"] > 0
        assert result["seniority_score"] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
