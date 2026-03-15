# 🎯 AI RESUME ANALYZER - COMPLETE PROJECT DETAILS

**Project Name:** AI Resume Analyzer  
**Developer:** Egiti Guru Venkata Krishna  
**University:** VIT-AP | CSE - AI & ML | CGPA: 9.20  
**Development Time:** Day 22 (4-5 hours)  
**Status:** In Development  

---

## 📋 PROJECT OVERVIEW

**Purpose:** Analyze resumes against job descriptions, provide ATS optimization scores, and suggest improvements.

**Problem Solved:** 75% of resumes never reach human recruiters due to ATS filtering. This tool helps candidates optimize their resumes for better visibility.

**Target Users:** Job seekers, students, early-career professionals preparing applications.

**Core Functionality:**
1. Upload resume PDF
2. Input job description
3. AI analyzes match quality
4. Returns score (0-100) + specific suggestions
5. Identifies missing keywords
6. Flags formatting issues
7. Suggests action verbs and quantification

---

## 🛠️ TECH STACK

### **Backend Framework: FastAPI**

**Choice:** FastAPI  
**Version:** 0.109.0  

**Why FastAPI:**
- **Async Support:** Handle multiple resume uploads simultaneously without blocking
- **Auto Documentation:** Built-in Swagger UI at `/docs` for testing
- **Type Safety:** Pydantic validation ensures clean data
- **Fast Performance:** ASGI-based, handles 1000+ req/min easily
- **Already Mastered:** Used in Production RAG system, no learning curve

**Alternative Considered:** Flask  
**Why Not:** No native async support, slower, no automatic validation

---

### **AI/LLM: Groq API (llama-3.1-8b-instant)**

**Choice:** Groq API  
**Model:** llama-3.1-8b-instant  

**Why Groq:**
- **Speed:** 10x faster than OpenAI (sub-second responses)
- **Cost:** Free tier (no API costs for student)
- **Quality:** Good accuracy for resume analysis
- **Experience:** Already integrated in RAG system

**Alternative Considered:** OpenAI GPT-4  
**Why Not:** Expensive ($0.03 per 1K tokens), slower response time

---

### **PDF Processing: PyPDF2**

**Choice:** PyPDF2  
**Version:** 3.17.4  

**Why PyPDF2:**
- **Simple:** Easy text extraction from PDFs
- **Reliable:** Handles 99% of resume formats
- **Lightweight:** No heavy dependencies
- **No OCR Needed:** Most resumes are text-based PDFs

**Alternative Considered:** pdfplumber  
**Why Not:** Overkill for simple text extraction, larger dependency

---

### **Data Validation: Pydantic**

**Choice:** Pydantic  
**Version:** 2.6.0  

**Why Pydantic:**
- **Structured Output:** Guarantees LLM returns valid JSON
- **Type Safety:** Automatic validation of input data
- **FastAPI Native:** Built-in integration with FastAPI
- **Error Handling:** Clear validation errors

**How Used:**
```python
class AnalysisResult(BaseModel):
    overall_score: int  # 0-100
    missing_keywords: List[str]
    strengths: List[str]
    improvements: List[str]
    ats_issues: List[str]
```

---

### **Database: PostgreSQL**

**Choice:** PostgreSQL  
**Version:** 15  

**Why PostgreSQL:**
- **Production Ready:** Handles concurrent writes (multiple users)
- **Analytics:** Track common resume weaknesses over time
- **Scalability:** Can handle millions of analyses
- **Free on Render:** Managed database included

**Alternative Considered:** SQLite  
**Why Not:** Single-writer limit, not suitable for production

**Schema:**
```sql
CREATE TABLE resume_analyses (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255),
    resume_text TEXT,
    job_description TEXT,
    overall_score INTEGER,
    missing_keywords JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analyses_email ON resume_analyses(user_email);
CREATE INDEX idx_analyses_score ON resume_analyses(overall_score);
```

---

### **Frontend: HTML + Tailwind CSS + Vanilla JavaScript**

