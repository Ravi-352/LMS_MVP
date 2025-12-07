from sqlalchemy import create_engine, inspect

# 1. Connect to your database
# Replace this with your actual database URL
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/lmsdb"
engine = create_engine(DATABASE_URL)

# 2. Create the Inspector
inspector = inspect(engine)

# 3. Get all table names
table_names = inspector.get_table_names()

# 4. Print the result
print(f"Tables in database: {table_names}")

# To check for a specific table:
if 'users' in table_names:
    print("The 'users' table already exists.")
