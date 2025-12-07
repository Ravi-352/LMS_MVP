# LMS MVP (Monorepo) — FastAPI backend + Next.js frontend

## What this repo contains
- backend/ : FastAPI monolithic backend (auth, courses, enrollment, assessments, feedback)
- frontend/: Next.js 14 frontend (App Router) with minimal Udemy-like UI

This is an *MVP* implementation intended to be simple, readable, and easy to extend.

## Prerequisites
- Docker & Docker Compose (recommended) OR
- Python 3.11+, Node 18+
- Git (optional)
- PostgreSQL

## Quickstart without Docker (from local for testing) -
1. Apply migration on deployment:  
```bash
alembic upgrade head

```
2. Then run your app with:  
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000

```
or Or with Gunicorn + Uvicorn workers for real production:  
```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --workers 2 --bind 0.0.0.0:8000

```

## Quickstart with Docker (recommended)
1. Copy env file:
   ```bash
   cp backend/.env.example backend/.env
```

2. From backend/ run:
    ```bash
    docker compose up --build
```
Backend will be on http://localhost:8000 and OpenAPI docs at http://localhost:8000/docs

3. Run Frontend:
 ```bash
 cd frontend
 npm install
 npm run dev
 ```

Frontend runs on http://localhost:3000.

In development, the frontend fetches backend endpoints at http://localhost:8000. If you prefer, update fetch URLs in components to match.


## Key flows to test manually

Sign up:

POST /auth/signup with { "email": "you@example.com", "password": "pass" }

List courses:

GET /courses/

Create a course:

POST /courses/ with CourseCreate JSON (use tools like Postman)

Enroll:

POST /enroll/enroll with { "user_id": 1, "course_id": 1 }

Update progress:

POST /enroll/progress?user_id=1&course_id=1&progress=30.0

Submit feedback (works only if progress >=25):

POST /feedback/ with { "user_id": 1, "course_id": 1, "rating": 4, "comment_markdown": "Nice course" }

```bash

---

# 5) Quick API testing (curl examples)

**Signup**

curl -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret"}'


** Create Course **

curl -X POST http://localhost:8000/courses/ -H "Content-Type: application/json" \
  -d '{"title":"Intro Python","slug":"intro-python","description":"Demo course","is_udemy":false,"sections":[{"title":"Basics","lessons":[{"title":"Lesson1","type":"video","youtube_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}]}]}'


** Enroll **
curl -X POST http://localhost:8000/enroll/enroll -H "Content-Type: application/json" \
  -d '{"user_id":1,"course_id":1}'

** Update Progress **

curl -X POST "http://localhost:8000/enroll/progress?user_id=1&course_id=1&progress=30"

** Post Feedback after 25% completion **

curl -X POST http://localhost:8000/feedback/ -H "Content-Type: application/json" \
  -d '{"user_id":1,"course_id":1,"rating":5,"comment_markdown":"Great course!"}'

```

################
connecting to DB - ```psql postgresql://postgres:postgres@localhost:5432/lmsdb```
DB commands - 
```SQL
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'users' AND table_schema = 'public';
```

```SQL
SELECT * FROM alembic_version;
INSERT INTO alembic_version (version_num) VALUES ('c8915a1ee2e7');
DELETE FROM alembic_version WHERE version_num = '756f3eadd5ba';

