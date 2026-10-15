# CareerPilot AI — Resume & Career Guidance Agent

A deployable MVP with a React + TypeScript frontend and FastAPI backend. It provides transparent heuristic resume readiness scoring, job-description skill matching, interview practice prompts, and a four-week learning roadmap.

## Features
- Resume text analysis and section checklist
- Skills detected from a built-in skill vocabulary
- Optional job description matching and missing-skill feedback
- Role-specific interview practice prompts
- Four-week starter roadmap for Machine Learning Engineer and Data Analyst roles
- Responsive dashboard and Render deployment configuration

## Important limitations
- The resume score is a transparent heuristic, **not** an official ATS score or hiring prediction.
- Interview questions come from a built-in template bank, not a live LLM.
- Resume text is submitted to your own backend for analysis; this MVP does not store it in a database.
- This MVP does not implement authentication or recruiter accounts. Do not use it to make automated hiring decisions.

## Run locally
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

### Frontend
In a second terminal:
```bash
cd frontend
npm install
```
Create `frontend/.env` with:
```env
VITE_API_URL=http://127.0.0.1:8000
```
Then run:
```bash
npm run dev
```
Open http://localhost:5173.

## Deploy to Render
### 1. Backend Web Service
- Repository: your GitHub repository
- Root Directory: `backend` (or `learnmate-ai/backend` if your repo contains an outer `learnmate-ai` directory)
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variable: `CORS_ORIGINS=https://YOUR-FRONTEND.onrender.com,http://localhost:5173,http://127.0.0.1:5173`

Test `https://YOUR-BACKEND.onrender.com/` and `/docs`.

### 2. Frontend Static Site
- Root Directory: `frontend` (or `learnmate-ai/frontend` if nested)
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`
- Environment variable: `VITE_API_URL=https://YOUR-BACKEND.onrender.com` (no `/docs`, no trailing slash)

After deploying the frontend, copy its actual URL into the backend `CORS_ORIGINS` value and redeploy the backend. Vite environment variables are applied at build time, so redeploy the frontend after changing `VITE_API_URL`.

## GitHub upload
Keep `backend/`, `frontend/`, `.gitignore`, `README.md`, and `DEPLOYMENT.md` at the repository root. Do not upload `.env` files, secrets, `node_modules`, or virtual environments.
