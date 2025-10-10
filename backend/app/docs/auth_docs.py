from app.models.auth_models import ErrorResponse

register_responses = {
    200: {
        "description": "User registered successfully",
        "content": {
            "application/json": {
                "example": {"message" : "user registered"}
            }
        },
    },
    409: {
        "description": "User already exists",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "User with name qwerty already exists"}
            }
        },
    },
}

login_responses = {
    200: {
        "description": "Login successful",
        "content": {
            "application/json": {
                "example": {
                    "message": "login successful",
                    "user_id": "1",
                    "username": "qwerty"
                }
            }
        },
    },
    401: {
        "description": "Invalid credentials",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Invalid credentials"}
            }
        },
    },
}

logout_responses = {
    200: {
        "description": "Login successful",
        "content": {
            "application/json": {
                "example": {"message": "logout successful"}
            }
        },
    },
}

token_data_responses = {
    200: {
        "description": "Request successful",
        "content": {
            "application/json": {
                "example": {
                    "user_id": "1",
                    "username": "qwerty"
                }
            }
        },
    },
}

get_current_user_responses = {
    401: {
        "description": "Not authenticated",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {"detail": "Not authenticated"}
            }
        },
    },
}



auth_responses = {
    "register": register_responses,
    "login": login_responses,
    "logout": logout_responses,
    "token_data": {**token_data_responses, **get_current_user_responses}
}