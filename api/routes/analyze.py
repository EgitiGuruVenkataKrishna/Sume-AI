import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.core.config import get_db, limiter, RATE_LIMIT
from api.core.security import verify_file_signature
from api.services.parser import extract_text_async
from api.services.llm import analyze_resume_llm, generate_cover_letter_llm
from api.models.analysis import DBResumeAnalysis

logger = logging.getLogger("sume-ai")
router = APIRouter()

@router.post("/analyze-resume")
@limiter.limit(RATE_LIMIT)
async def analyze_resume(
    request: Request,
    resume: UploadFile = File(..., description="Resume PDF or DOCX file (max 5MB)"),
    job_description: str = Form(..., description="Job description text (max 5000 chars)"),
    db: Session = Depends(get_db)
):
    """
    Analyze a resume PDF/DOCX against a job description for ATS compatibility.
    Returns a structured analysis and logs the transaction.
    """
    # ── Validate inputs ──────────────────────────────────────────────────
    filename = resume.filename or ""
    
    # Read file content
    content = await resume.read()
    if len(content) > 5_000_000:
        raise HTTPException(status_code=400, detail="File too large. Maximum file size is 5MB.")

    if len(job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short. Please paste the full job description (at least 50 characters)."
        )

    if len(job_description) > 5000:
        raise HTTPException(status_code=400, detail="Job description is too long. Maximum 5000 characters.")

    # ── Verify Magic Byte Signatures ──────────────────────────────────────
    verify_file_signature(content, filename)

    # ── Extract Text Concurrently (Thread Offloaded) ──────────────────────
    resume_text = await extract_text_async(content, filename)

    if not resume_text or len(resume_text.strip()) < 50:
        file_type = "PDF" if filename.lower().endswith(".pdf") else "DOCX"
        raise HTTPException(
            status_code=400,
            detail=f"Could not extract sufficient text from the {file_type}. The file may be image-based, scanned, or corrupted."
        )

    # ── Analyze with Groq LLM ─────────────────────────────────────────────
    logger.info(f"Initiating resume analysis for {filename} ({len(resume_text)} chars)")
    
    analysis_result = await analyze_resume_llm(resume_text, job_description)

    # ── Save to Database ──────────────────────────────────────────────────
    try:
        db_analysis = DBResumeAnalysis(
            user_email=None,  # Expandable for authentication in future releases
            resume_filename=filename,
            resume_text=resume_text,
            job_description=job_description,
            overall_score=analysis_result["overall_score"],
            missing_keywords=analysis_result.get("missing_keywords", [])
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        logger.info(f"Analysis saved to database. Record ID: {db_analysis.id}")
    except Exception as db_err:
        logger.warning(f"Database insertion failed: {str(db_err)}")
        # Don't fail the API call if database logs fail
        db.rollback()

    return JSONResponse(content=analysis_result)


@router.post("/generate-cover-letter")
@limiter.limit(RATE_LIMIT)
async def generate_cover_letter(
    request: Request,
    resume: UploadFile = File(..., description="Resume PDF or DOCX file (max 5MB)"),
    job_description: str = Form(..., description="Job description text"),
    db: Session = Depends(get_db)
):
    """
    Generate a tailored cover letter based on the resume and job description.
    """
    filename = resume.filename or ""
    content = await resume.read()
    
    if len(content) > 5_000_000:
        raise HTTPException(status_code=400, detail="File too large. Maximum file size is 5MB.")

    # ── Verify Magic Byte Signatures & Extract Text ──────────────────────
    verify_file_signature(content, filename)
    resume_text = await extract_text_async(content, filename)

    if not resume_text or len(resume_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Could not extract sufficient text from the document. The file may be image-based or corrupted."
        )

    # ── Generate Cover Letter via LLM ─────────────────────────────────────
    logger.info(f"Generating cover letter for {filename}")
    cover_letter = await generate_cover_letter_llm(resume_text, job_description)
    
    return JSONResponse(content={"cover_letter": cover_letter})