**Choice:** Plain HTML/CSS/JS  

**Why Not React:**
- **Simplicity:** Just a form + results display
- **No Build Step:** Faster development
- **Faster Load:** No framework overhead
- **Sufficient:** No complex state management needed

**Why Tailwind CSS:**
- **Rapid Styling:** Utility-first classes
- **Responsive:** Mobile-friendly out of box
- **Small Bundle:** CDN version only 3KB gzipped

**Libraries Used:**
- Tailwind CSS (CDN)
- Chart.js (for score visualization)
- Marked.js (for markdown rendering of suggestions)

---

### **Deployment: Render**

**Choice:** Render.com  

**Why Render:**
- **Experience:** Already deployed RAG system here
- **Free Tier:** 512MB RAM, 100GB bandwidth
- **Auto Deploy:** Git push → automatic deployment
- **Managed DB:** PostgreSQL included free
- **SSL:** HTTPS automatic

**Alternative Considered:** Railway  
**Why Not:** Image size limits (already hit this with RAG)

---

### **Containerization: Docker**

**Choice:** Docker  

**Why Docker:**
- **Consistency:** Works same locally and in production
- **Dependencies:** All packages bundled
- **Easy Deploy:** Render supports Docker natively
- **Already Know:** Used in Week 3 projects

**Dockerfile Strategy:** Single-stage build (project is small)

---

## 🏗️ PROJECT ARCHITECTURE

```
┌─────────────┐
│   Browser   │
│  (Upload)   │
└──────┬──────┘
       │
       ▼ HTTP POST /analyze
┌─────────────────┐
│   FastAPI App   │
│  (main.py)      │
└────┬────────┬───┘
     │        │
     │        ▼ Extract Text
     │   ┌──────────┐
     │   │  PyPDF2  │
     │   └──────────┘
     │
     ▼ Analyze
┌──────────────┐
│  Groq API    │
│ (LLM call)   │
└──────┬───────┘
       │
       ▼ Store Result
┌──────────────┐
│ PostgreSQL   │
│  Database    │
└──────────────┘
       │
       ▼ Return JSON
┌──────────────┐
│   Browser    │
│ (Display)    │
└──────────────┘
```

---

## 📁 PROJECT STRUCTURE

```
resume-analyzer/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container config
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file
├── static/
│   ├── index.html         # Upload form
│   └── styles.css         # Custom styles (if needed)
├── templates/
│   └── results.html       # Results page (optional)
└── README.md              # Project documentation
```

---

## 🔌 API ENDPOINTS

### **1. Health Check**
```
GET /health
Response: {"status": "healthy"}
Purpose: Check if service is running
```

### **2. Analyze Resume**
```
POST /analyze-resume
Content-Type: multipart/form-data

Parameters:
- resume: File (PDF, max 5MB)
- job_description: String (max 5000 chars)
- user_email: String (optional, for tracking)

Response:
{
    "overall_score": 85,
    "missing_keywords": ["Python", "Docker", "CI/CD"],
    "strengths": [
        "Strong action verbs used",
        "Quantified achievements (increased by 40%)",
        "Clean formatting with proper sections"
    ],
    "improvements": [
        "Add 'Python' keyword (appears 5 times in JD)",
        "Replace 'Responsible for' with 'Led' or 'Managed'",
        "Add metrics to 'Built application' (how many users?)"
    ],
    "ats_issues": [
        "Use standard section headers (EXPERIENCE not Work History)",
        "Font size too small (use 11pt minimum)"
    ],
    "confidence": 0.92
}

Error Responses:
400: Invalid file format or size
500: Analysis failed
```

### **3. Get Analytics (Admin)**
```
GET /analytics/common-issues
Response: Top 10 most common resume problems

GET /analytics/score-distribution
Response: Histogram of scores (0-100)
```

---

## 💻 CORE CODE STRUCTURE

### **main.py**

