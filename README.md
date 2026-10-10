# ZECPATH AI Hiring Platform

> An AI-powered recruitment platform focused on automating key stages of the hiring lifecycle — from job-description and resume processing to candidate screening, interviews, and evaluation.

## Overview

**ZECPATH AI** is a recruitment technology project designed to help automate and structure the hiring workflow.

The platform is organized into independent modules for:

- Resume parsing and text extraction
- Job Description (JD) parsing
- ATS and candidate matching
- AI-based screening
- HR and technical interviews
- Candidate scoring and evaluation
- Compliance and supporting utilities

The project is being developed as a modular Python-based platform so that individual components can be tested and improved independently.

---

## Project Status

### Currently implemented

- Resume PDF text extraction and cleaning
- DOCX/PDF-related resume parsing components
- Job Description PDF parsing
- JD cleaning and normalization
- JD section extraction
- Role extraction
- Skill extraction
- Experience requirement extraction
- Education requirement extraction
- Structured JSON generation for parsed JDs
- Automated processing of multiple JD PDFs
- Test and utility structure for continued development

### In development

- ATS matching and candidate ranking
- AI voice screening
- HR and technical interview workflows
- Candidate evaluation and scoring
- Additional recruitment automation features

> Features listed as "in development" are part of the platform architecture but should not be considered production-ready unless their implementation and testing are complete.

---

## Architecture

The repository is organized into functional modules:

```
ZECPATH-AI/
│
├── ats_engine/          # ATS and candidate matching components
├── compliance/          # Compliance-related components
├── config/              # Configuration files
├── data/                # Input data and generated outputs
├── db/                  # Database-related components
├── docs/                # Project documentation
├── interview_ai/        # AI interview components
├── parsers/             # Resume and JD parsing engines
├── reports/             # Reports and generated analysis
├── scoring/             # Candidate scoring components
├── screening_ai/        # AI screening components
├── tests/               # Automated tests
├── utils/               # Logging and helper utilities
│
├── main.py
├── main_resume.py
├── main_job_parser.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Core Modules

## 1. Resume Parser

The resume-processing pipeline extracts useful text from candidate resumes and prepares it for downstream recruitment processing.

### Current capabilities

- PDF resume text extraction
- DOCX resume parsing components
- Text cleaning
- Cleaned resume output
- Processing of resume files from the project data directory

### Input

```
data/resumes/
```

### Run

```bash
python main_resume.py
```

---

## 2. Job Description Parser

The JD Parser converts Job Description PDFs into structured JSON data that can be consumed by downstream recruitment and matching components.

### Extraction pipeline

```
PDF
 ↓
PDF Text Extraction
 ↓
Cleaning
 ↓
Normalization
 ↓
Section Detection
 ↓
Role Extraction
 ↓
Skill Extraction
 ↓
Experience Extraction
 ↓
Education Extraction
 ↓
Structured JSON
```

### Current capabilities

- PDF Job Description reading
- JD cleaning
- JD normalization
- Section detection
- Role extraction
- Required-skill extraction
- Experience requirement extraction
- Education extraction
- Structured JSON generation
- Batch processing of multiple JD PDFs

### Input

```
data/job_descriptions/
```

### Output

```
data/parsed_jd/
```

### Run

```bash
python main_job_parser.py
```

The script scans the Job Description directory for PDF files and creates a corresponding JSON file for each JD.

### Example output

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

The `ats_engine/` module is intended to support automated resume-to-JD matching and candidate ranking.

Planned/ongoing areas include:

- Skill matching
- Experience matching
- Education matching
- Resume/JD compatibility scoring
- Candidate ranking

---

## 4. Screening AI

The `screening_ai/` module contains components for AI-assisted candidate screening.

Development areas include:

- Voice-based interaction
- Transcript processing
- Candidate response analysis
- Communication assessment
- Screening evaluation

---

## 5. Interview AI

The `interview_ai/` module is intended to support AI-assisted recruitment interviews.

Development areas include:

- HR interviews
- Technical interviews
- Question generation
- Candidate response evaluation
- Interview reports

---

## 6. Scoring

The `scoring/` module is intended to combine recruitment signals into structured candidate evaluation.

Potential scoring dimensions include:

- Technical performance
- Experience
- Skills
- Communication
- Interview performance
- Overall candidate recommendation

---

## 7. Compliance

The `compliance/` module contains components related to responsible recruitment and compliance workflows.

---

# Data Flow

A simplified recruitment workflow is:

```
Candidate Resume ───────┐
                        │
                        ▼
                  Resume Parser
                        │
                        ▼
                 Candidate Data
                        │
                        ├──────────────┐
                        │              │
                        ▼              ▼
                   ATS Engine     Interview AI
                        │              │
                        └──────┬───────┘
                               ▼
                         Scoring Engine
                               │
                               ▼
                     Candidate Evaluation
```

For job descriptions:

```
Job Description PDF
        │
        ▼
    JD Parser
        │
        ├── Role
        ├── Skills
        ├── Experience
        └── Education
        │
        ▼
   Structured JSON
```

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/asif-chittengadan/zecpath-ai.git
cd zecpath-ai
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

Some dependencies use external model packages and system resources. If an installation issue occurs, check the package-specific error before changing the pinned versions.

---

# Running the Project

## Resume processing

Place a PDF resume in:

```
data/resumes/
```

Then run:

```bash
python main_resume.py
```

## Job Description parsing

Place one or more JD PDFs in:

```
data/job_descriptions/
```

Then run:

```bash
python main_job_parser.py
```

Parsed JSON files will be written to:

```
data/parsed_jd/
```

## Main entry point

```bash
python main.py
```

The main entry point currently demonstrates the resume text-extraction workflow.

---

# Testing

The repository contains a `tests/` directory for automated testing.

Run:

```bash
pytest
```

---

# Technology Stack

### Programming

- Python 3

### Document processing

- PyMuPDF
- pdfplumber
- python-docx

### NLP / AI

- spaCy
- Transformers
- Sentence Transformers
- PyTorch
- Faster-Whisper

### Data and machine learning

- NumPy
- Pandas
- Scikit-learn
- RapidFuzz

### API / backend

- FastAPI
- Uvicorn

### Testing

- PyTest

### Data formats

- JSON
- PDF
- DOCX

---

# Repository Goals

ZECPATH AI is being developed toward an end-to-end AI-assisted recruitment workflow:

```
Job Description
      ↓
JD Parsing
      ↓
Resume Parsing
      ↓
ATS Screening
      ↓
AI Screening
      ↓
HR / Technical Interview
      ↓
Candidate Scoring
      ↓
Recruiter Decision
```

The project is intended to make recruitment workflows more structured, explainable, and easier to automate while keeping individual components modular and testable.

---

# Documentation

Project documentation and supporting materials are available in:

```
docs/
```

Additional generated reports and analysis are maintained in:

```
reports/
```

---

# Author

**Asif C**

ZECPATH AI Hiring Platform

---

## License

License information will be added when the project license is finalized.
