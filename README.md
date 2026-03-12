# Jarvis AI Study Agent

Jarvis is a full-stack AI study platform with:
- FastAPI backend APIs
- Next.js frontend dashboard
- RAG-style notes retrieval for tutoring
- Quiz generation + exam analysis
- PostgreSQL-ready SQLAlchemy schema
- Docker deployment files

## Structure

```text
backend/
frontend/
services/
deploy/
```

## Run backend

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`  
Backend: `http://localhost:8000`

## Core API routes
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/upload/notes`
- `POST /api/quiz/generate`
- `POST /api/mentor/chat`
- `POST /api/mentor/exam-analysis`

## Tests

```bash
pytest backend/tests -q
```

## Docker

```bash
cd deploy
docker compose up --build
```
