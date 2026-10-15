# Deployment checklist

## Backend on Render
1. Create a Web Service and connect your GitHub repo.
2. Root Directory: `backend` (use `learnmate-ai/backend` if nested inside that folder).
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Set `CORS_ORIGINS` to your future frontend URL plus localhost origins.
6. Confirm `/` returns `{"name":"CareerPilot AI API","docs":"/docs","status":"ok"}`.

## Frontend on Render
1. Create a Static Site from the same repo.
2. Root Directory: `frontend` (use `learnmate-ai/frontend` if nested).
3. Build: `npm install && npm run build`
4. Publish Directory: `dist`
5. Set `VITE_API_URL` to the backend base URL, without `/docs` or a trailing slash.
6. Deploy and then update backend `CORS_ORIGINS` with the actual frontend URL.

## Smoke tests
- Open frontend and load sample resume.
- Analyze without and with a job description.
- Generate interview questions.
- Generate career roadmap.
- If requests fail, check browser console, `VITE_API_URL`, backend logs, and CORS configuration.
