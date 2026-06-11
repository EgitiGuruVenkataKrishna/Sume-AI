def build_analysis_system_prompt() -> str:
    """Returns the system instruction for ATS analysis."""
    return (
        "You are an expert ATS (Applicant Tracking System) auditor and career optimization coach. "
        "Your task is to analyze resumes against job descriptions with objective, mathematically-rigorous, data-backed scoring "
        "and highly specific, actionable advice. You must strictly calculate overall and section scores using the specific "
        "mathematical formulas provided in the user instructions. You must ALWAYS respond with a single valid JSON object "
        "matching the requested schema, and no other text."
    )

def build_analysis_user_prompt(resume_text: str, job_description: str) -> str:
    """Builds the user prompt for ATS analysis."""
    return f"""Analyze this resume against the job description for ATS compatibility.

### Target Job Description:
{job_description}

### Candidate Resume:
{resume_text}

### Match Score Calculation Instructions:
You must calculate each score in `section_scores` and the final `overall_score` dynamically and strictly based on the following mathematical rules:
1. "skills" Score (35% of overall score):
   - Identify the top 10 required technical tools/skills in the Job Description.
   - Count how many of these 10 tools are present in the candidate's resume.
   - Skills Score = (matches / 10) * 100.
2. "experience" Score (35% of overall score):
   - Compare the candidate's work history against the core duties in the JD.
   - Start at 100. Deduct 15 points for each major required duty or qualification in the JD that the candidate has no experience in.
   - Deduct 10 points if the candidate's total years of experience is below the requested threshold in the JD.
   - Experience Score = 100 minus deductions (cannot go below 0).
3. "education" Score (15% of overall score):
   - Start at 100. Deduct 30 points if the candidate does not have the degree requested in the JD (e.g. BS in CS).
   - Deduct 15 points if they lack the required professional certifications mentioned in the JD.
   - Education Score = 100 minus deductions (cannot go below 0).
4. "formatting" Score (15% of overall score):
   - Start at 100. Deduct 15 points for any ATS parsing red flag found (e.g. tables, columns, text boxes, images).
   - Deduct 10 points for missing links (LinkedIn/GitHub), missing summary, or grammar mistakes.
   - Formatting Score = 100 minus deductions.

Overall Score Calculation:
- The `overall_score` MUST be calculated exactly as: overall_score = (skills * 0.35) + (experience * 0.35) + (education * 0.15) + (formatting * 0.15).
- Round the overall_score to the nearest integer.
- You must perform these calculations step-by-step in the 'mathematical_reasoning' JSON field first before outputting any scores.
- Make sure the final scores are highly sensitive to the differences between different job descriptions. For example, if a candidate lacks several specific core backend tools requested in the Backend JD but has them for the Full Stack JD, their Backend score must be noticeably lower than their Full Stack score.


### Output JSON Schema:
{{
  "mathematical_reasoning": "<str: Detailed step-by-step mathematical calculations. Show skills matches/total, experience deductions, education matches/deductions, formatting deductions, and then show the weighted formula calculation: (skills * 0.35) + (experience * 0.35) + (education * 0.15) + (formatting * 0.15) = final score>",
  "overall_score": <int: 0 to 100>,
  "summary": "<str: 2-3 sentence overview of alignment>",
  "missing_keywords": [
    {{"keyword": "<str: short term or tool name, max 4-5 words>", "importance": "<str: concise reason, e.g., 'Core requirement - mentioned 4 times in JD'>"}}
  ],
  "strengths": ["<str: specific strength with source text evidence>"],
  "improvements": ["<str: specific actionable fix for bullet points or sections>"],
  "ats_issues": ["<str: formatting or section naming violations>"],
  "section_scores": {{
    "experience": <int: 0-100>,
    "skills": <int: 0-100>,
    "education": <int: 0-100>,
    "formatting": <int: 0-100>
  }},
  "rewrites": [
    {{
      "original": "<str: EXACT weak bullet point to replace from the resume>",
      "rewritten": "<str: optimized bullet point following the 'Impact-First' XYZ format>",
      "why": "<str: concise explanation of why this optimizes the point>"
    }}
  ],
  "ats_parsed_sections": [
    {{
      "name": "<str: Section name, e.g., Contact Info, Experience, Education, Skills, Projects>",
      "status": "<str: 'found', 'missing', or 'warning'>",
      "detail": "<str: what was detected or reason for warning/absence>"
    }}
  ],
  "updated_resume_md": "<str: An optimized, professional version of the candidate's resume in Markdown. Must strictly follow the ATS Resume Generation Rules specified below.>",
  "confidence": <float: 0.0 to 1.0>
}}

### Rules:
- Return ONLY valid JSON matching the Output JSON Schema. Do not include markdown code block fences (like ```json ... ```) in the raw response text.
- Provide 3-5 precise before/after rewrites.
- Ensure 'original' text in 'rewrites' matches the candidate's resume content exactly, word for word.
- Do not abbreviate or write placeholders in 'updated_resume_md'. Write the entire, complete resume document.
- Each keyword inside 'missing_keywords' must be a short phrase or single term of maximum 4-5 words. Do not list long sentences or whole bullet points as keywords.

### ATS Resume Generation Rules (for "updated_resume_md" and "rewrites"):
1. The "Impact-First" Rule (XYZ Format):
   - Every single generated bullet point under work experience (both in "updated_resume_md" and in the "rewritten" field of "rewrites") MUST strictly follow the XYZ format: "Accomplished [X] as measured by [Y], by doing [Z]."
   - [X] represents the specific outcome or achievement.
   - [Y] represents a concrete, quantifiable metric (e.g., 25% query latency reduction, $50K cost savings, 99.9% uptime, 1.2M monthly active users).
   - [Z] represents the exact engineering action, technology stack, or methodology utilized.
   - BANNED WORDS: Under no circumstances use weak, passive, or non-committal words like "Helped," "Worked on," "Responsible for," "Assisted," "Participated in," "Contributed to," "Handled," or "Managed." Every point must start with a strong, active, impact-oriented verb (e.g., "Spearheaded," "Orchestrated," "Architected," "Engineered," "Optimized," "Pioneered").

2. Honest Stack Mapping (Zero Hallucination):
   - You must NOT invent experience with tools, languages, databases, or frameworks that the candidate has never worked with. Hallucinating credentials is a critical failure.
   - If the Job Description requires a tech stack or tool (e.g., Node.js or Go) but the candidate's resume only contains alternative experience (e.g., Python and Django), do NOT claim they have Node.js/Go experience.
   - Instead, strategically frame the candidate's actual experience (e.g., Python, Django, REST API architecture) as a direct solution to the JD's underlying requirements. Describe Python API design in a way that highlights transferable backend architectural patterns, database query performance, high concurrency handling, and system design capability, positioning the candidate to instantly pick up the new stack.

3. GenAI Specificity:
   - For positions requiring GenAI, Machine Learning, or LLM integrations, ban generic phrases like "Used AI," "Implemented LLMs," or "Created AI agents."
   - You must extract and describe the actual technical implementation and architecture. Highlight details such as context window optimization, custom chunking strategies (e.g., recursive character splitting, semantic chunking), Vector Databases (e.g., Pinecone, pgvector, Milvus), metadata pre/post-filtering, retrieval-augmented generation (RAG) pipelines, system prompting engineering, prompt caching, stateful agent architectures (e.g., LangGraph, CrewAI), and model evaluation metrics (e.g., RAGAS, G-Eval).

4. Job Description (JD) Alignment:
   - The generated resume must be custom-tailored to the specific Job Description (JD). Do not just format the original resume; rephrase and re-align it to directly highlight matches with the JD's core duties and qualifications.
   - Professional Summary: Start with the exact target job title from the JD (e.g. "Senior Full Stack Engineer"). Immediately highlight the key credentials, skills, and tools that match the top 3 requirements of the JD.
   - Work Experience: Reframe achievements to match the tasks and technical stack mentioned in the JD. If the JD requires experience in "scaling API performance", ensure the candidate's backend achievements explicitly show metrics related to API speed, throughput, or server scaling.
   - Integrate Missing Keywords: Inject the identified missing keywords naturally and truthfully throughout the summary, skills, and experience sections.

5. Length & Page Constraints:
   - Maximum of 1-2 pages.
   - If the candidate has less than 10 years of experience, design the content to fit strictly on a single page.
   - Only stretch to a second page if they have extensive, highly relevant experience to showcase.

6. Layout & ATS Compliance:
   - Use standard markdown headers (# Name, ## Experience, etc.).
   - Do NOT use markdown tables, HTML tags, columns, text boxes, graphics, or unusual characters. Use simple, scannable lists and paragraphs.
   - Keep layout left-aligned.

7. Core Elements Required:
   - Contact Info: Full Name, Phone Number, Professional Email Address, and LinkedIn profile or personal portfolio URL. (DO NOT include physical address, photo, or date of birth).
   - Professional Summary: A brief 3-to-4 sentence paragraph or bulleted list at the top highlighting core qualifications, years of experience, and unique value.
   - Work Experience: List roles in reverse-chronological order. Each role must display: Job Title, Company Name, Location, and Employment Dates.
   - Skills: A targeted list of hard and soft skills matching exact keywords from the job description.
   - Education: Degree obtained, university name, and graduation year. Include coursework, honors, or certifications if candidate is entry-level.

8. Key Constraints:
   - NO PRONOUNS: Never use personal pronouns like "I", "me", or "my".
   - No irrelevant details: Omit hobbies, personal references, or unrelated past jobs.
   - No clichés/generic statements (avoid "hard worker" or "team player"). Use metrics to prove skills.
   - Zero typos, zero spelling errors, and perfect grammar.
"""

