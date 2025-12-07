from fastapi import APIRouter, Header, Depends
from app.core.auth import get_current_user
from app.core.logging_config import logger
from app.core.config import settings
from jose import jwt
from pydantic import BaseModel

router = APIRouter(prefix="/logs", tags=["Logging"])

class LogEvent(BaseModel):
    message: str
    level: str = "info"

@router.post("/client")
def log_client_event(event: LogEvent, current_user=Depends(get_current_user)):
    user_id = getattr(current_user, 'id', 'unknown')
    message = event.get("message", "")
    level = event.get("level", "info")

    # Decode User ID from JWT
    #user_id = current_user.id
    
    log_msg = f"user={user_id} | {level.upper()} | {message}"
    
    if level == "error":
        logger.error(log_msg)
    else:
        logger.info(log_msg)

    return {"status": "logged"}