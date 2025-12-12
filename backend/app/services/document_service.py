import json
import logging
from io import BytesIO
from uuid import uuid4
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from types_boto3_s3.client import S3Client
from qdrant_client import AsyncQdrantClient
import httpx
from qdrant_client import models

from app.core.ml_models import ml_models
from app.db.schema import Document, Report
from app.models.auth_models import UserData
from app.core.s3 import AWS_BUCKET
from app.core.config import config
from app.core.qdrant import collection_name
from app.models.document_models import DocumentStatus
from app.services.report_service import process_report, s3_delete_report, s3_upload_report
from app.models.report_models import ReportJson

PRESIGNED_URLS_EXPIRATION_TIME_SECONDS = 3600 # 1 hour

def s3_upload_document(content: bytes, s3_filename: str, s3_mime_type: str, user_filename: str, user_data: UserData, s3_client: S3Client, db: Session) -> None:
    logging.info(f"Uploading file {user_filename}.{s3_mime_type} to s3 for user {user_data.user_id}")
    s3_client.upload_fileobj(Fileobj=BytesIO(content), Bucket=AWS_BUCKET, Key=f"documents/{s3_filename}.{s3_mime_type}")
    document = Document(owner_id=user_data.user_id, name=user_filename, status=DocumentStatus.UPLOADED.value, s3_filename=s3_filename, s3_mime_type=s3_mime_type, report_id=None)
    db.add(document)
    db.commit()


async def s3_delete_document(document: Document, user_data: UserData, qdrant_client: AsyncQdrantClient, s3_client: S3Client, db: Session)  -> None:
    logging.info(f"Starting deleting process for document {document.id} which is owned by user {user_data.user_id}")

    if document.report_id is not None:
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(
                        value=str(user_data.user_id),
                    ),
                ),
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(
                        value=document.id
                    )
                )
            ]
        )

        search = await qdrant_client.query_points(
            collection_name=collection_name,
            query_filter=filter_condition,
            limit=1,
            with_payload=False,
            with_vectors=False
        )

        if len(search.points) > 0:
            logging.info(f"Deleting vectors for report {document.report_id} which is owned by user {user_data.user_id}")
            await qdrant_client.delete(
                collection_name=collection_name,
                points_selector=filter_condition,
                wait=True
            )

        logging.info(f"Deleting report {document.report_id} which is owned by user {user_data.user_id}")
        await run_in_threadpool(s3_delete_report, document, s3_client, db)

    logging.info(f"Deleting document {document.id} from s3")
    await run_in_threadpool(s3_client.delete_object, Bucket=AWS_BUCKET, Key=f"documents/{document.s3_filename}.{document.s3_mime_type}")
    logging.info(f"Deleting document {document.id} from db")
    await run_in_threadpool(db.delete, document)
    await run_in_threadpool(db.commit)

def s3_get_documents(page: int, page_size: int, user_data: UserData, s3_client: S3Client, db: Session) -> list[dict[str, str]]:
    logging.info(f"Presigning documents urls for user {user_data.user_id} from s3")
    query = db.query(Document).filter(Document.owner_id == user_data.user_id)

    total_items = query.count()

    documents = (
        query.offset((page-1)*page_size)
        .limit(page_size)
        .all()
    )

    result = []
    for document in documents:
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": AWS_BUCKET, 
                "Key": f"documents/{document.s3_filename}.{document.s3_mime_type}",
                "ResponseContentType": "application/pdf",
                "ResponseContentDisposition": "inline"
            },
            ExpiresIn=PRESIGNED_URLS_EXPIRATION_TIME_SECONDS,
        )
        result.append({"id": document.id,"key": f"{document.name}.{document.s3_mime_type}", "status": document.status, "url": url})
        
    return {"page": page, "page_size": page_size, "total_items": total_items, "documents": result}

