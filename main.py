"""
Sume AI — Resume ATS Analyzer Entrypoint
FastAPI application that serves the frontend and delegates API requests to modular routers.
"""

import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from api.core.config import engine, Base, ALLOWED_ORIGINS, limiter
from api.routes import analyze, feedback

# ── Logging Setup ────────────────────────────────────────────────────────────
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s" if not IS_PRODUCTION
    else '{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
    datefmt="%H:%M:%S" if not IS_PRODUCTION else "%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("sume-ai")

# ── Lifespan Startup/Shutdown ────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes database tables on startup."""
    logger.info("Starting up Sume AI Backend...")
    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified/created successfully.")
    except Exception as e:
        logger.critical(f"Database initialization failed: {str(e)}")
    yield
    logger.info("Shutting down Sume AI Backend...")


# ── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sume AI — Resume ATS Analyzer",
    description="Analyze resumes against job descriptions for ATS optimization",
    version="3.0.0",
    lifespan=lifespan,
)

# Attach rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Security Headers Middleware ──────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers and performance logging to every response."""
    start_time = time.time()
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    duration = round((time.time() - start_time) * 1000)
    if request.url.path not in ("/health", "/favicon.ico"):
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration}ms)")

    return response


# ── Register Routes ─────────────────────────────────────────────────────────
app.include_router(analyze.router, tags=["Resume Analysis"])
app.include_router(feedback.router, tags=["Feedback & Analytics"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "sume-ai", "version": "3.0.0"}


# ── Serve Static Assets ──────────────────────────────────────────────────────
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_frontend():
    """Serve the main frontend page."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Sume AI API is running. Static frontend assets are missing."}


# ── Entrypoint ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    PORT = int(os.getenv("PORT", 8000))
    print(f"\n  [*] Sume AI starting on http://localhost:{PORT}\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
