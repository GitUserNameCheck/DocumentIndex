from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth_api
from app.api import document_api
from app.core.config import config
from app.core.logging import setup_logging
from app.db.schema import Base, engine

setup_logging()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=config.app_name)

origins = [
    config.frontend_origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_api.router, prefix="/api", tags=["auth"])
app.include_router(document_api.router, prefix="/api", tags=["document"])