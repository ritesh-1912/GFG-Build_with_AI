# GitHub Dev Card Generator

A beautiful, AI-powered GitHub profile card generator. This project analyzes a user's GitHub activity and uses Gemini 2.5 Flash to derive insights, technical skills, and a personality vibe to create a custom-themed dev card.

## Live Demo
- Frontend: https://github-card-frontend-790349081371.us-central1.run.app
- Backend Health: https://github-card-backend-790349081371.us-central1.run.app/health

## Features
- AI insights generated from GitHub profile data.
- Dynamic themed profile cards.
- FastMCP tool workflow for structured generation.
- Dockerized deployment on Google Cloud Run.

## Tech Stack
- AI/LLM: Gemini 2.5 Flash
- Orchestration: FastMCP
- Backend: FastAPI (Python)
- Frontend: Vanilla HTML/CSS/JS
- Deployment: Google Cloud Run

## Local Run
1. Create `.env` in project root or `backend/`:

```env
GOOGLE_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_pat_optional
```

2. Run backend:

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

3. Run frontend:
- Open `frontend/index.html` directly, or serve it with a static server.

## Deployment
Backend:

```bash
gcloud run deploy github-card-backend --source ./backend --port 8080 --allow-unauthenticated
```

Frontend:

```bash
gcloud run deploy github-card-frontend --source ./frontend --port 80 --set-env-vars BACKEND_URL=https://your-backend-url.run.app --allow-unauthenticated
```

## Project Structure
- `backend/`: FastAPI API, MCP tools, AI logic
- `frontend/`: static web app
- `docker-compose.yml`: local container setup
- `GEMINI.md`: project AI instructions
