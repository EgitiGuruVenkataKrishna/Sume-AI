# ⚡ Sume AI — Premium ATS Resume Analyzer & Optimizer

> **A production-grade, asynchronous AI system that simulates real-world ATS parser behaviors and delivers high-fidelity, actionable resume improvements.**

🌐 [Live Demo](https://sume-ai.vercel.app) | 📸 Demo Screenshot:

![Sume AI Demo Dashboard](E:\Sume-AI\assets\demo_Image.png)

---

## 🏗️ System Architecture Flow

The following diagram traces the complete lifecycle of an analysis request, highlighting how input files are validated, parsed, and orchestrated through the resilient LLM pipeline.

```
┌────────────────────────────────────────────────────────────────────────┐
│                              Dark-Grid UI                              │
│         (Premium glassmorphic front-end with live particle wallpaper)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Upload Resume (.pdf/.docx) + Job Description
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Server Router                          │
│                      (api/routes/analyze.py)                           │
└───────────┬───────────────────────────────────────────────┬────────────┘
            │                                               │
            │ 1. Verify Magic Bytes                         │ 2. Thread-Offloaded Parser
            ▼ (api/core/security.py)                        ▼ (api/services/parser.py)
  ┌──────────────────┐                            ┌───────────────────┐
  │ PDF: %PDF        │                            │ asyncio.to_thread │
  │ DOCX: PK\x03\x04 │                            │ (Extracts Text)   │
  └──────────────────┘                            └─────────┬─────────┘
                                                            │
                                                            │ Resume Text + Job Description
                                                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        LLM Orchestration Layer                         │
│                       (api/services/llm.py)                            │
└───────────┬───────────────────────────────────────────────┬────────────┘
            │                                               │
            │ 3. Failover & Key Rotation                    │ 4. Output Validation & Recovery
            ▼                                               ▼
  ┌───────────────────────────┐                   ┌───────────────────────────┐
  │ Round-Robin Groq Rotation │                   │ Pydantic strict parsing   │
  │ (GROQ_API_KEYS array)     │                   │ JSON markdown recovery    │
  └─────────┬─────────────────┘                   └─────────┬─────────────────┘
            │                                               │
            ▼                                               ▼
  ┌───────────────────────────┐                   ┌───────────────────────────┐
  │ HTTP 429 System Overload  │                   │ AnalysisResult schema     │
  │ Circuit Breaker           │                   │ validation & fallback     │
  └───────────────────────────┘                   └─────────┬─────────────────┘
                                                            │
                                                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Router Response                         │
│                      (200 OK - JSONResponse)                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Writes record asynchronously
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         Local SQLite Database                          │
│                  (Persistent logs in sume_ai.db)                       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ The Engineering Edge (Why this is production-ready)

Sume AI is engineered to address the common bottlenecks and points of failure that cause standard AI wrappers and prototypes to degrade under real-world traffic.

### 1. Event Loop Protection
PDF and DOCX text extraction are highly CPU-bound operations. Running them synchronously blocks FastAPI's single-threaded event loop, delaying all concurrent API requests. Sume AI utilizes `asyncio.to_thread` to offload parsing to an external worker thread pool, keeping the main event loop completely unblocked and highly responsive.

### 2. Fault Tolerance & Key Rotation
To bypass the strict rate limits associated with free-tier AI APIs, we built a custom round-robin key rotation system. 
* The backend parses a comma-separated list of keys from `GROQ_API_KEYS`.
* It iterates sequentially through the available keys on each API call.
* If a key encounters an `HTTP 429` (RateLimitError), it automatically shifts to the next active key.
* If all keys are exhausted, a dedicated HTTP 429 **"System Overload"** circuit breaker is tripped, placing the user in our high-priority queue gracefully instead of crashing the server.

### 3. Magic Bytes Security Validation
Attackers can bypass frontend extensions by renaming malicious scripts to `resume.pdf`. Sume AI enforces raw file signature (magic bytes) validation. We read the initial bytes of the uploaded file stream and verify that:
* **PDFs** start exactly with `b"%PDF"`
* **DOCXs** start exactly with the ZIP signature `b"PK\x03\x04"`
* Files failing these structural checks are rejected instantly with an `HTTP 400` error before entering any downstream parsing processes.

### 4. Resilient AI Extraction
LLM outputs are notoriously unpredictable. Sume AI guarantees structural integrity by enforcing strict JSON validation against the Pydantic `AnalysisResult` schema. If the LLM wraps the response in markdown code fences (e.g., ` ```json `), our markdown recovery layer cleans it. If standard schema validation fails, a fallback JSON parser cleans the payload and attempts recovery with default attributes rather than raising an unhandled exception.

---

## ⚙️ Tech Stack

* **Language:** Python 3.10+
* **Framework:** FastAPI (Asynchronous Web Framework)
* **LLM Engine:** Groq API (Llama 3.1 70B Versatile)
* **Validation Layer:** Pydantic v2
* **Database:** SQLite / PostgreSQL (via SQLAlchemy)
* **Frontend:** Vanilla HTML5, CSS3, & Javascript (Modern glassmorphic UI, responsive layouts, live custom particles background, CSS variables)
* **Rate Limiting:** SlowAPI (Proxy-aware IP extraction)

---

## 🔧 Developer Setup

Follow these steps to deploy and run Sume AI locally:

### 1. Clone the Repository
```bash
git clone https://github.com/EgitiGuruVenkataKrishna/Sume-AI.git
cd Sume-AI
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```ini
# Environment
ENVIRONMENT=development
PORT=8000

# Groq API Configuration (Comma-separated keys for round-robin rotation)
GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3
GROQ_MODEL=llama-3.1-70b-versatile

# Dev Offline Override
MOCK_LLM_RESPONSE=false # Set to true to bypass live Groq API calls for offline styling/testing

# Rate Limiting & Security
RATE_LIMIT=10/hour
ALLOWED_ORIGINS=*

# Database URL (Defaults to local SQLite if left empty)
DATABASE_URL=sqlite:///sume_ai.db
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Server
Start the backend server using the entrypoint script:
```bash
python main.py
```
Or run directly via Uvicorn:
```bash
uvicorn main:app --reload --port 8000
```
The application will be available at `http://localhost:8000`.

---

## 👨‍💻 Author Details

**Guru Venkata Krishna**  
*B.Tech CSE (AI/ML) at VIT-AP University*

* 🌐 **LinkedIn:** [Guru Venkata Krishna](https://www.linkedin.com/in/guru-venkata-krishna-egiti-46070a303/)
* 💻 **GitHub:** [EgitiGuruVenkataKrishna](https://github.com/EgitiGuruVenkataKrishna)
