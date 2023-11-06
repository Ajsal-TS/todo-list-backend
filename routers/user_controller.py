from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from models import RevokedToken, Token, User_det, get_db
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

# for authenitcating the user
secret_key = "uisdfh9823h4rh4r8u34smkldnvvkndnoiebviewbufjcancciewc93ueu"
algorithm = "HS256"
# api_key = APIKeyHeader(name="Authorization",auto_error=True)
hashing = CryptContext(schemes=["bcrypt"])


def create_users(request, db):
    try:
        print(request.name)
        new_user = User_det(name=request.name, password=hashing.hash(request.password))
        db.add(new_user)
        db.commit()
        return {
            "status": "success",
            "message": "successfully created a new user",
            "data": [],
            "error": False,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Not Created",
        )


def refresh_tok(name: str, id: str, time, is_refresh_token=True):
    """Generate and returns refresh token.
    Params:
        name:name of the user
        id:id of the user
        time: accesstoken active time
        is_refresh_token: The status of the refresh token
    Return:
         return refresh token
    """
    payload = {"id": id, "name": name, "ref_token": is_refresh_token}
    expiration = datetime.utcnow() + time
    payload["expiration"] = expiration.isoformat()
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def token_gen(name: str, id: str, time):
    """Generate and returns the access token.
    Params:
        name:name of the user
        id:id of the user
        time: accesstoken active time
    Return:
         return access token"""
    payload = {"name": name, "id": id}
    expiration = datetime.utcnow() + time
    payload["expiration"] = expiration.isoformat()
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def get_current_user(token, db):
    """Returns the user id of current active user
    Params:
        Token: The token of the current user
    Return:
         userid of the current active user ."""
    try:
        revoked_token = (
            db.query(RevokedToken).filter(RevokedToken.token == token).first()
        )
        if revoked_token:
            raise HTTPException(status_code=401, detail="Token has been revoked")
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id: str = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user_id
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
