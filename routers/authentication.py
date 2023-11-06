from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel
from models import User_det, get_db
from routers.user_controller import get_current_user, hashing


# api_key = APIKeyHeader(name="Authorization",auto_error=True)
def authentic(name: str, password: str, db: Session = Depends(get_db)):
    """To authenticate the user and return user details"""
    username = db.query(User_det).filter(name == User_det.name).first()
    if not username:
        return False
    if not hashing.verify(password, str(username.password)):
        return False
    return username


def token_authenticate(request: Request, db: Session = Depends(get_db)):
    token_value = request.headers.get("Authorization")
    if not token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    id = get_current_user(token_value, db)
    return id