async def process_document(document: Document, user_data: UserData, qdrant_client: AsyncQdrantClient, s3_client: S3Client, db: Session):
    logging.info(f"Processing document {document.s3_filename}.{document.s3_mime_type} from s3 for user {user_data.user_id}")
    document.status = DocumentStatus.PROCESSING.value
    await run_in_threadpool(db.commit)
    try:
        if document.report_id is None:
            files = {
                "file": (
                    f"{document.s3_filename}.{document.s3_mime_type}",
                    await run_in_threadpool(s3_client.get_object(Bucket=AWS_BUCKET, Key=f"documents/{document.s3_filename}.{document.s3_mime_type}")["Body"].read),
                    f"application/{document.s3_mime_type}"
                )
            }

            data = {
                "process": '{"glam_rows": true}'
            }

            logging.info(f"Sending documents {document.s3_filename}.{document.s3_mime_type} to pager for user {user_data.user_id}")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(config.pager_url + "/", data=data, files=files)
                response.raise_for_status()

            report_uuid = uuid4()
            
            report = await run_in_threadpool(s3_upload_report, response.content, str(report_uuid), document, s3_client, db)

            report_obj = ReportJson.model_validate(response.json())

        else: 
            report = await run_in_threadpool(lambda: db.query(Report).filter(Report.id == document.report_id).first())

            # report = await run_in_threadpool(s3_client.get_object, Bucket=AWS_BUCKET, Key=f"reports/{report.s3_filename}.json")

            report_file = await run_in_threadpool(
                lambda: s3_client.get_object(
                    Bucket=AWS_BUCKET,
                    Key=f"reports/{report.s3_filename}.json"
                )["Body"].read()
            )

            data = await run_in_threadpool(json.loads, report_file)

            report_obj = ReportJson.model_validate(data)
        

        logging.info(f"Processing report {report.s3_filename}.json for user {user_data.user_id}")
        await process_report(report_obj, document.id, user_data.user_id, qdrant_client)

        document.status = DocumentStatus.PROCESSED.value
        await run_in_threadpool(db.commit)

    except Exception as e:
        await run_in_threadpool(db.rollback)
        logging.exception(f"Error while processing document {document.s3_filename}.{document.s3_mime_type} from s3 for user {user_data.user_id} \n {e}")
        document.status = DocumentStatus.PROCESSING_FAILED.value
        await run_in_threadpool(db.commit)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document processing failed"
        )
    
async def search_documents(text: str, label: str | None, user_data: UserData, qdrant_client: AsyncQdrantClient, s3_client: S3Client, db: Session) -> list[dict[str, str]]:
    logging.info(f"Searching documents for user {user_data.user_id} with string {text}")

    text = text.replace("-\n", "").replace("\n", " ").lower()
    
    embedding = await run_in_threadpool(ml_models["embedding_model"].encode, text)

    conditions = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(
                    value=str(user_data.user_id),
                ),
            ),
        ]
    
    if label is not None:
        conditions.append(
            models.FieldCondition(
                key="label",
                match=models.MatchValue(
                    value=label,
                ),
            )
        )

    filter_condition = models.Filter(
        must=conditions
    )

    result = await qdrant_client.query_points_groups(
        collection_name=collection_name,
        query_filter=filter_condition,
        query=embedding,
        group_by="document_id",
        group_size=1,
        limit=5,
        score_threshold=config.qdrant_distance_score_threshold
    )

    return result

    # documents_ids = []
    # for group in result.groups:
    #     documents_ids.append(group.hits[0].payload.get("document_id"))

    # logging.info(f"Presigning found documents urls for user {user_data.user_id} from s3")
    # documents = await run_in_threadpool(lambda: db.query(Document).filter(Document.id.in_(documents_ids)).all())
    # urls = []
    # for document in documents:
    #     url = s3_client.generate_presigned_url(
    #         ClientMethod="get_object",
    #         Params={"Bucket": AWS_BUCKET, "Key": f"documents/{document.s3_filename}.{document.s3_mime_type}"},
    #         ExpiresIn=PRESIGNED_URLS_EXPIRATION_TIME_SECONDS
    #     )
    #     urls.append({"id": document.id,"key": f"{document.name}.{document.s3_mime_type}", "status": document.status, "url": url})

    # return urls


