import argparse
import random
import os
from pathlib import Path
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

FIRST_NAMES = ["Jan", "Petr", "Pavel", "Tomáš", "Martin", "Jakub", "Lukáš", "David", "Michal", "Filip",
               "Anna", "Marie", "Eva", "Petra", "Jana", "Lucie", "Kateřina", "Lenka", "Martina", "Veronika"]
LAST_NAMES = ["Novák", "Svoboda", "Novotný", "Dvořák", "Černý", "Procházka", "Kučera", "Veselý", "Horák", "Němec",
              "Marek", "Pokorný", "Pospíšil", "Hájek", "Král", "Jelínek", "Růžička", "Beneš", "Fiala", "Sedláček"]

SKILLS = ["Python", "Java", "JavaScript", "React", "Angular", "Node.js", "AWS", "Azure", "GCP", "Docker",
          "Kubernetes", "SQL", "NoSQL", "PostgreSQL", "MongoDB", "Terraform", "CI/CD", "Machine Learning",
          "Data Engineering", "DevOps", "Cloud Architecture", "Microservices", "REST APIs", "GraphQL",
          "Agile", "Scrum", "Leadership", "Team Management"]

ROLES = [
    ("Junior Developer", 1, 2),
    ("Software Developer", 2, 4),
    ("Senior Developer", 4, 7),
    ("Lead Developer", 6, 10),
    ("Software Architect", 8, 12),
    ("Engineering Manager", 7, 15),
    ("Principal Engineer", 10, 15)
]

COMPANIES = ["TechCorp", "DataSystems", "CloudWorks", "InnoSoft", "DevHub", "CodeFactory", "ByteLabs",
             "AgileWorks", "SmartSolutions", "DigitalForge", "WebMasters", "AppBuilders"]

EDUCATION = [
    "Bachelor of Science in Computer Science",
    "Master of Science in Software Engineering",
    "Bachelor of Engineering in Information Technology",
    "Master of Science in Computer Science",
    "Bachelor of Science in Information Systems",
    "PhD in Computer Science"
]


def generate_cv_data():
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    
    num_roles = random.randint(2, 5)
    experience = []
    current_year = 2024
    years_exp = 0
    
    for i in range(num_roles):
        role_info = random.choice(ROLES)
        role_name = role_info[0]
        duration = random.randint(role_info[1], role_info[2])
        start_year = current_year - duration
        experience.append({
            "role": role_name,
            "company": random.choice(COMPANIES),
            "start": start_year,
            "end": current_year,
            "duration": duration
        })
        years_exp += duration
        current_year = start_year
        if current_year < 2010:
            break
    
    num_skills = random.randint(5, 12)
    skills = random.sample(SKILLS, num_skills)
    
    education = random.choice(EDUCATION)
    
    summary_templates = [
        f"Experienced software engineer with {years_exp} years of expertise in building scalable applications.",
        f"Strategic thinker with {years_exp} years of leadership in software development and team mentoring.",
        f"Results-driven developer with {years_exp} years of experience in cloud architecture and DevOps.",
        f"Innovation-focused engineer with {years_exp} years delivering high-impact solutions.",
    ]
    summary = random.choice(summary_templates)
    
    return {
        "name": name,
        "summary": summary,
        "experience": experience,
        "skills": skills,
        "education": education
    }


def generate_docx(cv_data, output_path):
    doc = Document()
    
    doc.add_heading(cv_data["name"], 0)
    
    doc.add_heading("Summary", level=2)
    doc.add_paragraph(cv_data["summary"])
    
    doc.add_heading("Experience", level=2)
    for exp in cv_data["experience"]:
        doc.add_paragraph(
            f"{exp['role']} at {exp['company']} ({exp['start']}–{exp['end']})",
            style='List Bullet'
        )
    
    doc.add_heading("Skills", level=2)
    doc.add_paragraph(", ".join(cv_data["skills"]))
    
    doc.add_heading("Education", level=2)
    doc.add_paragraph(cv_data["education"])
    
    doc.save(output_path)


def generate_pdf(cv_data, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    y = height - inch
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(inch, y, cv_data["name"])
    y -= 0.5 * inch
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Summary")
    y -= 0.3 * inch
    
    c.setFont("Helvetica", 11)
    c.drawString(inch, y, cv_data["summary"])
    y -= 0.5 * inch
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Experience")
    y -= 0.3 * inch
    
    c.setFont("Helvetica", 11)
    for exp in cv_data["experience"]:
        text = f"• {exp['role']} at {exp['company']} ({exp['start']}–{exp['end']})"
        c.drawString(inch, y, text)
        y -= 0.25 * inch
        if y < inch:
            break
    
    y -= 0.2 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Skills")
    y -= 0.3 * inch
    
    c.setFont("Helvetica", 11)
    skills_text = ", ".join(cv_data["skills"])
    c.drawString(inch, y, skills_text[:80])
    if len(skills_text) > 80:
        y -= 0.25 * inch
        c.drawString(inch, y, skills_text[80:])
    
    y -= 0.5 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Education")
    y -= 0.3 * inch
    
    c.setFont("Helvetica", 11)
    c.drawString(inch, y, cv_data["education"])
    
    c.save()


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic CVs for testing")
    parser.add_argument("-n", "--number", type=int, default=20, help="Number of CVs to generate (default: 20)")
    parser.add_argument("-o", "--output", type=str, default="sample", help="Output directory (default: data/sample)")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {args.number} synthetic CVs in {output_dir}...")
    
    for i in range(args.number):
        cv_data = generate_cv_data()
        
        if i % 2 == 0:
            output_path = output_dir / f"cv_{i+1:03d}.docx"
            generate_docx(cv_data, str(output_path))
        else:
            output_path = output_dir / f"cv_{i+1:03d}.pdf"
            generate_pdf(cv_data, str(output_path))
        
        print(f"Created: {output_path}")
    
    print(f"\nSuccessfully generated {args.number} CVs!")


if __name__ == "__main__":
    main()
