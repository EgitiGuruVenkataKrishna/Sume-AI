<h1 align="center">
  ⚡ Sume AI — Resume ATS Analyzer
</h1>

<p align="center">
  <strong>Beat the ATS. Land the Interview.</strong><br/>
  Upload your resume, paste any job description, and get an AI-powered ATS compatibility score with exact fixes — in seconds.
</p>

<p align="center">
  <a href="https://sume-ai.vercel.app" target="_blank">
    <img src="https://img.shields.io/badge/🌐 Live Demo-sume--ai.vercel.app-5C6BC0?style=for-the-badge" alt="Live Demo"/>
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Groq-Llama%203.1--8B-FF6B35?style=flat-square"/>
  <img src="https://img.shields.io/badge/Vercel-Deployed-000000?style=flat-square&logo=vercel&logoColor=white"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/PWA-Enabled-5A0FC8?style=flat-square&logo=pwa&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square"/>
</p>

---

## 📌 Table of Contents

- [Why Sume AI?](#-why-sume-ai)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Local Setup](#-local-setup)
- [Docker](#-docker)
- [Deployment](#-deployment-vercel)
- [Environment Variables](#-environment-variables)
- [Security](#-security)
- [Author](#-author)

---

## 🎯 Why Sume AI?

> **75% of resumes never reach a human recruiter** — they're filtered out by Applicant Tracking Systems (ATS) before anyone reads them.

Sume AI solves this by acting as your personal ATS simulator. It reads your resume exactly the way a system like Taleo, Workday, or Greenhouse would, then tells you — with precision — what to fix.

---

## ✨ Features

### 🔍 ATS Resume Analyzer
- **ATS Compatibility Score** (0–100) weighted across keyword match, experience relevance, skills alignment, and formatting
- **Missing Keywords** — identifies critical JD keywords absent from your resume, with context on why each matters
- **Section-by-Section Scoring** — individual scores for Experience, Skills, Education, and Formatting
- **ATS Section Simulation** — simulates how a real ATS parses your resume sections (Contact Info, Summary, Experience, Skills, Education, Certifications, Projects), with `found` / `missing` / `warning` statuses
- **Before → After Rewrites** — 3–5 exact bullet-point rewrites with the original text, improved version, and the reason it improves ATS compatibility
- **Strengths** — specific, evidence-backed strengths detected in the resume
- **Actionable Improvements** — concrete, numbered fixes (not generic advice)
- **ATS Formatting Issues** — flags non-standard headers, tables, columns, and other ATS pitfalls

### 📝 Cover Letter Generator
- Generates a tailored, professional cover letter (≤350 words) from your resume + job description
- Grounded strictly in your resume — no hallucinated achievements
- Professional but personable tone with a strong opening hook and clear call to action

### 🛡️ Production-Grade Infrastructure
- **Rate limiting** — configurable per-IP (default: 10 analyses/hour) via `slowapi`
- **Security headers** — `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy` on every response
- **CORS** — configurable allowed origins
- **Structured JSON logging** — human-readable in dev, structured JSON in production
- **Input validation** — file type (PDF / DOCX), file size (max 5 MB), JD length (50–5000 chars)

### 📱 Progressive Web App (PWA)
- Installable on Android and desktop directly from the browser
- Service Worker for offline support
- Custom dark-themed manifest with app icons

---

## 🛠️ Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend** | FastAPI 0.109+ | Async-native, auto Swagger UI, Pydantic integration |
| **LLM** | Groq `llama-3.1-8b-instant` | Sub-second inference — ~10× faster than OpenAI |
| **PDF Parsing** | pypdf | Lightweight, reliable text extraction |
| **DOCX Parsing** | python-docx | Handles paragraphs and table-cell layouts in resumes |
| **Validation** | Pydantic v2 | Guarantees structured, typed JSON output from the LLM |
| **Rate Limiting** | slowapi | Per-IP rate limiting with standard HTTP 429 responses |
| **Frontend** | Vanilla HTML / CSS / JS | Zero build step, fast load, full custom design system |
| **PWA** | Web App Manifest + Service Worker | Installable, offline-capable |
| **Deployment** | Vercel (Serverless) | Edge-deployed, auto HTTPS, zero-config |
| **Container** | Docker | Reproducible local and CI/CD environments |

---

## 📁 Project Structure

```
Sume-AI/
├── main.py                # FastAPI application (v3.0.0)
│                          #   ├─ /analyze-resume  (ATS analysis)
│                          #   ├─ /generate-cover-letter
│                          #   └─ /health
├── api/
│   └── index.py           # Vercel serverless entry point (imports main.app)
├── static/
│   ├── index.html         # Single-page frontend application
│   ├── styles.css         # Full custom design system (~38 KB)
│   ├── manifest.json      # PWA manifest
│   ├── sw.js              # Service Worker (offline support)
│   └── icons/
│       ├── icon-192.png   # PWA icon (192×192)
│       └── icon-512.png   # PWA icon (512×512)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container configuration
├── vercel.json            # Vercel routing config
├── .env.example           # Environment variable template
├── .gitignore
└── README.md
```

---

## 📡 API Reference

### `GET /health`
Health check endpoint.

```json
{ "status": "healthy", "service": "sume-ai", "version": "3.0.0" }
```

---

### `POST /analyze-resume`

Analyze a resume against a job description.

**Request** — `multipart/form-data`

| Field | Type | Required | Constraints |
|---|---|---|---|
| `resume` | File | ✅ | PDF or DOCX, max 5 MB |
| `job_description` | string | ✅ | 50–5000 characters |

**Response** — `200 OK`

```json
{
  "overall_score": 74,
  "summary": "Your resume shows strong Python skills but lacks several cloud-native keywords critical to this role...",
  "missing_keywords": [
    { "keyword": "Kubernetes", "importance": "Mentioned 6 times in JD — core infrastructure skill" }
  ],
  "strengths": [
    "Strong action verbs: Architected, Delivered, Led",
    "Quantified achievements: reduced latency by 40%"
  ],
  "improvements": [
    "Replace 'Responsible for deployments' → 'Managed CI/CD pipelines deploying 3 microservices to AWS EKS'"
  ],
  "ats_issues": [
    "Section header 'Work History' should be 'EXPERIENCE' for ATS compatibility"
  ],
  "section_scores": {
    "experience": 80,
    "skills": 65,
    "education": 90,
    "formatting": 70
  },
  "rewrites": [
    {
      "original": "Responsible for managing the backend API",
      "rewritten": "Engineered and maintained a FastAPI backend serving 50K+ daily requests with 99.9% uptime",
      "why": "Replaces passive language with a strong verb and quantified impact"
    }
  ],
  "ats_parsed_sections": [
    { "name": "Contact Info", "status": "found", "detail": "Name, email, and phone detected" },
    { "name": "Skills", "status": "warning", "detail": "Skills listed in paragraph form — use comma-separated list" }
  ],
  "confidence": 0.91
}
```

**Error Responses**

| Code | Meaning |
|---|---|
| `400` | Invalid file type, file too large, or JD too short/long |
| `429` | Rate limit exceeded |
| `500` | LLM or server error |

---

### `POST /generate-cover-letter`

Generate a tailored cover letter from a resume and job description.

**Request** — `multipart/form-data`

| Field | Type | Required | Constraints |
|---|---|---|---|
| `resume` | File | ✅ | PDF or DOCX, max 5 MB |
| `job_description` | string | ✅ | Full job description text |

**Response** — `200 OK`

```json
{
  "cover_letter": "Dear Hiring Manager,\n\nWith 3 years of backend engineering experience..."
}
```

---

### `GET /docs`

Auto-generated interactive Swagger UI — available in development at `http://localhost:8000/docs`.

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- A free Groq API key → [console.groq.com/keys](https://console.groq.com/keys)

### 1. Clone & Install

```bash
git clone https://github.com/EgitiGuruVenkataKrishna/Sume-AI.git
cd Sume-AI

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and fill in your Groq API key:

```env
GROQ_API_KEY=gsk_your_key_here
```

### 3. Run

```bash
python main.py
```

Open **[http://localhost:8000](http://localhost:8000)** in your browser.  
Swagger docs available at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## 🐳 Docker

```bash
# Build
docker build -t sume-ai .

# Run
docker run -p 8000:8000 -e GROQ_API_KEY=gsk_your_key_here sume-ai
```

The container uses `gunicorn` with 2 `UvicornWorker` processes for production-grade concurrency.

---

## ☁️ Deployment (Vercel)

The project is live at **[sume-ai.vercel.app](https://sume-ai.vercel.app)**.

All requests are routed via `vercel.json` → `api/index.py` → `main.app` (FastAPI).

### Deploy Your Own Fork

```bash
npm install -g vercel
vercel login
vercel --prod
```

Set the `GROQ_API_KEY` environment variable in your Vercel project dashboard under **Settings → Environment Variables**.

---

## 🔐 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ | — | Groq API key for LLM inference |
| `ENVIRONMENT` | ❌ | `development` | Set to `production` for JSON logging |
| `RATE_LIMIT` | ❌ | `10/hour` | slowapi rate limit string (e.g. `5/minute`) |
| `ALLOWED_ORIGINS` | ❌ | `*` | Comma-separated CORS origins |
| `PORT` | ❌ | `8000` | Server port (for local / Docker runs) |

Copy `.env.example` to `.env` and fill in your values. **Never commit `.env` to version control.**

---

## 🔒 Security

- **Security headers** on all HTTP responses (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`)
- **Rate limiting** at the IP level to prevent abuse
- **No resume data stored** — resumes are processed in-memory and immediately discarded
- **Input validation** on file type, file size, and JD length before any LLM call

---

## 👤 Author

**Egiti Guru Venkata Krishna**  
VIT-AP University · CSE — Artificial Intelligence & Machine Learning · CGPA: 9.20

- 🌐 Live: [sume-ai.vercel.app](https://sume-ai.vercel.app)
- 💻 GitHub: [github.com/EgitiGuruVenkataKrishna](https://github.com/EgitiGuruVenkataKrishna)

---

<p align="center">
  Made with ☕ and too many API calls.<br/>
  If this helped you land a job, give it a ⭐
</p>
