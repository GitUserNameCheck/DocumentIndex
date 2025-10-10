from pydantic import BaseModel

class AuthUserRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserData(BaseModel):
    user_id: int | None = None
    username: str | None = None

class ErrorResponse(BaseModel):
    detail: str