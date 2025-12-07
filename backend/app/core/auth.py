# backend/app/core/auth.py
from fastapi import Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
from app.db.sessions import SessionLocal
from app import models
from typing import Optional
from sqlalchemy.orm import Session

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")


#def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)):
def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    token = request.cookies.get("access_token")
    # token = credentials.credentials
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # Some setups send cookies like: "Bearer eyJhbGciOi..."
    if token.startswith("Bearer "):
        token = token.split(" ")[1]


    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        
        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication payload")
    
        user_id = int(sub)

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    user = db.query(models.User).get(user_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# CSRF verifier dependency: compares header to cookie (double submit)
def verify_csrf(request: Request):
    # For safety, only check when method is state-changing; caller should include as dependency in such routes
    header_token = request.headers.get("x-csrf-token")
    cookie_token = request.cookies.get("csrf_token")
    if not header_token or not cookie_token or header_token != cookie_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token")
    return True

def require_role(role: str):
    """
    Dependency factory that ensures current_user has given role.
    role: one of 'student', 'instructor', 'admin' (depends on your model)
    """
    def _require_role(current_user: models.User = Depends(get_current_user)):
        # we store boolean is_educator in user model; map to instructor
        if role == "student":
            # any authenticated user is a student unless blocked
            return current_user
        if role == "instructor":
            if not getattr(current_user, "is_educator", False):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Instructor role required")
            return current_user
        if role == "admin":
            # assume user.is_admin flag if you have it; else check email or DB role
            if not getattr(current_user, "is_admin", False):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
            return current_user
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid role config")
    return _require_role