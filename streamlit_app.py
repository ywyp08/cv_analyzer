import streamlit as st
from pipeline.pipeline import analyze_cv

st.set_page_config(page_title="CV Seniority Estimator", layout="wide")

st.title("AI CV Seniority & Salary Estimator")
st.write("Nahraj CV v PDF nebo DOCX, systém vypočítá senioritu, odhad mzdy a doporučení.")

uploaded_file = st.file_uploader("Vyberte CV soubor", type=["pdf", "docx"])
if uploaded_file is not None:
    import os
    file_extension = os.path.splitext(uploaded_file.name)[1]
    temp_file_path = f"data/uploads/uploaded_cv{file_extension}"
    os.makedirs("data/uploads", exist_ok=True)
    with open(temp_file_path, "wb") as tmp:
        tmp.write(uploaded_file.read())

    with st.spinner("Analyzuji CV..."):
        result = analyze_cv(temp_file_path)

    st.metric("Seniority Score", f"{result['seniority_score']}/100")
    st.metric("Salary range", f"{result['salary_estimate']['min']}–{result['salary_estimate']['max']} CZK / měsíc")

    st.subheader("Shrnutí profilu")
    for item in result['summary_insights']:
        st.write(f"- {item}")

    st.subheader("Vysvětlení a doporučení")
    st.write(result['explanation'])
