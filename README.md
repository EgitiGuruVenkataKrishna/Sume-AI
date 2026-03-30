# ⚡ Sume AI — ATS Resume Analyzer

> **AI-powered resume analysis system that simulates real ATS behavior and delivers precise, actionable improvements**

🌐 Live: https://sume-ai.vercel.app

---

## 🚀 Why This Project Matters

Most resumes fail before reaching a recruiter due to ATS filters.

**Sume AI solves this by:**

* Simulating real ATS parsing logic
* Identifying missing keywords based on job descriptions
* Generating **exact, actionable improvements** (not generic advice)

👉 Built as a **production-ready AI system**, not just a demo.

---

## 🧠 Key Capabilities

### 1. ATS Scoring Engine

* Multi-factor scoring (keywords, structure, relevance)
* Section-level evaluation (Experience, Skills, Formatting)
* ATS parsing simulation with structured output

### 2. AI-Powered Improvements

* Missing keyword detection with context
* Bullet-point rewrites (before → after)
* Actionable, ranked recommendations

### 3. Resume + Cover Letter Generation

* Resume rewriting with improved phrasing
* Tailored cover letter generation (grounded in input data)

---

## 🏗️ System Architecture

**Flow:**

```
User Input (Resume + JD)
        ↓
Parsing Layer (PDF / DOCX)
        ↓
LLM Analysis Engine
        ↓
Structured Scoring + Insights
        ↓
API Response (FastAPI)
        ↓
Frontend (Vercel)
```

---

## ⚙️ Tech Stack

* **Backend:** FastAPI
* **LLM:** Groq (Llama 3.1)
* **Parsing:** PyPDF, python-docx
* **Validation:** Pydantic
* **Infra:** Docker, Vercel

---

## 📡 API Highlights

### `/analyze-resume`

* Returns:

  * ATS score
  * missing keywords
  * section scores
  * improvements
  * rewrites

### `/generate-cover-letter`

* Generates tailored cover letter using resume + JD

---

## ⚡ Engineering Highlights

* Designed **structured LLM outputs** using validation layers
* Implemented **rate limiting** to prevent abuse
* Added **security headers** for production safety
* Built **stateless processing** (no resume storage)
* Optimized for **low-latency inference**

---

## 📊 What Makes It Production-Ready

* Input validation (file type, size, JD length)
* Error handling across all endpoints
* API-first design with clear contracts
* Deployed and accessible publicly

---

## 🚧 Limitations

* Dependent on LLM quality
* No persistent user sessions
* Limited customization for industry-specific resumes

---

## 📈 Future Improvements

* Multi-user accounts
* Resume history tracking
* Fine-tuned scoring models
* Advanced keyword weighting

---

## 👨‍💻 Author

**Guru Venkata Krishna**
B.Tech CSE (AI/ML), VIT-AP

* GitHub: https://github.com/EgitiGuruVenkataKrishna
* LinkedIn: https://linkedin.com/in/your-link

---

## ⭐ If this project helped you, consider starring it.
