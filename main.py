"""
Sume AI — Resume ATS Analyzer Backend
FastAPI application that analyzes resumes against job descriptions using Groq LLM.
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from pydantic import BaseModel, Field
from typing import List
import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# ── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Sume AI — Resume ATS Analyzer",
    description="Analyze resumes against job descriptions for ATS optimization",
    version="1.0.0",
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_groq_client() -> Groq:
    """Create a Groq client with the current API key (re-reads .env each time)."""
    load_dotenv(override=True)  # Re-read .env to pick up changes
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not set. Please add it to your .env file.",
        )
    return Groq(api_key=api_key)

# ── Pydantic Models ──────────────────────────────────────────────────────────


class KeywordDetail(BaseModel):
    """A missing keyword with context on why it matters."""
    keyword: str
    importance: str = Field(description="Why this keyword matters — e.g., 'Appears 4 times in JD'")


class AnalysisResult(BaseModel):
    """Structured ATS analysis result from the LLM."""
    overall_score: int = Field(ge=0, le=100, description="ATS match score 0-100")
    summary: str = Field(description="2-3 sentence overall assessment")
    missing_keywords: List[KeywordDetail] = Field(description="Keywords from JD missing in resume")
    strengths: List[str] = Field(description="What the resume does well (3-5 items)")
    improvements: List[str] = Field(description="Specific, actionable improvements (3-5 items)")
    ats_issues: List[str] = Field(description="ATS formatting/compatibility issues")
    section_scores: dict = Field(
        description="Breakdown scores: experience, skills, education, formatting (each 0-100)"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence in analysis")


# ── Helper Functions ─────────────────────────────────────────────────────────


def extract_pdf_text(file) -> str:
    """Extract all text from a PDF file."""
    try:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")


def build_analysis_prompt(resume_text: str, job_description: str) -> str:
    """Build the LLM prompt for ATS analysis."""
    return f"""You are an expert ATS (Applicant Tracking System) analyst and career coach. 
Analyze the following resume against the given job description with extreme precision.

## Job Description:
{job_description}

## Resume:
{resume_text}

## Your Task:
Perform a thorough ATS compatibility analysis. Score the resume 0-100 based on:
- Keyword match (40% weight): How many critical keywords from the JD appear in the resume?
- Experience relevance (25% weight): Does the experience align with what the role needs?
- Skills alignment (20% weight): Are the required technical/soft skills present?
- Formatting & structure (15% weight): Is the resume ATS-parseable (standard sections, no tables/images, clean formatting)?

## Respond in this EXACT JSON format:
{{
    "overall_score": <number 0-100>,
    "summary": "<2-3 sentence overall assessment of the resume's ATS compatibility>",
    "missing_keywords": [
        {{"keyword": "<keyword>", "importance": "<why it matters, e.g. 'Mentioned 5 times in JD — critical skill'>"}}
    ],
    "strengths": [
        "<specific strength with evidence — e.g., 'Strong action verbs: Led, Architected, Delivered'>"
    ],
    "improvements": [
        "<specific, actionable fix — e.g., 'Replace \\'Responsible for managing\\' with \\'Managed a team of 8 engineers\\''>"
    ],
    "ats_issues": [
        "<specific ATS problem — e.g., 'Section header \\'Work History\\' should be \\'EXPERIENCE\\' for ATS compatibility'>"
    ],
    "section_scores": {{
        "experience": <0-100>,
        "skills": <0-100>,
        "education": <0-100>,
        "formatting": <0-100>
    }},
    "confidence": <0.0-1.0>
}}

## Rules:
- Be SPECIFIC and ACTIONABLE — no generic advice like "add more keywords"
- Reference exact phrases from the resume and JD when suggesting changes
- For missing_keywords, only include keywords that genuinely appear in the JD and are absent from the resume
- For improvements, give the EXACT replacement text (before → after)
- Score honestly — a poor match should score below 40
- Return ONLY valid JSON, no markdown formatting"""


# ── API Endpoints ────────────────────────────────────────────────────────────


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "sume-ai"}


@app.post("/analyze-resume", response_model=AnalysisResult)
async def analyze_resume(
    resume: UploadFile = File(..., description="Resume PDF file (max 5MB)"),
    job_description: str = Form(..., description="Job description text (max 5000 chars)"),
):
    """
    Analyze a resume PDF against a job description for ATS compatibility.
    Returns a structured analysis with score, missing keywords, and suggestions.
    """
    # ── Validate inputs ──────────────────────────────────────────────────
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported. Please upload a .pdf file.",
        )

    # Read file content to check size
    content = await resume.read()
    if len(content) > 5_000_000:  # 5MB
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum file size is 5MB.",
        )

    if len(job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short. Please paste the full job description (at least 50 characters).",
        )

    if len(job_description) > 5000:
        raise HTTPException(
            status_code=400,
            detail="Job description is too long. Maximum 5000 characters.",
        )

    # ── Extract text from PDF ────────────────────────────────────────────
    import io

    resume_text = extract_pdf_text(io.BytesIO(content))

    if not resume_text or len(resume_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Could not extract sufficient text from the PDF. The file may be image-based or corrupted. Please upload a text-based PDF.",
        )

    # ── Analyze with Groq LLM ───────────────────────────────────────────
    prompt = build_analysis_prompt(resume_text, job_description)

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert ATS resume analyst. Always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content

        # Parse and validate the response
        try:
            result = AnalysisResult.model_validate_json(raw_content)
        except Exception:
            # Try to parse as dict first, then validate
            raw_data = json.loads(raw_content)
            result = AnalysisResult.model_validate(raw_data)

        return result

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI returned invalid response format. Please try again. Error: {str(e)}",
        )
    except HTTPException:
        raise  # Re-raise our own HTTP exceptions (e.g. missing key)
    except Exception as e:
        error_msg = str(e)
        print(f"[Sume AI] Analysis error: {error_msg}")  # Log to console for debugging
        if "api_key" in error_msg.lower() or "invalid" in error_msg.lower() or "401" in error_msg or "authentication" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail=f"Groq API rejected the key. Please generate a new key at console.groq.com/keys. Details: {error_msg}",
            )
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed. Please try again. Error: {error_msg}",
        )


# ── Static Files ─────────────────────────────────────────────────────────────

# Serve the static directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def serve_frontend():
    """Serve the main frontend page."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Sume AI API is running. Frontend not found at /static/index.html"}


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    PORT = int(os.getenv("PORT", 8000))
    print(f"\n  [*] Sume AI starting on http://localhost:{PORT}\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
