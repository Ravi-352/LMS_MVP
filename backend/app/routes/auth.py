from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app import crud, schemas, models
from jose import jwt, JWTError, ExpiredSignatureError
import time, secrets
from app.core.config import settings
from app.core import security, auth
from pydantic import SecretStr
from passlib.context import CryptContext

router = APIRouter()

# Very small JWT helpers (MVP)
def create_access_token(data: dict, expires_in=3600):
    payload = data.copy()
    payload.update({"exp": int(time.time()) + expires_in})
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

@router.post("/signup", response_model=schemas.UserOut)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = crud.create_user(db, user_in)
    return user

@router.post("/token")
def token(response: Response, user_in: schemas.LoginRequest, db: Session = Depends(get_db)):
#def token(response: Response, user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Authenticate and set HttpOnly access_token cookie + csrf_token cookie (double-submit)."""
    # For MVP using email/password in JSON body
    user = crud.get_user_by_email(db, user_in.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # verify password with passlib (crud.authenticate_user could be added)
    #password = user_in.password.get_secret_value()
    password = user_in.password
    if not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # We establish "student" as the default baseline context upon logging in
    token_payload = {
        "sub": str(user.id),
        "active_role": "student" 
    }
    
    #token = create_access_token({"sub": str(user.id)})
    token = create_access_token(token_payload)

    csrf_token = secrets.token_urlsafe(32)

     # cookie settings
    cookie_params = {
        "httponly": True,
        "secure": settings.COOKIE_SECURE,   # True in prod
        "samesite": settings.COOKIE_SAMESITE, # "none" for cross-site deployments
        "path": "/",
        # optionally set domain=settings.COOKIE_DOMAIN
    }

    # set access token cookie (HttpOnly)
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **cookie_params
    )

    # set csrf token cookie (NOT HttpOnly, accessible to JS)
    csrf_cookie_params = cookie_params.copy()
    csrf_cookie_params["httponly"] = False
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **csrf_cookie_params
    )


    #return {"access_token": token, "token_type": "bearer"}
    # Return user info (optional)
    return {"message": "ok", "user_id": user.id, "csrf_token": csrf_token}


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@router.post("/flip-role")
def flip_role(
    response: Response, 
    request: Request, 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Switches the user's active session context between Student and Instructor modes.
    """
    # 1. Determine current operating context from request state
    current_context = getattr(request.state, "active_role", "student")
    
    # 2. Compute target context direction
    target_context = "instructor" if current_context == "student" else "student"
    
    # 3. Security Guardrail: Verify eligibility if trying to access instructor mode
    if target_context == "instructor" and not getattr(current_user, "is_educator", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You are not authorized as an instructor. Please register your ID proof first."
        )
        
    # 4. Generate a fresh access token embedded with the new active context
    new_payload = {
        "sub": str(current_user.id),
        "active_role": target_context
    }
    new_token = create_access_token(new_payload)
    
    # 5. Drop the fresh cookie over the old one
    cookie_params = {
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "path": "/",
    }
    
    response.set_cookie(
        key="access_token",
        value=new_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **cookie_params
    )
    
    return {"message": "Role context switched successfully", "active_role": target_context}
    

@router.post("/logout")
def logout(response: Response):
    # clear cookies by setting expiry 0
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("csrf_token", path="/")
    return {"message": "logged out"}