```python
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pypdf import PdfReader
from pydantic import BaseModel, Field
from typing import List
import os
from groq import Groq

app = FastAPI(title="AI Resume Analyzer")

# Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Pydantic models
class AnalysisResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    missing_keywords: List[str]
    strengths: List[str]
    improvements: List[str]
    ats_issues: List[str]
    confidence: float = Field(ge=0.0, le=1.0)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/analyze-resume", response_model=AnalysisResult)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    user_email: str = Form(None)
):
    # Validate file
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    if resume.size > 5_000_000:  # 5MB
        raise HTTPException(400, "File too large (max 5MB)")
    
    # Extract text from PDF
    try:
        pdf = PdfReader(resume.file)
        resume_text = ""
        for page in pdf.pages:
            resume_text += page.extract_text()
    except Exception as e:
        raise HTTPException(400, f"Failed to read PDF: {str(e)}")
    
    # Analyze with LLM
    prompt = f"""Analyze this resume against the job description.

Job Description:
{job_description}

Resume:
{resume_text}

Provide analysis in this EXACT JSON format:
{{
    "overall_score": <number 0-100>,
    "missing_keywords": [<list of keywords from JD not in resume>],
    "strengths": [<list of 3-5 resume strengths>],
    "improvements": [<list of 3-5 specific improvements>],
    "ats_issues": [<list of ATS formatting problems>],
    "confidence": <number 0.0-1.0>
}}

Be specific and actionable. Focus on ATS optimization."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        result = AnalysisResult.model_validate_json(
            response.choices[0].message.content
        )
        
        # Store in database (optional)
        # save_to_db(user_email, resume_text, job_description, result)
        
        return result
        
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
```

---

## 📦 DEPENDENCIES

### **requirements.txt**

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
gunicorn==21.2.0
groq==0.4.2
pypdf==3.17.4
pydantic==2.6.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.25
```

**Why Each:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server for development
- `gunicorn` - Production WSGI server
- `groq` - LLM API client
- `pypdf` - PDF text extraction
- `pydantic` - Data validation
- `python-dotenv` - Load .env files
- `psycopg2-binary` - PostgreSQL driver
- `sqlalchemy` - ORM for database

---

## 🐳 DOCKER CONFIGURATION

### **Dockerfile**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .
COPY static/ static/

# Create upload directory
RUN mkdir -p /app/uploads

EXPOSE 8000

# Production server
CMD ["gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:$PORT", "--timeout", "120"]
```

**Why These Choices:**
- `python:3.10-slim` - Smaller image (200MB vs 1GB)
- `--no-cache-dir` - Reduces image size
- `gunicorn` - Production-ready, handles multiple workers
- `--workers 2` - Balance between performance and memory (free tier = 512MB)
- `--timeout 120` - LLM analysis can take 30-60 seconds

---

