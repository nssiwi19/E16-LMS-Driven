import abc
import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename


# ---------- Abstract base ----------

class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def save_file(self, file, folder: str = "uploads") -> str:
        """Lưu file, trả về URL hoặc relative path để lưu vào DB."""

    @abc.abstractmethod
    def delete_file(self, file_path: str) -> None:
        """Xóa file theo path/key đã lưu."""

    @abc.abstractmethod
    def get_url(self, file_path: str) -> str:
        """Trả về URL public để render trong template."""


# ---------- Local backend (dùng ngay, không cần credential) ----------

class LocalStorage(BaseStorage):
    def save_file(self, file, folder: str = "uploads") -> str:
        if not file:
            return None
        ext = os.path.splitext(secure_filename(file.filename))[1].lower()
        unique_name = f"{uuid.uuid4()}{ext}"
        upload_path = os.path.join(current_app.static_folder, folder)
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, unique_name))
        return f"{folder}/{unique_name}"  # relative path

    def delete_file(self, file_path: str) -> None:
        if not file_path:
            return
        full = os.path.join(current_app.static_folder, file_path)
        if os.path.exists(full):
            os.remove(full)

    def get_url(self, file_path: str) -> str:
        from flask import url_for
        return url_for("static", filename=file_path)


# ---------- S3 backend (bật khi cần, không ảnh hưởng local dev) ----------

class S3Storage(BaseStorage):
    def __init__(self):
        import boto3
        self._bucket = os.environ["AWS_S3_BUCKET"]
        self._region = os.environ.get("AWS_S3_REGION", "ap-southeast-1")
        self._client = boto3.client(
            "s3",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=self._region,
        )

    def save_file(self, file, folder: str = "uploads") -> str:
        if not file:
            return None
        ext = os.path.splitext(secure_filename(file.filename))[1].lower()
        key = f"{folder}/{uuid.uuid4()}{ext}"
        self._client.upload_fileobj(
            file,
            self._bucket,
            key,
            ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
        )
        return key  # lưu key vào DB, không lưu full URL

    def delete_file(self, file_path: str) -> None:
        if not file_path:
            return
        self._client.delete_object(Bucket=self._bucket, Key=file_path)

    def get_url(self, file_path: str) -> str:
        return f"https://{self._bucket}.s3.{self._region}.amazonaws.com/{file_path}"


# ---------- Factory — đọc env var 1 lần lúc khởi động ----------

def _build_storage() -> BaseStorage:
    backend = os.getenv("STORAGE_BACKEND", "local").lower()
    if backend == "s3":
        return S3Storage()
    return LocalStorage()


# Singleton, import từ nơi khác: from ..services.storage import storage
storage = _build_storage()
