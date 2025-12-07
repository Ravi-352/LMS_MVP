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

## Quickstart (from local for testing) -

### **PostgreSQL**

#### Starting DB -->
Running docker-compose for DB creates and starts postgresql DB

```
version: '3.8'
services:
  backend:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - postgres
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: lmsdb
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:

```

Change USER and PASSWORD when you run the above file -
```
docker-compose -f docker-compose.yml up -d
```

#### Schema/Model creation in DB
We need to first create DB tables and indexes. Usually, we need to use alembic commands and env.py in backend/alembic folder.
In Alembic, env.py configures how migrations detect your SQLAlchemy models and apply them to the database. To make Alembic automatically generate migrations for tables, indexes, constraints, you must:

✔ Import your Base metadata
✔ Attach your database engine (from settings)
✔ Enable autogenerate feature

Command to generate initial/base tables and indexes --.
```bash
alembic revision --autogenerate -m "initial migration"
```
A db schema version file gets generated in alembic/versions folder. If the tables in the file seems okay then we can commit it directly to DB using below command -->
```bash
alembic upgrade head

```
**But, above commands didn't work in this case. So we made a work around. **
#when alembic autogenerate not able to generate version file that has all models/tables, can use the script to manually generate DDL (Data Definition Language) -->

```bash 
python3 generate_ddl.py > initial_schema.sql
```

**Wrap generated raw SQL into a new revision file inside alembic/versions using op.execute() under def upgrade(): function**

```bash
alembic upgrade head

```
THis commits all the tables and indexes to DB.

### Spinning up the backend - in local - without docker
From backend root folder -->

2. Then run your app with:  
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000

```
or Or with Gunicorn + Uvicorn workers for real production:  
```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --workers 2 --bind 0.0.0.0:8000

```

### Spinning up the backend - in local - with docker
1. Copy env example file:
   ```bash
   cp backend/.env.example backend/.env
```
Make necessary changes in .env file.

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


