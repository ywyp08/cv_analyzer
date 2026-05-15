import os
import uuid
from pathlib import Path

import streamlit as st
from pipeline.pipeline import analyze_cv

st.set_page_config(page_title="CV Seniority Estimator", layout="wide")

st.title("AI CV Seniority & Salary Estimator")
st.write("Nahraj CV v PDF nebo DOCX, systém vypočítá senioritu, odhad mzdy a LLM vysvětlení.")

uploaded_file = st.file_uploader("Vyberte CV soubor", type=["pdf", "docx"])
if uploaded_file is not None:
    file_extension = os.path.splitext(uploaded_file.name)[1]
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = upload_dir / f"uploaded_cv_{uuid.uuid4().hex}{file_extension}"
    with open(temp_file_path, "wb") as tmp:
        tmp.write(uploaded_file.read())

    with st.spinner("Analyzuji CV..."):
        result = analyze_cv(str(temp_file_path))

    st.subheader("Výsledky")
    st.write(f"**Name:** {result.get('name', 'Unknown')}")
    st.write(f"**Seniority Score:** {result['seniority_score']}/100")
    st.write(f"**Salary estimate:** {result['salary_estimate']['min']}–{result['salary_estimate']['max']} CZK / měsíc")

    st.subheader("LLM Explanation")
    st.write(result['explanation'])
