from typing import Annotated
import boto3
from fastapi import Depends
from app.core.config import config
from botocore.client import Config

AWS_BUCKET = config.s3_bucket_name

s3_client = boto3.client(            
            "s3",
            endpoint_url=config.s3_url,
            aws_access_key_id=config.s3_login,
            aws_secret_access_key=config.s3_password,
            config=Config(signature_version="s3v4")
        )