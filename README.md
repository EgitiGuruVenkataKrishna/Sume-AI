# ⚡ Sume AI — Resume ATS Analyzer

**Beat the ATS. Land the Interview.**

Sume AI analyzes your resume against job descriptions, reveals exactly why ATS filters reject you, and gives actionable fixes to land more interviews.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square)
![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.1-orange?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square)

---

## What It Does

1. **Upload** your resume (PDF)
2. **Paste** the job description you're targeting
3. **Get** an ATS compatibility score (0–100) with:
   - Missing keywords the ATS expects
   - Specific strengths in your resume
   - Actionable improvements (exact before → after fixes)
   - ATS formatting issues to fix
   - Section-by-section scoring

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | FastAPI | Async, auto-docs, Pydantic native |
| AI/LLM | Groq (Llama 3.1-8B) | 10x faster than OpenAI, free tier |
| PDF Parsing | PyPDF2 | Lightweight, reliable text extraction |
| Validation | Pydantic | Structured JSON output from LLM |
| Frontend | Vanilla HTML/CSS/JS | No build step, fast load, custom UI |
| Deployment | Docker + Render | Consistent environments, auto deploy |

---

## Quick Start

### Prerequisites
- Python 3.10+
- A Groq API key (free at [console.groq.com](https://console.groq.com))

### Setup

```bash
# Clone the repo
git clone https://github.com/EgitiGuruVenkataKrishna/Sume-AI.git
cd Sume-AI

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the server
python main.py
```

Open **http://localhost:8000** in your browser.

### Docker

```bash
docker build -t sume-ai .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key_here sume-ai
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/analyze-resume` | Analyze resume vs job description |
| `GET` | `/docs` | Swagger UI (auto-generated) |

### Example Request

```bash
curl -X POST http://localhost:8000/analyze-resume \
  -F "resume=@my_resume.pdf" \
  -F "job_description=Looking for a Python developer with FastAPI and Docker experience"
```

---

## Project Structure

```
Sume-AI/
├── main.py              # FastAPI backend
├── requirements.txt     # Python dependencies
├── .env.example         # Env var template
├── .gitignore           # Git ignore rules
├── Dockerfile           # Container config
├── README.md            # This file
├── project_details.md   # Full project spec
└── static/
    ├── index.html       # Frontend SPA
    └── styles.css       # Custom design system
```

---

## Deploy to Render

1. Push to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your repo
4. Set Environment: **Docker**, Branch: **main**
5. Add env var: `GROQ_API_KEY` = your key
6. Deploy!

---

## Author

**Egiti Guru Venkata Krishna**  
VIT-AP | CSE - AI & ML  
