import logging
from io import BytesIO
from uuid import uuid4
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
import httpx
from sqlalchemy.orm import Session

from app.db.schema import Document
from app.models.auth_models import UserData
from app.core.s3 import AWS_BUCKET, s3_client
from app.core.config import config
from app.models.document_models import DocumentStatus
from app.services.report_service import process_report, s3_delete_report, s3_upload_report
from app.models.report_models import ReportJson

PRESIGNED_URLS_EXPIRATION_TIME_SECONDS = 3600 # 1 hour

async def s3_upload_document(content: bytes, s3_filename: str, s3_mime_type: str, user_filename: str, user_data: UserData, db: Session) -> None:
    logging.info(f"Uploading file {user_filename}.{s3_mime_type} to s3 for user {user_data.user_id}")
    await run_in_threadpool(s3_client.upload_fileobj, Fileobj=BytesIO(content), Bucket=AWS_BUCKET, Key=f"documents/{s3_filename}.{s3_mime_type}")
    document = Document(owner_id=user_data.user_id, name=user_filename, status=DocumentStatus.UPLOADED.value, s3_filename=s3_filename, s3_mime_type=s3_mime_type, report_id=None)
    db.add(document)
    db.commit()


async def s3_delete_document(document: Document, user_data: UserData, db: Session)  -> None:
    logging.info(f"Deleting file {document.name}.{document.s3_mime_type} from s3 which is owned by user {user_data.user_id}")
    if document.status == DocumentStatus.PROCESSED.value:
        await s3_delete_report(document=document, db=db)
    await run_in_threadpool(s3_client.delete_object, Bucket=AWS_BUCKET, Key=f"documents/{document.s3_filename}.{document.s3_mime_type}")
    db.delete(document)
    db.commit()

async def s3_get_all_documents(user_data: UserData,  db: Session) -> list[dict[str, str]]:
    logging.info(f"Presigning all documents urls for user {user_data.user_id} from s3")
    documents = db.query(Document).filter(Document.owner_id == user_data.user_id).all()
    urls = []
    for document in documents:
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": AWS_BUCKET, "Key": f"documents/{document.s3_filename}.{document.s3_mime_type}"},
            ExpiresIn=PRESIGNED_URLS_EXPIRATION_TIME_SECONDS
        )
        urls.append({"id": document.id,"key": f"{document.name}.{document.s3_mime_type}", "status": document.status, "url": url})
    return urls

async def pager_process_document(document: Document, user_data: UserData, db: Session):
    logging.info(f"Processing document {document.s3_filename}.{document.s3_mime_type} from s3 for user {user_data.user_id}")
    # document.status = DocumentStatus.PROCESSING.value
    # db.commit()
    try:

        files = {
            "file": (
                f"{document.s3_filename}.{document.s3_mime_type}",
                s3_client.get_object(Bucket=AWS_BUCKET, Key=f"documents/{document.s3_filename}.{document.s3_mime_type}")["Body"],
                f"application/{document.s3_mime_type}"
            )
        }

        data = {
            "process": '{"glam_rows": true}'
        }

        # maybe should call post with run_in_threadpool, not sure
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(config.pager_url + "/", data=data, files=files)

        # report_uuid = uuid4()
        
        # report = await s3_upload_report(content=response.content, s3_filename=str(report_uuid), document=document, db=db)

        report_obj = ReportJson.model_validate(response.json())
        
        await run_in_threadpool(process_report, report_obj, document.id, user_data.user_id)

        # document.status = DocumentStatus.PROCESSED.value
        # document.report_id = report.id
        # db.commit()

    except Exception as e:
        logging.exception(f"Error while processing document {document.s3_filename}.{document.s3_mime_type} from s3 for user {user_data.user_id} \n {e}")
        db.rollback()
        document.status = DocumentStatus.PROCESSING_FAILED.value
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document processing failed"
        )