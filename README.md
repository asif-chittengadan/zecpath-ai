# ZECPATH AI

ZECPATH AI is a modular Python project that prototypes AI-assisted recruitment tasks: resume and job-description processing, candidate-to-job scoring, screening and interview workflows, decision support, and compliance helpers.

The repository contains callable modules and local demonstration scripts. It is not a deployed hiring service, and the sample simulations do not prove production accuracy, fairness, security, or scale.

## Current project status

As of Day 68, the local synthetic demonstration and automated suite have been validated. The final check completed **679 tests and 8 subtests**. A four-profile Day 63 run completed in about 1.02 seconds after model initialization, with score bounds and weighted totals checked. See the [Day 68 validation report](output/pdf/Day_68_Final_Validation_and_Bug_Fix_Report.pdf).

The integrated demonstrations use fictional profiles and supplied response or rubric fixtures. Resume parsing is not connected end to end to ATS matching. The repository has no implemented HTTP API or connected hiring UI. `website/index.html` is a static page and is separate from the company's official website.

## Project structure

- `parsers/` - PDF/DOCX text readers, resume parsing components, and job-description parsing.
- `scoring/` - resume/JD matching, ATS scoring, screening score aggregation, unified scores, eligibility, recommendations, explainability, and fairness helpers.
- `screening_ai/` - screening conversation state, response analysis, and speech/transcript utilities.
- `interview_ai/` - HR, technical, behavioral, and machine-test components.
- `compliance/` - consent, access-policy checks, audit-event writing, and retention decisions. These helpers are not enforced across every application path.
- `config/` - scoring, interview, eligibility, access, and retention rules.
- `data/day63_demo/` - fictional demo jobs, candidate profiles, and assessment fixtures.
- `tests/` - pytest coverage for the project modules and edge cases.
- `reports/` - local JSON/Markdown analysis outputs.
- `docs/` - technical references, governance materials, reports, and the Day 69 package.
- `output/` - presentation and PDF deliverables.
- `main_day56_full_system_simulation.py` and `main_day63_end_to_end_simulation.py` - local synthetic pipeline demonstrations.

The `ats_engine/` directory is a legacy namespace; active ATS matching and ranking code is primarily under `scoring/`. The `db/` folder contains a schema draft, not a live database integration.

## Setup

Python 3.13 is the validated development runtime for this repository. From a PowerShell terminal:

```powershell
git clone https://github.com/asif-chittengadan/zecpath-ai.git
cd zecpath-ai
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For macOS or Linux:

```bash
git clone https://github.com/asif-chittengadan/zecpath-ai.git
cd zecpath-ai
python3.13 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The semantic matching component uses the Sentence Transformers model `all-MiniLM-L6-v2`. Its first use may download model files from Hugging Face, so allow network access and enough disk space; later runs can use the local model cache. Some speech and document dependencies may also require platform-specific system libraries.

## Run the project

Run commands from the repository root with the virtual environment active.

### Resume text extraction

`main.py` uses the configured `data/resumes/mycv.pdf` path:

```powershell
python main.py
```

`main_resume.py` processes a PDF from `data/resumes/`. These are parser demonstrations; their output is not automatically sent to ATS scoring.

### Parse job descriptions

Place job-description PDFs in `data/job_descriptions/`, then run:

```powershell
python main_job_parser.py
```

The script writes parsed JSON files under `data/parsed_jd/`.

### Run synthetic hiring demonstrations

Day 56 exercises a selected path through ATS, screening, HR, technical scoring, unified scoring, and a final decision:

```powershell
python main_day56_full_system_simulation.py
```

Day 63 runs four fictional candidates through eight demo stages using the separate dataset under `data/day63_demo/`:

```powershell
python main_day63_end_to_end_simulation.py
```

The Day 56 and Day 63 scripts write local reports under `reports/` and may replace the corresponding prior report. Their outputs are demonstration results, not real hiring decisions.

### Run tests and the warm-scoring benchmark

```powershell
python -m pytest -q
python -m tests.day18_warm_benchmark
```

The benchmark loads the semantic model and scores JSON resumes under `data/labeled_resumes/`. Results depend on model-cache state, hardware, and input size.

## Responsible use and data handling

- Use fictional or explicitly authorized data for demonstrations. The repository may contain resume files and other candidate-related records; review them before sharing, uploading, or creating a public archive.
- The Day 63 fixtures are explicitly synthetic and intended for local demonstrations.
- Machine-test results in the current end-to-end fixture are supplied rubric values; submitted code is not run in a sandbox.
- Interview and screening scores are decision-support signals. A human must review evidence and make any real employment decision.
- Consent, access-control, audit, and retention modules provide reusable controls, but their presence does not mean every path is protected or that retention actions execute automatically.

## Documentation and portfolio

Start at [docs/README.md](docs/README.md) for a guide to the existing documentation and reports. The Day 69 handoff includes:

- [Internship portfolio source](docs/day69/INTERNSHIP_PORTFOLIO.md)
- [AI roadmap source](docs/day69/AI_ROADMAP.md)
- [Day 69 package index](docs/day69/README.md)
- `output/pdf/Day_69_Internship_Portfolio.pdf`
- `output/pdf/Day_69_AI_Roadmap.pdf`

## Author

Asif C

License terms have not been finalized in this repository.
