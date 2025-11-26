import logging
import os
from fastapi import APIRouter, HTTPException, status, UploadFile
from fastapi.concurrency import run_in_threadpool
from uuid import uuid4

from app.core.magika import magika
from app.services.auth_service import AuthUserData
from app.services.document_service import pager_process_document, s3_get_all_documents, s3_upload_document, s3_delete_document
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
async def upload_document(user_data: AuthUserData, db: DbSession, file: UploadFile | None = None):

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

    content = await file.read()

    identifier = await run_in_threadpool(magika.identify_bytes, content)
    mime_type = identifier.output.mime_type
    filename = os.path.splitext(file.filename)[0]

    if mime_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {mime_type}. Supported types are {SUPPORTED_FILE_TYPES}."
        )
    
    document_uuid = uuid4()

    await s3_upload_document(content, str(document_uuid), SUPPORTED_FILE_TYPES[mime_type], filename, user_data, db)

    return {"message": "file uploaded successfuly"}


@router.post("/delete")
async def delete_document(id: int, user_data: AuthUserData, db: DbSession):
    document = db.query(Document).filter(Document.id == id).first()
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

    await s3_delete_document(document, user_data, db)

    return {"message": "file successfuly deleted"}

@router.get("/all")
async def get_all_documents(user_data: AuthUserData, db: DbSession):

    urls = await s3_get_all_documents(user_data, db)

    return {"message": "file successfuly deleted", "urls": urls}


@router.post("/process")
async def process_document(id: int, user_data: AuthUserData, db: DbSession):
    document = db.query(Document).filter(Document.id == id).first()
    if document.owner_id != user_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This file is not yours"
    )
    # if document.status == DocumentStatus.PROCESSED.value:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="Document is already processed"
    #     )
    # if document.status == DocumentStatus.PROCESSING.value:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="Document is already being processed"
    #     )

    await pager_process_document(document, user_data, db)

    return {"message": "document successfuly processed"}