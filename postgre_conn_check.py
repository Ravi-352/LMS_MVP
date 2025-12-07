import psycopg2
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from a .env file in project root

try:
    conn = psycopg2.connect(
        dbname="lmsdb",
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password"),
        host="localhost",
        port=5432
    )
    print("Connected successfully!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)

