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

### create virtual python environment at backend root and activate it.
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

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

Change USER and PASSWORD when you run the above file and make it consistent across backend usage-
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

Backend will be on http://localhost:8000 and OpenAPI docs at http://localhost:8000/docs - to open Swagger page where we can test APIs created in backend.
<img width="1267" height="978" alt="image" src="https://github.com/user-attachments/assets/dbf05910-7604-4004-b14b-7c7b36054575" />

### Spinning up frontend -
#### Creating docker image --
```
# Building docker image -
docker build --build-arg NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1 -t lms-frontend:1.0 .

# Run container from the image created above --
docker run -dt -p 3000:3000 --env-file=.env.local lms-frontend:1.0
```
# Accessing frontend
http://localhost:3000/

Currently, this is new app and no courses available on Home page. We need to 
1. signup as instructor,
2. login
3. create/add courses
4. Check the same from a public view @ http://localhost:3000
5. Create a new user as a student, enroll for a course and start learning. After 25% progress see if Feedback button is enabled.

In development, the frontend fetches backend endpoints at http://localhost:8000/api/v1. If you prefer, update fetch URLs in components to match.

<img width="1817" height="452" alt="image" src="https://github.com/user-attachments/assets/1fc9a9a1-ccce-4901-b202-4de854947db0" />

```
# To Stop and delete all the containers running on the image -  "lms-frontend:1.0"
docker stop $(docker ps -aq --filter "ancestor=lms-frontend:1.0")| xargs docker rm

# To remove image - lms-frontend:1.0
docker rmi lms-frontend:1.0
```


################
Sample commands for DB:
Connecting to DB - ```psql postgresql://postgres:postgres@localhost:5432/lmsdb```

DB commands - 
1. CHeck schema present - different tables, fields etc.
```SQL
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'users' AND table_schema = 'public';
```

2. Check alembic versions and update - for manual rectifications.
```SQL
SELECT * FROM alembic_version;
INSERT INTO alembic_version (version_num) VALUES ('c8915a1ee2e7');
DELETE FROM alembic_version WHERE version_num = '756f3eadd5ba';

3. Manually searching user by email -
```SQL
SELECT * FROM users WHERE email='rk@gmail.com';
```
To exit from the DB console -- `q`
To exit from the DB connection ---> `exit`





