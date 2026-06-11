from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from api.core.config import Base

# ── SQLAlchemy ORM Models ───────────────────────────────────────────────────

class DBResumeAnalysis(Base):
    """Database record for a resume analysis."""
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)
    resume_filename = Column(String(255), nullable=True)
    resume_text = Column(Text, nullable=False)
    job_description = Column(Text, nullable=False)
    overall_score = Column(Integer, nullable=False, index=True)
    missing_keywords = Column(JSON, nullable=True)  # List of keyword dicts
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class DBFeedback(Base):
    """Database record for user feedback messages."""
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), default="Anonymous")
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── Pydantic Validation Models ────────────────────────────────────────────────

class KeywordDetail(BaseModel):
    """Structured detail of a missing keyword."""
    keyword: str
    importance: str = Field(default="", description="Explanation of keyword importance in JD")


class RewriteSuggestion(BaseModel):
    """Weak resume bullet point compared against optimized version."""
    original: str = Field(description="Exact match of original text from the resume")
    rewritten: str = Field(description="Optimized bullet point with action verbs and metrics")
    why: str = Field(default="", description="Reason for the change")


class ATSParsedSection(BaseModel):
    """Simulated ATS section parsing check."""
    name: str = Field(description="Section name, e.g. 'Contact Info', 'Experience', 'Education'")
    status: str = Field(description="Detection status: 'found', 'missing', or 'warning'")
    detail: str = Field(default="", description="Details on what was found or warning reasons")


class AnalysisResult(BaseModel):
    """Validated structured resume analysis payload."""
    mathematical_reasoning: str = Field(default="", description="Step-by-step mathematical calculation of the overall and section scores")
    overall_score: int = Field(ge=0, le=100, description="ATS match score 0-100")
    summary: str = Field(default="", description="General assessment summary")
    missing_keywords: List[KeywordDetail] = Field(default=[], description="List of keywords missing")
    strengths: List[str] = Field(default=[], description="Strengths identified in the resume")
    improvements: List[str] = Field(default=[], description="Actionable points of improvement")
    ats_issues: List[str] = Field(default=[], description="ATS structure issues")
    section_scores: Dict[str, int] = Field(default={}, description="Score breakdown by section")
    rewrites: List[RewriteSuggestion] = Field(default=[], description="Before/after rewrite list")
    ats_parsed_sections: List[ATSParsedSection] = Field(default=[], description="ATS parsing checklist")
    updated_resume_md: str = Field(default="", description="Complete updated resume in Markdown format")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence of model analysis")
