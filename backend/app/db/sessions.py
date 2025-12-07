from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from app.db.base import Base




# create_engine → Connects to your database
# sessionmaker → Factory to create DB sessions (transactions)
# declarative_base → Base class to define models (tables)
# settings → Loads DATABASE_URL from .env

# engine = actual connection to database
# pool_pre_ping=True → checks DB connection is alive before using (avoids stale connections)

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# SessionLocal() will give a database session object
# autocommit=False → you must explicitly commit changes
# autoflush=False → session won’t automatically push pending changes until commit
# bind=engine → connects session to our DB engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# simple dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
