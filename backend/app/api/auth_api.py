from typing import Annotated
from fastapi import APIRouter, Depends, Response

from app.db.schema import DbSession
from app.models.auth_models import AuthUserRequest, UserData
from app.services import auth_service
from app.core.config import config
from app.docs.auth_docs import auth_responses

router = APIRouter(
    prefix="/auth"
)

@router.post("/register", responses=auth_responses["register"])
def register_user(request: AuthUserRequest, db: DbSession) -> dict[str, str]:
    auth_service.register_user(request, db)
    return {"message" : "user registered"}


@router.post("/login", responses=auth_responses["login"])
def login(response: Response, request: AuthUserRequest, db: DbSession) -> dict[str, str]:
    token, user = auth_service.login(request, db)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token.access_token}",
        httponly=True,
        max_age=auth_service.ACCESS_TOKEN_EXPIRATION_TIME_SECONDS,
        samesite="strict",
        secure=config.secure_cookie, 
        path="/"
    )
    response.set_cookie(
        key="token",
        value=f"token",
        max_age=auth_service.ACCESS_TOKEN_EXPIRATION_TIME_SECONDS,
        samesite="strict",
        secure=config.secure_cookie, 
        path="/"
    )
    return {
        "message": "login successful",
        "user_id": str(user.user_id),
        "username": user.username
    }

@router.post("/logout", responses=auth_responses["logout"])
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="token", path="/")
    return {"message": "logout successful"}

@router.get("/token_data", responses=auth_responses["token_data"])
def get_token_data(token_data: auth_service.AuthUserData) -> UserData:
    return token_data