## 🌐 FRONTEND (index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Resume Analyzer</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <h1 class="text-4xl font-bold text-center mb-8">AI Resume Analyzer</h1>
        
        <form id="analyzeForm" class="bg-white p-8 rounded-lg shadow-md">
            <div class="mb-6">
                <label class="block text-gray-700 font-bold mb-2">Upload Resume (PDF)</label>
                <input type="file" id="resume" accept=".pdf" required
                       class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2">
            </div>
            
            <div class="mb-6">
                <label class="block text-gray-700 font-bold mb-2">Job Description</label>
                <textarea id="jobDesc" rows="8" required
                          placeholder="Paste the job description here..."
                          class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"></textarea>
            </div>
            
            <button type="submit" 
                    class="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-bold">
                Analyze Resume
            </button>
        </form>
        
        <div id="results" class="hidden mt-8 bg-white p-8 rounded-lg shadow-md">
            <h2 class="text-2xl font-bold mb-4">Analysis Results</h2>
            <div id="score" class="text-6xl font-bold text-center mb-6"></div>
            <div id="details"></div>
        </div>
    </div>
    
    <script>
        document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('resume', document.getElementById('resume').files[0]);
            formData.append('job_description', document.getElementById('jobDesc').value);
            
            try {
                const response = await fetch('/analyze-resume', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                // Display results
                document.getElementById('score').textContent = result.overall_score + '/100';
                document.getElementById('score').className = 
                    result.overall_score >= 80 ? 'text-green-600' :
                    result.overall_score >= 60 ? 'text-yellow-600' : 'text-red-600';
                
                let html = '';
                
                html += '<h3 class="font-bold text-lg mb-2">Strengths:</h3><ul class="list-disc pl-5 mb-4">';
                result.strengths.forEach(s => html += `<li>${s}</li>`);
                html += '</ul>';
                
                html += '<h3 class="font-bold text-lg mb-2">Missing Keywords:</h3><ul class="list-disc pl-5 mb-4">';
                result.missing_keywords.forEach(k => html += `<li>${k}</li>`);
                html += '</ul>';
                
                html += '<h3 class="font-bold text-lg mb-2">Improvements:</h3><ul class="list-disc pl-5 mb-4">';
                result.improvements.forEach(i => html += `<li>${i}</li>`);
                html += '</ul>';
                
                html += '<h3 class="font-bold text-lg mb-2">ATS Issues:</h3><ul class="list-disc pl-5">';
                result.ats_issues.forEach(a => html += `<li>${a}</li>`);
                html += '</ul>';
                
                document.getElementById('details').innerHTML = html;
                document.getElementById('results').classList.remove('hidden');
                
            } catch (error) {
                alert('Analysis failed: ' + error.message);
            }
        });
    </script>
</body>
</html>
```

---

## 🔐 ENVIRONMENT VARIABLES

### **.env** (Local Development)

```bash
# Groq API
GROQ_API_KEY=gsk_your_groq_api_key_here

# Database (local)
DATABASE_URL=postgresql://localhost/resume_analyzer

# Server
PORT=8000
ENVIRONMENT=development
```

### **Render Environment Variables** (Production)

```
GROQ_API_KEY = gsk_xxxxxxxxxxxxx
DATABASE_URL = (auto-set by Render)
PORT = (auto-set by Render)
ENVIRONMENT = production
```

---

## 🚀 DEPLOYMENT STEPS

### **1. Local Development**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Run locally
python main.py

# Test
curl http://localhost:8000/health
```

### **2. Push to GitHub**

```bash
git init
git add .
git commit -m "AI Resume Analyzer - Initial commit"
git remote add origin https://github.com/EgitiGuruVenkataKrishna/AI-Resume-Analyzer.git
git push -u origin main
```

### **3. Deploy to Render**

1. Go to render.com
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - Name: `ai-resume-analyzer`
   - Environment: `Docker`
   - Branch: `main`
5. Add environment variable:
   - `GROQ_API_KEY` = your key
6. Create Web Service
7. Wait 5-10 minutes
8. Get URL: `https://ai-resume-analyzer.onrender.com`

---

## ✅ TESTING

### **Manual Test**

```bash
# 1. Upload test resume
curl -X POST https://ai-resume-analyzer.onrender.com/analyze-resume \
  -F "resume=@test_resume.pdf" \
  -F "job_description=Looking for Python developer with FastAPI experience"

# 2. Check response
# Should return JSON with score and suggestions
```

### **Test Cases**

| Test Case | Input | Expected Output |
|-----------|-------|-----------------|
| Perfect match | Resume with all JD keywords | Score 90-100 |
| Partial match | Resume missing some keywords | Score 60-80, list missing keywords |
| Poor match | Resume unrelated to JD | Score 0-40, many improvements |
| Bad PDF | Corrupted file | 400 error |
| Large file | 10MB PDF | 400 error (too large) |

---

## 📊 PERFORMANCE METRICS

**Target Performance:**
- Response Time: <3 seconds (PDF extraction + LLM analysis)
- Throughput: 100 analyses per hour on free tier
- Accuracy: 85%+ match with human recruiter assessment

**Bottlenecks:**
1. LLM API call (1-2 seconds) - Can't optimize much
2. PDF parsing (0.1-0.5 seconds) - Already fast
3. Database write (0.05 seconds) - Negligible

