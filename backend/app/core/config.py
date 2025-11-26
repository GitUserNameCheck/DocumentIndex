from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    app_name: str = "ScalableFastAPIProject"
    secret_key: str = "dev_secret"
    secure_cookie: bool = False
    frontend_origin: str = ""
    db_url: str = ""
    s3_bucket_name: str = ""
    s3_login: str = ""
    s3_password: str = ""
    s3_url: str = ""
    pager_url: str = ""
    embedding_model_path: str = ""

config = Config()