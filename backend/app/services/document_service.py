import logging
from io import BytesIO
from typing import List
from sqlalchemy.orm import Session

from app.db.schema import Document
from app.models.auth_models import UserData
from app.core.s3 import AWS_BUCKET, s3_client


async def s3_upload_document(content: bytes, s3_filename: str, s3_mime_type: str, user_filename: str, user_data: UserData, db: Session) -> None:
    logging.info(f"Uploading file {user_filename} to s3")
    s3_client.upload_fileobj(BytesIO(content), AWS_BUCKET, f"documents/{s3_filename}.{s3_mime_type}")
    document = Document(owner_id=user_data.user_id, name=user_filename, status="UPLOADED", s3_filename=s3_filename, s3_mime_type=s3_mime_type, report_id=None)
    db.add(document)
    db.commit()


async def s3_delete_document(document: Document, db: Session)  -> None:
    logging.info(f"Deleting file {document.name} from s3")
    s3_client.delete_object(Bucket=AWS_BUCKET, Key=f"documents/{document.s3_filename}.{document.s3_mime_type}")
    db.delete(document)
    db.commit()

async def s3_get_all_documents(documents: List[Document], db: Session, user_data: UserData) -> list[dict[str, str]]:
    logging.info(f"Receiving all documents for {user_data.username} from s3")
    urls = []
    for document in documents:
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": AWS_BUCKET, "Key": f"documents/{document.s3_filename}.{document.s3_mime_type}"},
            ExpiresIn=3600  # 1 hour
        )
        urls.append({"id": document.id,"key": f"{document.name}.{document.s3_mime_type}", "status": document.status, "url": url})
    return urls