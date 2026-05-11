# cv_analyzer
AI pipeline for analyzing CVs to estimate seniority and salary.

## Installation

1. Clone the repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running

### Command Line Interface
Run the CLI tool with a CV file:
```
python app.py path/to/cv.pdf
```
Or for JSON output:
```
python app.py path/to/cv.pdf --json
```

### Web Application
Run the Streamlit web app:
```
streamlit run streamlit_app.py
```
Then open the provided URL in your browser to upload CVs.

## Testing

Run the tests using pytest:
```
pytest tests/
```
