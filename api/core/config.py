import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env", override=True)

# Environment settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Server configuration
PORT = int(os.getenv("PORT", 8000))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Rate limiting
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/hour")

# Groq API Keys Configuration (Round-Robin Rotation Settings)
from typing import List
from pydantic import BaseModel, Field

class Settings(BaseModel):
    groq_api_keys: str = Field(default="")
    groq_keys: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        v = self.groq_api_keys or ""
        if v:
            self.groq_keys = [key.strip() for key in v.split(",") if key.strip()]
        else:
            # Fallback gracefully if legacy separate keys are present
            legacy = [
                os.getenv("GROQ_API_KEY"),
                os.getenv("GROQ_API_KEY_2"),
                os.getenv("GROQ_API_KEY_3")
            ]
            self.groq_keys = [k.strip() for k in legacy if k and k.strip()]

settings = Settings(groq_api_keys=os.getenv("GROQ_API_KEYS", ""))
GROQ_API_KEYS = settings.groq_keys

# Database setup
# Fallback to local SQLite file for development
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{BASE_DIR}/sume_ai.db"
elif DATABASE_URL.startswith("postgres://"):
    # Fix Render/Heroku legacy postgres connection string
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLAlchemy Database configuration
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from slowapi import Limiter
from fastapi import Request

# Add connect_args for SQLite to avoid threading issues
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_client_ip(request: Request) -> str:
    """Resolves client IP, parsing X-Forwarded-For if behind a proxy."""
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

# Initialize global rate limiter with proxy-aware IP resolver
limiter = Limiter(key_func=get_client_ip)

