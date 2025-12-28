from pydantic import BaseSettings
#from pydantic_settings import BaseSettings
from typing import List
import ast


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # cookie config
    COOKIE_SECURE: bool = False          # set False in development
    COOKIE_SAMESITE: str = "lax"       # "none" for cross-site; "lax" for same-site
    COOKIE_DOMAIN: str = None           # optional

    CORS_ORIGINS: list[str]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
