from io import BytesIO
import logging

from fastapi.concurrency import run_in_threadpool
from app.db.schema import Document, Report
from app.core.s3 import AWS_BUCKET, s3_client
from sqlalchemy.orm import Session

from app.models.report_models import ReportStatus

async def s3_upload_report(content: bytes, s3_filename: str, document: Document, db: Session) -> Report:
    logging.info(f"Creating report for document {document.s3_filename}.{document.s3_mime_type} from s3")
    await run_in_threadpool(s3_client.upload_fileobj, Fileobj=BytesIO(content), Bucket=AWS_BUCKET, Key=f"reports/{s3_filename}.json")
    report = Report(document_id = document.id, status = ReportStatus.CREATED.value, s3_filename = s3_filename)
    db.add(report)
    db.commit()
    return report

async def s3_delete_report(document: Document, db: Session) -> Report:
    report = db.query(Report).filter(Report.id == document.report_id).first()
    logging.info(f"Deleting report {report.s3_filename} from s3 for document {report.document_id}")
    await run_in_threadpool(s3_client.delete_object, Bucket=AWS_BUCKET, Key=f"reports/{report.s3_filename}.json")
    document.report_id = None
    db.delete(report)
    db.commit()
