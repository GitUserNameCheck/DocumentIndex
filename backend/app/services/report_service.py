from io import BytesIO
import logging
from fastapi.concurrency import run_in_threadpool
from uuid import uuid4
from sqlalchemy.orm import Session
from torch import Tensor
from app.core.ml_models import ml_models
from types_boto3_s3.client import S3Client
from app.db.schema import Document, Report
from app.core.s3 import AWS_BUCKET
from app.core.qdrant import QdrantClient, collection_name
from app.core.config import config
from qdrant_client.http import models
from app.models.report_models import ReportJson

def s3_upload_report(content: bytes, s3_filename: str, document: Document, s3_client: S3Client, db: Session) -> Report:
    logging.info(f"Creating report for document {document.s3_filename}.{document.s3_mime_type} from s3")
    s3_client.upload_fileobj(Fileobj=BytesIO(content), Bucket=AWS_BUCKET, Key=f"reports/{s3_filename}.json")
    report = Report(document_id = document.id, s3_filename = s3_filename)
    db.add(report)
    db.flush()
    document.report_id = report.id
    db.commit()
    return report

def s3_delete_report(document: Document, s3_client: S3Client, db: Session) -> Report:
    report = db.query(Report).filter(Report.id == document.report_id).first()
    logging.info(f"Deleting report {report.s3_filename} from s3 for document {report.document_id}")
    s3_client.delete_object(Bucket=AWS_BUCKET, Key=f"reports/{report.s3_filename}.json")
    document.report_id = None
    db.delete(report)
    db.commit()


async def process_report(report: ReportJson, document_id: int, user_id: int, qdrant_client: QdrantClient) -> None:
    
    text = await run_in_threadpool(prepare_text, report)
    
    chunks = await run_in_threadpool(chunk_text, text)

    embeddings = await run_in_threadpool(ml_models["embedding_model"].encode, chunks)

    points = await run_in_threadpool(get_points, chunks, embeddings, user_id, document_id)

    await qdrant_client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True
    )

def prepare_text(report: ReportJson) -> str:
    text = ""

    for page in report.pages:
        block_text = ""
        for block in page.blocks:
            block_text = block_text + block.text
            text = text + block.text

    text = text.replace("-\n", "")
    text = text.replace("\n", " ")

    return text

def chunk_text(text: str, chunk_size: int = config.embedding_text_size, overlap: int = config.embedding_text_overlap) -> list[str]:
    chunks = []
    text_len = len(text)
    start = 0

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        chunks.append(chunk)

        if end == text_len:
            break

        start = end - overlap

    return chunks

def get_points(chunks: list[str], embeddings: Tensor, user_id: int, document_id: int) -> list[models.PointStruct]:
    points = []
    for text, embedding in zip(chunks, embeddings):
        points.append(
            models.PointStruct(
                id = uuid4(),
                vector = embedding,
                payload = {
                    "user_id": str(user_id),
                    "document_id": document_id,
                    "text": text
                }
            )
        )

    return points