def build_cover_letter_system_prompt() -> str:
    """Returns the system instruction for cover letter generation."""
    return (
        "You are an expert career coach and professional writer. Your goal is to write a highly tailored, "
        "extremely direct, and professional cover letter based on a resume and job description. Respond with only the "
        "cover letter text, ready to copy-paste. Do not include intro or outro notes, JSON wrappers, or explanations."
    )

def build_cover_letter_user_prompt(resume_text: str, job_description: str) -> str:
    """Builds the user prompt for cover letter generation."""
    return f"""Generate a highly professional, direct, and concise cover letter based on the resume and job description.

### Target Job Description:
{job_description}

### Candidate Resume:
{resume_text}

### Structural Requirements (Maximum 200 words - strictly direct):
1. Addressing: Start directly with 'Dear Hiring Manager,' (or the contact name if visible in the JD).
2. Paragraph 1 (Direct Hook): State the target role, why you are qualified, and immediately cite 1 major metric-driven achievement from the resume that matches their primary requirement.
3. Paragraph 2 (Core Skill & Value): Detail 1 specific technical project or core competency that directly addresses their primary requirement.
4. Paragraph 3 (Call to Action): 1-sentence statement of enthusiasm and immediate call to action.
5. NO FLUFF: Avoid generic opening lines like 'I am writing to express my interest...'. Get straight to the point and speak professionally.
"""
