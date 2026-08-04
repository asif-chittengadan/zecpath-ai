# Zecpath AI Hiring Platform

## Overview

Zecpath AI is an AI-powered recruitment platform designed to automate the end-to-end hiring process. The platform extracts information from resumes and job descriptions, performs ATS screening, conducts AI-based interviews, scores candidates, and assists recruiters in making hiring decisions.

---

# Project Structure

```
ZECPATH-AI/
│
├── data/
│   ├── resumes/
│   ├── cleaned/
│   ├── extracted/
│   ├── job_descriptions/
│   ├── parsed_jd/
│   ├── roles.json
│   ├── skills.json
│   ├── education.json
│   └── synonyms.json
│
├── parsers/
│   ├── pdf_reader.py
│   ├── docx_reader.py
│   ├── resume_engine.py
│   ├── resume_parser.py
│   ├── text_cleaner.py
│   ├── jd_cleaner.py
│   ├── jd_normalizer.py
│   ├── section_extractor.py
│   ├── role_extractor.py
│   ├── skill_extractor.py
│   ├── experience_extractor.py
│   ├── education_extractor.py
│   ├── requirement_extractor.py
│   ├── jd_builder.py
│   └── job_parser.py
│
├── ats_engine/
├── screening_ai/
├── interview_ai/
├── scoring/
├── utils/
├── tests/
├── logs/
│
├── main.py
├── main_resume.py
├── main_job_parser.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Modules

## 1. Resume Parser

Extracts text from PDF and DOCX resumes.

### Features

- PDF Resume Reader
- DOCX Resume Reader
- Resume Text Extraction
- Text Cleaning
- Clean Resume Output Generation
- Supports multiple resume files

### Output

Cleaned resume text is stored inside:

```
data/cleaned/
```

---

## 2. Job Description Parser

Converts Job Description PDFs into structured AI-readable JSON.

### Features

- PDF Job Description Reader
- JD Cleaning
- JD Normalization
- Section Detection
- Role Extraction
- Skill Extraction
- Experience Requirement Extraction
- Education Requirement Extraction
- JSON Builder
- Automatically processes every JD inside the folder

### Input

```
data/job_descriptions/
```

Supported formats:

- PDF

### Output

Structured JSON files are generated inside:

```
data/parsed_jd/
```

Example:

```json
{
    "role": "Software Developer",
    "skills": [
        "C",
        "C++",
        "JavaScript"
    ],
    "experience": {
        "minimum": 0,
        "maximum": 0,
        "text": "Freshers"
    },
    "education": [
        "B.Tech",
        "Computer Science",
        "Artificial Intelligence"
    ]
}
```

---

## 3. ATS Engine

Calculates ATS compatibility between resumes and job descriptions.

### Planned Features

- Resume Scoring
- Skill Matching
- Experience Matching
- Education Matching
- Candidate Ranking

---

## 4. Screening AI

Conducts AI-powered voice screening interviews.

### Planned Features

- Voice Interaction
- Candidate Communication Analysis
- Behaviour Assessment

---

## 5. Interview AI

Conducts HR and Technical interviews.

### Planned Features

- HR Interview
- Technical Interview
- AI Evaluation

---

## 6. Scoring Engine

Generates candidate evaluation scores.

### Planned Features

- Technical Score
- HR Score
- Communication Score
- Final Recommendation

---

## Utilities

Contains helper modules including:

- Logger
- Configurations
- Helper Functions

---

## Tests

Contains automated test cases for:

- Resume Parser
- Job Description Parser
- ATS Engine
- Scoring

Run tests:

```bash
pytest
```

---

# Installation

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Project

## Resume Parser

```bash
python main_resume.py
```

---

## Job Description Parser

```bash
python main_job_parser.py
```

---

## Main Project

```bash
python main.py
```

---

# Technologies Used

- Python 3
- pdfplumber
- PyMuPDF
- python-docx
- Regular Expressions (Regex)
- JSON
- PyTest

---

# Deliverables Completed

- Resume Text Extraction Engine
- Resume Cleaning Engine
- Job Description Parser Module
- Structured JSON Output
- Automated Test Cases

---

# Author

**Asif C**

**Data Science Engineer Intern**

**Zecpath AI Hiring Platform**