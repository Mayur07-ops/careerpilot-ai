import os
import re
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="CareerPilot AI API", version="1.0.0", description="Resume analysis and career guidance MVP")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

SKILL_BANK = ["python", "sql", "machine learning", "deep learning", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "fastapi", "flask", "react", "typescript", "javascript", "html", "css", "git", "docker", "aws", "azure", "gcp", "power bi", "tableau", "excel", "statistics", "data analysis", "data visualization", "nlp", "computer vision", "postgresql", "mongodb", "rest api", "communication", "leadership", "problem solving", "project management", "agile", "linux", "pytorch", "xgboost"]

class AnalyzeRequest(BaseModel):
    resume: str = Field(min_length=20, max_length=30000)
    job_description: str = Field(default="", max_length=20000)
    target_role: str = "Machine Learning Engineer"

class QuestionsRequest(BaseModel):
    role: str = "Machine Learning Engineer"
    level: str = "Entry level"
    count: int = Field(default=8, ge=4, le=15)

class RoadmapRequest(BaseModel):
    role: str = "Machine Learning Engineer"
    skills: List[str] = []

def find_skills(text: str):
    low = text.lower()
    found = []
    for skill in SKILL_BANK:
        if re.search(r"(?<![a-z0-9+#])" + re.escape(skill) + r"(?![a-z0-9+#])", low):
            if skill not in found:
                found.append(skill)
    return found

@app.get("/")
def root():
    return {"name": "CareerPilot AI API", "docs": "/docs", "status": "ok"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    resume = req.resume.strip()
    words = re.findall(r"\b[\w+#.-]+\b", resume)
    skills = find_skills(resume)
    jd_skills = find_skills(req.job_description) if req.job_description.strip() else []
    matched = [s for s in jd_skills if s in skills]
    missing = [s for s in jd_skills if s not in skills]
    # Transparent heuristic score: structure + evidence + relevant skills, not a real ATS vendor score.
    sections = {"Contact details": bool(re.search(r"@|linkedin|github|\+?\d[\d ()-]{7,}", resume, re.I)),
                "Experience or internships": bool(re.search(r"experience|internship|intern |employment", resume, re.I)),
                "Projects": bool(re.search(r"projects?", resume, re.I)),
                "Education": bool(re.search(r"education|bachelor|b\.tech|degree|university|college", resume, re.I)),
                "Skills section": bool(re.search(r"skills|technologies|technical stack", resume, re.I))}
    section_score = round(sum(sections.values()) / len(sections) * 30)
    length_score = 20 if 250 <= len(words) <= 900 else (12 if 120 <= len(words) < 250 or 900 < len(words) <= 1200 else 5)
    skill_score = min(30, len(skills) * 3)
    keyword_score = round((len(matched) / len(jd_skills) * 20) if jd_skills else min(20, len(skills)))
    score = min(100, section_score + length_score + skill_score + keyword_score)
    suggestions = []
    if not sections["Contact details"]: suggestions.append("Add professional contact details and links to LinkedIn or GitHub.")
    if not sections["Experience or internships"]: suggestions.append("Add relevant experience, internships, volunteering, or practical work.")
    if not sections["Projects"]: suggestions.append("Add 2–3 relevant projects with measurable outcomes and tools used.")
    if not sections["Education"]: suggestions.append("Include your degree, institution, and expected graduation date.")
    if not sections["Skills section"]: suggestions.append("Add a clearly labeled technical skills section tailored to the target role.")
    if len(words) < 250: suggestions.append("Consider adding specific project details, impact, and evidence; the resume may be too brief.")
    if req.job_description and missing: suggestions.append("Where truthful, incorporate relevant job-description terms: " + ", ".join(missing[:8]) + ".")
    if not suggestions: suggestions.append("Strengthen bullets with measurable impact, action verbs, and evidence of results.")
    return {"score": score, "score_label": "Heuristic resume readiness score", "target_role": req.target_role,
            "word_count": len(words), "skills": skills, "job_skills": jd_skills, "matched_skills": matched,
            "missing_skills": missing, "match_percent": round(len(matched) / len(jd_skills) * 100) if jd_skills else None,
            "sections": sections, "suggestions": suggestions,
            "disclaimer": "This is a transparent heuristic assessment, not an official ATS score or hiring decision. Verify all suggestions and only claim skills you genuinely have."}

@app.post("/api/questions")
def questions(req: QuestionsRequest):
    role = req.role.strip() or "your target role"
    bank = [
      f"Explain a project where you used skills relevant to {role}. What was your contribution?",
      "Describe a difficult technical problem you solved and how you validated the solution.",
      "How do you debug an issue when the cause is unclear?",
      "Tell me about a time you received feedback and changed your approach.",
      "How do you prioritize tasks when several deadlines overlap?",
      "Explain a trade-off you made in a project and what you would improve now.",
      f"What core concepts should a candidate understand for an entry-level {role} role?",
      "Describe how you would communicate a complex technical result to a non-technical teammate.",
      "What would you monitor after deploying a project into production?",
      "Tell me about a mistake you made, how you corrected it, and what you learned.",
      "How do you keep your technical knowledge current?",
      "Walk through your resume and explain the evidence behind your strongest achievement.",
      "How would you handle a requirement that is ambiguous or changes midway through a project?",
      "What makes you a good fit for this role, and what are you actively improving?",
      "If you had one week to improve a project in your portfolio, what would you prioritize?"
    ]
    if "senior" in req.level.lower():
        bank[0] = f"Describe a system-level decision you made in {role} and the trade-offs involved."
        bank[8] = "How would you design monitoring, reliability, and incident response for a production service?"
    return {"role": role, "level": req.level, "questions": bank[:req.count], "note": "Practice prompts generated from a built-in template bank; they are not generated by a live LLM."}

@app.post("/api/roadmap")
def roadmap(req: RoadmapRequest):
    skills = {s.lower() for s in req.skills}
    role = req.role.lower()
    if "data analyst" in role:
        weeks = [
          {"week": "1", "title": "SQL and data cleaning", "tasks": ["Practice joins, CTEs, window functions", "Clean a messy CSV with pandas"]},
          {"week": "2", "title": "Analysis and statistics", "tasks": ["Review descriptive statistics and sampling", "Write 5 insight-driven analysis questions"]},
          {"week": "3", "title": "Visualization", "tasks": ["Build a Power BI or Tableau dashboard", "Explain 3 business insights"]},
          {"week": "4", "title": "Portfolio and interviews", "tasks": ["Publish a polished end-to-end project", "Practice SQL and case-study questions"]}]
        baseline = ["sql", "excel", "power bi", "tableau", "pandas", "statistics"]
    else:
        weeks = [
          {"week": "1", "title": "Python and data foundations", "tasks": ["Practice Python functions, collections, and testing", "Use pandas and NumPy to clean a dataset"]},
          {"week": "2", "title": "Core machine learning", "tasks": ["Build baseline regression and classification models", "Evaluate with suitable metrics and cross-validation"]},
          {"week": "3", "title": "Deployment and APIs", "tasks": ["Expose a model through FastAPI", "Add input validation, logging, and a README"]},
          {"week": "4", "title": "Portfolio and interview practice", "tasks": ["Polish one project with reproducible steps", "Practice ML fundamentals and explain model trade-offs"]}]
        baseline = ["python", "sql", "pandas", "scikit-learn", "statistics", "git", "fastapi"]
    missing = [s for s in baseline if s not in skills]
    return {"role": req.role, "weeks": weeks, "suggested_focus": missing[:6], "note": "A starter roadmap; adapt it to your current level, schedule, and target job descriptions."}
