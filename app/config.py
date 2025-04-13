import os
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), ".env")

class Settings(BaseSettings):
    minio_server_address: str = "0.0.0.0"
    minio_access_key: str = "accesskey"
    minio_secret_key: str = "secretkey"
    minio_bucket_name: str = "whisperapi"
    minio_secure: bool = False

    model_config = SettingsConfigDict(env_file=DOTENV)
