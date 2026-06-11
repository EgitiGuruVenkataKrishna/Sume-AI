import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.core.config import get_db, limiter
from api.models.analysis import DBFeedback, DBResumeAnalysis

logger = logging.getLogger("sume-ai")
router = APIRouter()

@router.post("/submit-feedback")
@limiter.limit("5/hour")
async def submit_feedback(
    request: Request,
    name: str = Form(default="Anonymous"),
    message: str = Form(..., min_length=5, max_length=1000),
    db: Session = Depends(get_db)
):
    """
    Accept user feedback and persist it to the relational database.
    """
    try:
        feedback_entry = DBFeedback(
            name=name.strip() or "Anonymous",
            message=message.strip()
        )
        db.add(feedback_entry)
        db.commit()
        db.refresh(feedback_entry)
        
        logger.info(f"Feedback received from: {feedback_entry.name} (Record ID: {feedback_entry.id})")
        return JSONResponse(content={"status": "success", "message": "Thank you for your feedback!"})
    except Exception as e:
        logger.error(f"Feedback persistence error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save feedback.")


@router.get("/analytics/user-count")
def get_user_count(db: Session = Depends(get_db)):
    """
    Returns the total count of analyzed resumes (seeded with 1000 for social proof).
    """
    try:
        db_count = db.query(DBResumeAnalysis).count()
        return {"count": 1000 + db_count}
    except Exception as e:
        logger.warning(f"Error querying analysis count: {str(e)}")
        return {"count": 1000}
