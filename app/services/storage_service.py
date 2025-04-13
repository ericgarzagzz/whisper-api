from minio import Minio
from minio.error import S3Error
from app.config import Settings

def get_minio_client() -> Minio:
    settings = Settings()
    return Minio(
        settings.minio_server_address,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure
    )

def upload_file(file_path: str, bucket: str, object_name: str):
    try:
        client = get_minio_client()
        bucket_found = client.bucket_exists(bucket)
        if not bucket_found:
            client.make_bucket(bucket)

        client.fput_object(bucket, object_name, file_path)
    except S3Error as e:
        raise Exception(f"Error uploading file: {e}")


def download_file(bucket: str, object_name: str) -> bytes:
    try:
        client = get_minio_client()
        response = client.get_object(bucket, object_name)
        return response.read()
    except S3Error as e:
        raise Exception(f"Error downloading file: {e}")

def get_file(bucket: str, object_name: str):
    try:
        client = get_minio_client()
        response = client.get_object(bucket, object_name)
        return response
    except S3Error as e:
        raise Exception(f"Error streaming file: {e}")

def get_file_range(bucket: str, object_name: str, offset: int, length: int):
    try:
        client = get_minio_client()
        response = client.get_object(bucket, object_name, offset=offset, length=length)
        return response
    except S3Error as e:
        raise Exception(f"Error streaming file: {e}")


def stat_file(bucket: str, object_name: str):
    try:
        client = get_minio_client()
        response = client.stat_object(bucket, object_name)
        return response
    except S3Error as e:
        raise Exception(f"Error streaming file: {e}")
