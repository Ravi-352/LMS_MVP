from pydantic import BaseSettings, AnyHttpUrl
#from pydantic_settings import BaseSettings
from typing import List
import ast


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # cookie config
    COOKIE_SECURE: bool = False          # set False in development, True in production
    COOKIE_SAMESITE: str = "lax"       # "none" for cross-site; "lax" for same-site
    COOKIE_DOMAIN: str = None           # optional

    CORS_ORIGINS: list[str]
    FRONTEND_URL: AnyHttpUrl
    ADMIN_FRONTEND_URL: AnyHttpUrl | None = None

    EMAIL_FROM: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str = None
    SMTP_PASSWORD: str = None
    SMTP_USE_TLS: bool = False

     # parse CORS_ORIGINS from a comma-separated string in env

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
