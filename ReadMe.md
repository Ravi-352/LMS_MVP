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
or manual commands to crete DB -->

```
# docker command to create a postgres container -->
docker run -d \
  -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -v postgresql_db_pgdata:/var/lib/postgresql/data \
  postgres:15

```
```
# Verifying container running -

docker ps -a
#OUTPUT
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS                                         NAMES
e32853614ac1   postgres:15   "docker-entrypoint.s…"   4 minutes ago   Up 4 minutes   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   musing_mahavira

```

##### Creating DB in the container -  
```
 docker exec -it musing_mahavira createdb -U postgres lmsdb

#verifying:
docker exec -it musing_mahavira psql -U postgres -l
```

Expected output:
```
List of databases
   Name    |  Owner   | Encoding |  Collate   |   Ctype    | ICU Locale | Locale Provider |   Access privileges
-----------+----------+----------+------------+------------+------------+-----------------+-----------------------
 lmsdb     | postgres | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            |
 postgres  | postgres | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            |
 template0 | postgres | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            | =c/postgres          +
           |          |          |            |            |            |                 | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            | =c/postgres          +
           |          |          |            |            |            |                 | postgres=CTc/postgres
(4 rows)

```


#### Schema/Model creation in DB
We need to set current index/state of DB with Alembic -
```
alembic upgrade head 
```
Sample Output:
<img width="1445" height="477" alt="image" src="https://github.com/user-attachments/assets/992f324c-f1df-48cf-b7c1-927b642ad9ea" />

```
NFO 2025-12-23 06:43:29,597 sqlalchemy.engine.Engine: [cached since 0.003852s ago] {'table_name': 'alembic_version', 'param_1': 'r', 'param_2': 'p', 'param_3': 'f', 'param_4': 'v', 'param_5': 'm', 'nspname_1': 'public'}
DEBUG 2025-12-23 06:43:29,598 sqlalchemy.engine.Engine: Col ('relname',)
INFO 2025-12-23 06:43:29,599 sqlalchemy.engine.Engine:
CREATE TABLE public.alembic_version (
        version_num VARCHAR(32) NOT NULL,
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
)


INFO 2025-12-23 06:43:29,599 sqlalchemy.engine.Engine: [no key 0.00018s] {}
INFO 2025-12-23 06:43:29,613 sqlalchemy.engine.Engine: COMMIT
```

Now we need to first create DB tables and indexes. Usually, we need to use alembic commands and env.py in backend/alembic folder.
In Alembic, env.py configures how migrations detect your SQLAlchemy models and apply them to the database. To make Alembic automatically generate migrations for tables, indexes, constraints, you must:

✔ Import your Base metadata
✔ Attach your database engine (from settings)
✔ Enable autogenerate feature

Command to generate initial/base tables and indexes --.
```bash
alembic revision --autogenerate -m "initial migration"
```


A db schema version file gets generated in alembic/versions folder. If the tables in the file seems okay then we can commit it directly to DB using below command -->

Version file screenshot for reference --

<img width="706" height="731" alt="image" src="https://github.com/user-attachments/assets/bd9ffb99-7671-47fb-b9d2-5640ad3430f8" />



```bash
alembic upgrade head

```

**But, if in case above commands didn't work we made a work around. **
#when alembic autogenerate not able to generate version file that has all models/tables, can use the script to manually generate DDL (Data Definition Language) -->

```bash 
python3 generate_ddl.py > initial_schema.sql
```

**Wrap generated raw SQL into a new revision file inside alembic/versions using op.execute() under def upgrade(): function**

```bash
alembic upgrade head

```
THis commits all the tables and indexes to DB.

Now log in the DB and cross-check if required tables created -

```bash
# login to lmsdb
psql postgresql://postgres:postgres@localhost:5432/lmsdb
```

```sql
lmsdb=# \dt
```
OUTPUT:
<img width="446" height="405" alt="image" src="https://github.com/user-attachments/assets/fe5671a6-bc97-400c-9c1d-96254db65f63" />

SQL portable style verification:

```sql
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```
<img width="323" height="500" alt="image" src="https://github.com/user-attachments/assets/59806c7f-5295-4d97-891d-b8783812f69a" />


#################################################################################################


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