**Total Expected Time:** 2-3 seconds per analysis

---

## 💡 FUTURE ENHANCEMENTS

**Phase 2 (if expanding):**
- Support DOCX format
- Multi-language resume support
- Resume template suggestions
- Side-by-side comparison with top candidates
- LinkedIn profile analyzer
- Cover letter generator
- ATS simulation (what recruiter sees)

**Tech Upgrades:**
- Add Redis for caching common job descriptions
- Implement rate limiting (5 analyses per email per day)
- Add user accounts with history
- Email reports with PDF of analysis
- Batch processing for multiple resumes

---

## 🎯 SUCCESS METRICS

**MVP Success Criteria:**
- ✅ Deploys successfully to Render
- ✅ Analyzes resume in <5 seconds
- ✅ Returns accurate missing keywords
- ✅ Provides actionable improvements
- ✅ Works on mobile (responsive design)
- ✅ Handles errors gracefully

**Interview Demo Success:**
- ✅ Can analyze resume live in interview
- ✅ Explains tech stack choices clearly
- ✅ Shows understanding of ATS systems
- ✅ Demonstrates production readiness

---

## 🔍 KEY DIFFERENTIATORS

**What Makes This Project Stand Out:**

1. **Solves Real Problem:** 75% of resumes filtered by ATS - this helps
2. **Production Ready:** Docker, cloud deployment, error handling
3. **Fast Development:** Built in 4-5 hours (shows efficiency)
4. **Relevant to Recruiters:** Shows understanding of hiring process
5. **Demonstrates Full Stack:** Backend (FastAPI) + Frontend (HTML/JS) + AI (LLM)
6. **Quantifiable Impact:** Scores 0-100, specific suggestions

**Interview Talking Points:**
- "Built this in 5 hours to help students optimize for ATS systems"
- "Uses Groq for 10x faster analysis than OpenAI"
- "Structured prompting with Pydantic ensures reliable JSON output"
- "Deployed on Render with Docker for production reliability"

---

## 📚 LEARNING OUTCOMES

**Skills Demonstrated:**
- ✅ FastAPI backend development
- ✅ LLM API integration (Groq)
- ✅ Prompt engineering for structured outputs
- ✅ PDF processing (PyPDF2)
- ✅ Pydantic data validation
- ✅ Docker containerization
- ✅ Cloud deployment (Render)
- ✅ Full stack development
- ✅ Production error handling

**Interview Questions You Can Answer:**
- "How do you ensure LLM returns valid JSON?" → Pydantic + structured prompts
- "How do you handle large PDF files?" → File size validation + streaming
- "How do you optimize for speed?" → Groq API (10x faster than OpenAI)
- "How do you deploy AI applications?" → Docker + Render workflow

---

## ⚠️ KNOWN LIMITATIONS

**Current Limitations:**
- PDF only (no DOCX support yet)
- English language only
- Max 5MB file size
- Free tier = slower cold starts (30-60 sec)
- No user accounts (anonymous usage)

**Mitigation:**
- Show error messages clearly
- Add file size check before upload
- Warn about cold start delay
- Consider adding DOCX if time permits

---

## 🎓 CONCLUSION

**Project Summary:**
AI-powered resume analyzer that scores resumes against job descriptions and provides ATS optimization suggestions. Built with FastAPI + Groq + Docker, deployed to Render.

**Development Time:** 4-5 hours  
**Complexity:** Medium (full stack + AI integration)  
**Impact:** High (solves real problem for job seekers)  
**Interview Value:** Very High (shows production skills + AI expertise)

**Status:** Ready for Day 22 development sprint!

---

**Developer:** Egiti Guru Venkata Krishna  
**Date:** Day 22 of 39-day AI Systems Engineer Roadmap  
**GitHub:** github.com/EgitiGuruVenkataKrishna/AI-Resume-Analyzer  
**Live Demo:** TBD (after deployment)

---

END OF DOCUMENT