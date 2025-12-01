import logging
import os
from fastapi import APIRouter, HTTPException, status, UploadFile
from fastapi.concurrency import run_in_threadpool
from uuid import uuid4

from app.core.ml_models import ml_models
from app.core.s3 import S3Client
from app.core.qdrant import QdrantClient
from app.services.auth_service import AuthUserData
from app.services.document_service import search_documents as service_search_documents, process_document as service_process_document, s3_get_all_documents, s3_upload_document, s3_delete_document
from app.db.schema import DbSession, Document
from app.models.document_models import DocumentStatus

router = APIRouter(
    prefix="/document"
)

KB = 1024
MB = 1024 * KB

SUPPORTED_FILE_TYPES = {
    "application/pdf": "pdf"
}


@router.post("/upload")
def upload_document(user_data: AuthUserData, s3_client: S3Client, db: DbSession, file: UploadFile | None = None):

    if not file:
        logging.info(f"User with name {user_data.username} did not provide a file")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No file was provided",
        )
    
    # come up with something better cause it is cleary won't work cause file.size can be spoofed
    # maybe should do ASGI server content-length header validation and check here validated header
    # https://github.com/fastapi/fastapi/discussions/8167
    # maybe just read chunks till it exeeds limit
    if not 0 < file.size <= 40 * MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported max file size is 40 mb"
        )
    
    content = file.file.read()
    identifier = ml_models["magika"].identify_bytes(content)
    mime_type = identifier.output.mime_type
    filename = os.path.splitext(file.filename)[0]

    if mime_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {mime_type}. Supported types are {SUPPORTED_FILE_TYPES}."
        )
    
    document_uuid = uuid4()

    s3_upload_document(content, str(document_uuid), SUPPORTED_FILE_TYPES[mime_type], filename, user_data, s3_client, db)

    return {"message": "file uploaded successfuly"}


@router.post("/delete")
async def delete_document(id: int, user_data: AuthUserData, qdrant_client: QdrantClient, s3_client: S3Client, db: DbSession):
    document = await run_in_threadpool(lambda: db.query(Document).filter(Document.id == id).first())
    if document.owner_id != user_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This file is not yours"
        )
    if document.status == DocumentStatus.PROCESSING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is being processed"
        )

    await s3_delete_document(document, user_data, qdrant_client, s3_client, db)

    return {"message": "file successfuly deleted"}

@router.get("/all")
def get_all_documents(user_data: AuthUserData, s3_client: S3Client, db: DbSession):

    urls = s3_get_all_documents(user_data, s3_client, db)

    return {"urls": urls}


@router.post("/process")
async def process_document(id: int, user_data: AuthUserData, qdrant_client: QdrantClient, s3_client: S3Client,  db: DbSession):
    document = await run_in_threadpool(lambda: db.query(Document).filter(Document.id == id).first())
    if document.owner_id != user_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This file is not yours"
    )
    if document.status == DocumentStatus.PROCESSED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is already processed"
        )
    if document.status == DocumentStatus.PROCESSING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is already being processed"
        )

    await service_process_document(document, user_data, qdrant_client, s3_client, db)

    return {"message": "document successfuly processed"}


@router.get("/search_documents")
async def search_documents(text:str, user_data: AuthUserData, qdrant_client: QdrantClient, s3_client: S3Client, db: DbSession):

    # urls = await s3_get_all_documents(user_data, db)

    urls = await service_search_documents(text, user_data, qdrant_client, s3_client, db)

    return {"urls": urls}