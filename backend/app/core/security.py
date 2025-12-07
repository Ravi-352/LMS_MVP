# core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    if hasattr(password, "get_secret_value"):
        password = password.get_secret_value()
    return pwd_context.hash(password.strip())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hasattr(plain_password, "get_secret_value"):
        plain_password = plain_password.get_secret_value()
    return pwd_context.verify(plain_password.strip(), hashed_password)
