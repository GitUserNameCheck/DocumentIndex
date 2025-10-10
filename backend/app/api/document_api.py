import logging
import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from magika import Magika
from uuid import uuid4

from app.core.config import config
from app.docs.auth_docs import auth_responses
from app.models.auth_models import UserData
from app.services import auth_service
from app.services.document_service import s3_get_all_documents, s3_upload_document, s3_delete_document
from app.db.schema import DbSession, Document

router = APIRouter(
    prefix="/document"
)

KB = 1024
MB = 1024 * KB

SUPPORTED_FILE_TYPES = {
    "application/pdf": "pdf"
}


@router.post("/upload")
async def upload_document(user_data: Annotated[UserData, Depends(auth_service.get_current_user)], db: DbSession, file: UploadFile | None = None,):
    if not file:
        logging.info(f"User with name {user_data.username} did not provide a file")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No file was provided",
        )
    
    content = await file.read()
    size=file.size

    if not 0 < size <= 40 * MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported max file size is 40 mb"
        )
    
    m = Magika()
    identifier = m.identify_bytes(content)
    mime_type = identifier.output.mime_type
    filename = os.path.splitext(file.filename)[0]

    if mime_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {mime_type}. Supported types are {SUPPORTED_FILE_TYPES}."
        )
    
    await s3_upload_document(content, f"{uuid4()}", SUPPORTED_FILE_TYPES[mime_type], filename, user_data, db)

    return {"message": "file uploaded successfuly"}


@router.post("/delete")
async def delete_document(id: int, user_data: Annotated[UserData, Depends(auth_service.get_current_user)], db: DbSession):
    document = db.query(Document).filter(Document.id == id).first()
    if document.owner_id != user_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This file is not yours"
    )

    await s3_delete_document(document, db)

    return {"message": "file successfuly deleted"}

@router.get("/all")
async def get_all_documents(user_data: Annotated[UserData, Depends(auth_service.get_current_user)], db: DbSession):
    documents = db.query(Document).filter(Document.owner_id == user_data.user_id).all()

    urls = await s3_get_all_documents(documents, db, user_data)

    return {"message": "file successfuly deleted", "urls": urls}