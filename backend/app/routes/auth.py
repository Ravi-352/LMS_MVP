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
from datetime import datetime, timezone
import hashlib
from pydantic.networks import EmailStr
from app.utils.email import send_mail
from app.core.security import hash_password
from app.schemas import ForgotPasswordRequest, ResetPasswordRequest
import hashlib
from slowapi import Limiter
from app.main import limiter

router = APIRouter()

# Very small JWT helpers (MVP)
def create_access_token(data: dict, expires_in=3600):
    payload = data.copy()
    payload.update({"exp": int(time.time()) + expires_in})
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token

@router.post("/signup", response_model=schemas.UserOut)
@limiter.limit("3/60minutes")
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = crud.create_user(db, user_in)
    return user


@router.post("/forgot-password")
@limiter.limit("3/60minutes")
def forgot_password(
    payload: ForgotPasswordRequest,
    #background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)):
    email = payload.email

    user = crud.get_user_by_email(db, email)
    if not user:
        return {"message": "If the email is registered, a reset token has been sent"}
    

    token_raw = crud.create_password_reset_token(db, user.id)
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token_raw}"


    # send email with reset_token (implement email sending logic here)
    send_mail(
        to=email,
        subject="Password Reset Request",
        body=f"Click the link to reset your password: {reset_link}\n\n"
                f"This link will expire in 30 minutes."
    )
    return {"message": "If the email is registered, a reset token has been sent"}

@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    
    #user = crud.get_user_by_email(db, email)
    #if not user:
    #    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token or email")
    #hash token from payload

    if len(payload.new_password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")

    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()

    # find  valid token
    prt = db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.token_hash == token_hash,
        models.PasswordResetToken.is_used == False,
        models.PasswordResetToken.expires_at > datetime.now(timezone.utc),
    ).first()
    if not prt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    
    # Load user associated with token
    user = db.query(models.User).filter(models.User.id == prt.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    
    # Update password
    user.hashed_password = hash_password(payload.new_password)

    # Mark token as used
    prt.is_used = True
    db.commit()
    
    return {"message": "Password has been reset successfully"}

@router.post("/token")
@limiter.limit("3/60minutes")
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
