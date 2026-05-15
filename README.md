# cv_analyzer
AI pipeline for analyzing CVs to estimate seniority, salary, and give explanation.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```

## How to run

### Command Line Interface
```
python app.py path/to/cv.pdf
```

### Web Application
```
streamlit run streamlit_app.py
```

## Pipeline

The CV analysis pipeline consists of three main stages:

1. **Processing** (`pipeline/processing/`)
   - `extract.py`: Extracts text from PDF and DOCX files
   - `structure.py`: Parses CV sections (experience, skills, education, etc.) and structures the data

2. **Scoring** (`pipeline/scoring/`)
   - `seniority.py`: Calculates seniority score based on experience and education
   - `salary.py`: Estimates salary range based on seniority score and skills

3. **Explaining** (`pipeline/explaining/`)
   - `explain.py`: Generates human-readable explanations using LLM or fallback heuristics

The main `pipeline.py` orchestrates these stages to produce a comprehensive CV analysis.

## Data

The `data/` directory contains:

- **`sample/`**: Sample CV files for testing (DOCX and PDF formats). Use `generate_synthetic_cvs.py` to populate this directory with synthetic CVs.
- **`uploads/`**: Temporary storage for CVs uploaded through the Streamlit web interface.

