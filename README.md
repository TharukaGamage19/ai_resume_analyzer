# ResumeIQ — AI Resume Analyzer & Job Coach

An AI-powered resume analyzer that scores ATS compatibility, identifies skill gaps, generates tailored interview Q&As, rewrites bullet points, and provides a full career coaching report — all in under 15 seconds.

Built with **LLaMA 3.3 70B via Groq**, **Streamlit**, and **FastAPI**.

---

## Features

- **ATS Score** — rates how well your resume passes applicant tracking systems (0–100)
- **Skill Gap Analysis** — identifies missing skills with learning suggestions
- **Interview Preparation** — generates 5 STAR-format Q&As tailored to the job description
- **Bullet Rewrites** — rewrites 3 weak bullet points with before/after/why
- **Coaching Report** — full Markdown report with a LinkedIn About draft
- **Career Coach Chatbot** — context-aware chatbot that knows your results and answers career questions

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | LLaMA 3.3 70B via Groq API |
| Frontend | Streamlit |
| Backend | FastAPI |
| PDF Extraction | pdfplumber |
| DOCX Extraction | python-docx |
| Testing | pytest + pytest-cov |
| CI/CD | GitHub Actions |

---

## Project Structure

```
ai-resume-analyzer/
├── backend/
│   ├── analyzer.py       # All 4 LLM methods + JSON parsing
│   └── main.py           # FastAPI /analyse and /health endpoints
├── frontend/
│   ├── main.py           # Streamlit UI
│   ├── utils.py          # PDF, DOCX, TXT text extraction
│   └── client.py         # HTTP client calling FastAPI
├── tests/
│   └── test_analyzer.py  # 18 unit tests, 86% coverage
├── .github/
│   └── workflows/
│       └── ci.yml        # CI pipeline
├── .coveragerc           # Coverage config
├── requirements.txt
└── .env.example
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Groq API key — get one free at [console.groq.com](https://console.groq.com)

### Installation

```bash
# Clone the repo
git clone https://github.com/TharukaGamage19/ai_resume_analyzer.git
cd ai_resume_analyzer

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running the App

Open two terminals:

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
streamlit run main.py
```

Open http://localhost:8501 in your browser.

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/test_analyzer.py -v --cov=backend --cov-config=.coveragerc --cov-report=term-missing
```

Current coverage: **86%** on analyzer.py

---

## CI/CD Pipeline

Every push to master triggers:

| Job | What it does |
|---|---|
| Lint & Test | flake8 lint + pytest with 80% coverage gate |
| Security | Bandit static analysis on all Python files |
| Build Check | Verifies all imports work correctly |

---

Tharuka Gamage
---

## License

MIT
