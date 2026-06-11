import os
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from groq import AsyncGroq
from api.models.analysis import AnalysisResult
from api.core.config import load_dotenv

logger = logging.getLogger("sume-ai")

async def call_groq_with_fallback(call_kwargs: Dict[str, Any]) -> str:
    """
    Executes a Groq API call, rotating through available API keys in case of rate limits (HTTP 429).
    If all keys are exhausted due to rate limits, raises a custom 429 HTTPException for frontend interception.
    """
    from api.core.config import settings
    from groq import AsyncGroq, RateLimitError

    keys = settings.groq_keys
    if not keys:
        logger.critical("No Groq API keys configured in settings.groq_keys.")
        raise HTTPException(
            status_code=500,
            detail="Groq service is unconfigured. Please check environment variables."
        )

    last_error = None
    rate_limit_errors_count = 0

    for attempt, key in enumerate(keys):
        try:
            logger.info(f"Attempting Groq API call with Key {attempt + 1}/{len(keys)}")
            client = AsyncGroq(api_key=key)
            response = await client.chat.completions.create(**call_kwargs)
            return response.choices[0].message.content
        except RateLimitError as rl_err:
            rate_limit_errors_count += 1
            last_error = rl_err
            logger.warning(f"Groq API Key index {attempt} is exhausted: rate-limited (HTTP 429): {str(rl_err)}")
        except Exception as e:
            last_error = e
            logger.error(f"Groq API Key index {attempt} failed with error: {str(e)}")

    # If the loop completes and all keys have failed, raise SYSTEM_OVERLOAD
    logger.critical("All available Groq API keys have failed. Raising SYSTEM_OVERLOAD 429.")
    raise HTTPException(
        status_code=429,
        detail={
            "error_type": "SYSTEM_OVERLOAD",
            "message": "Sume AI is under heavy load. You have been placed in our high-priority queue."
        }
    )

def clean_llm_json_response(raw_content: str) -> str:
    """
    Cleans markdown code fences and balanced brackets from JSON response string.
    """
    cleaned = raw_content.strip()
    
    # Strip markdown block wraps
    if cleaned.startswith("```"):
        # Remove starting fence (e.g. ```json or ```)
        first_line_end = cleaned.find("\n")
        if first_line_end != -1:
            cleaned = cleaned[first_line_end:].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
            
    return cleaned

async def analyze_resume_llm(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Orchestrates the Groq LLM call to analyze a resume and returns a validated JSON dict.
    """
    from api.prompts.templates import build_analysis_system_prompt, build_analysis_user_prompt
    
    system_prompt = build_analysis_system_prompt()
    user_prompt = build_analysis_user_prompt(resume_text, job_description)
    
    # We choose llama-3.1-70b-versatile for higher reliability and higher limits on Groq.
    model_name = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    
    call_kwargs = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 2500,
        "response_format": {"type": "json_object"}
    }
    
    raw_content = await call_groq_with_fallback(call_kwargs)
    cleaned_content = clean_llm_json_response(raw_content)
    
    try:
        # Strict validation
        validated = AnalysisResult.model_validate_json(cleaned_content)
        return validated.model_dump()
    except Exception as parse_err:
        logger.error(f"JSON schema validation failed: {str(parse_err)}")
        # Fallback parsing strategy (clean up JSON and attempt recovery)
        try:
            raw_data = json.loads(cleaned_content)
            # Try to build Pydantic with fallback defaults
            validated = AnalysisResult.model_validate(raw_data)
            return validated.model_dump()
        except Exception as fallback_err:
            logger.error(f"Fallback validation failed: {str(fallback_err)}")
            raise HTTPException(
                status_code=500,
                detail="AI service returned structured data that could not be mapped to the validator. Please try again."
            )

async def generate_cover_letter_llm(resume_text: str, job_description: str) -> str:
    """
    Orchestrates the Groq LLM call to write a tailored cover letter.
    """
    from api.prompts.templates import build_cover_letter_system_prompt, build_cover_letter_user_prompt
    
    system_prompt = build_cover_letter_system_prompt()
    user_prompt = build_cover_letter_user_prompt(resume_text, job_description)
    
    # Text generation uses temperature 0.6 for custom variance
    call_kwargs = {
        "model": os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 1500
    }
    
    cover_letter = await call_groq_with_fallback(call_kwargs)
    return cover_letter.strip()
