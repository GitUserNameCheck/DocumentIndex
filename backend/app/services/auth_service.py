from datetime import datetime, timedelta, timezone
import logging
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from app.core.config import config
from app.db.schema import User
from app.models.auth_models import AuthUserRequest, UserData, Token

SECRET_KEY = config.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION_TIME_SECONDS = 7200 # 2 hours

password_hash = PasswordHash.recommended()
oauth2_bearer  = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

def verify_token(token: str) -> UserData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) 
        return UserData(user_id=payload.get("user_id"), username=payload.get("username"))
    except jwt.PyJWTError as e:
        logging.info(f"Token verification failed {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

def get_current_user(request: Request) -> UserData:
    cookie_access_token = request.cookies.get("access_token")

    if cookie_access_token and cookie_access_token.startswith("Bearer "):
        cookie_token = cookie_access_token.split(" ")[1]
        return verify_token(cookie_token)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
AuthUserData = Annotated[UserData, Depends(get_current_user)]

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def register_user(request: AuthUserRequest, db: Session) -> None:
    user = db.query(User).filter(User.name == request.username).first()
    if(user is not None):
        logging.info(f"Failed to register user {request.username}. User with that name already exists")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with name {request.username} already exists",
        )
    user = User(name=request.username, password=get_password_hash(request.password))
    db.add(user)
    db.commit()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
    
def authenticate_user(username: str, password: str, db: Session) -> User | None:
    user = db.query(User).filter(User.name == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_access_token(user_id: int, username: str, expiration_time_seconds: int = ACCESS_TOKEN_EXPIRATION_TIME_SECONDS) -> str:
    encode = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(seconds = expiration_time_seconds)
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def login(request: AuthUserRequest, db: Session) -> tuple[Token, UserData]:
    user = authenticate_user(request.username, request.password, db)
    if user is None:
        logging.info(f"Failed to authenticate user: {request.username}.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(user.id, user.name)
    return Token(access_token=token, token_type="bearer"), UserData(user_id=user.id, username=user.name)