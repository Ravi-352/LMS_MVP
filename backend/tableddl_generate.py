#when alembic autogenerate not able to generate version file that has all models/tables, can use this script to manually generate DDL (Data Definition Language)

# raw CREATE TABLE statements for your entire schema:
# Create a new file called generate_table_ddl.py in your backend/ directory

# After running the script --> python3 generate_ddl.py > initial_schema.sql

# wrap generated raw SQL into a new revision file inside alembic/versions using op.execute() under def upgrade(): function

import os
import sys
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.engine import default

# Ensure your app directory is in the path for imports
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, BASE_DIR)

from app.db.base import Base  # Import your Base
from app import models        # Import your models to register tables

print("--- RAW SQL DDL START ---")

# Use PostgreSQL dialect to ensure correct syntax is generated
dialect = default.DefaultDialect()

# 1. GENERATE CREATE TABLE STATEMENTS
for table in Base.metadata.sorted_tables:
    # Print CREATE TABLE statement
    print(str(CreateTable(table).compile(dialect=dialect)) + ";")
    print("\n")
    
# 2. GENERATE CREATE INDEX STATEMENTS
for table in Base.metadata.sorted_tables:
    # Iterate over any explicit Index objects defined on the table
    for index in table.indexes:
        # Print CREATE INDEX statement
        print(str(CreateIndex(index).compile(dialect=dialect)) + ";")
        print("\n")

print("--- RAW SQL DDL END ---")


