# -*- coding: utf-8 -*-
from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from e16_app import create_app
from e16_app.services.storage import LocalStorage


@pytest.fixture
def app(tmp_path):
    app = create_app()
    app.config.update({"TESTING": True})
    app.static_folder = str(tmp_path)
    with app.app_context():
        yield app


def test_local_storage_rejects_disallowed_extension(app):
    storage = LocalStorage()
    file = FileStorage(stream=BytesIO(b"bad"), filename="payload.exe", content_type="application/octet-stream")

    with pytest.raises(ValueError, match="Định dạng file không được hỗ trợ"):
        storage.save_file(file, "assignments")


def test_local_storage_accepts_allowed_extension_with_magic(app):
    storage = LocalStorage()
    # Notes.pdf must start with %PDF magic bytes
    file = FileStorage(stream=BytesIO(b"%PDF-1.5\nhello"), filename="notes.pdf", content_type="application/pdf")

    saved_path = storage.save_file(file, "assignments")

    assert saved_path.startswith("assignments/")
    assert saved_path.endswith(".pdf")


def test_local_storage_rejects_spoofed_extension_magic_mismatch(app):
    storage = LocalStorage()
    # evil.pdf but actually starts with plain text "hello" instead of %PDF
    file = FileStorage(stream=BytesIO(b"hello world"), filename="evil.pdf", content_type="application/pdf")

    with pytest.raises(ValueError, match="Nội dung file thực tế không khớp với phần mở rộng tệp"):
        storage.save_file(file, "assignments")


def test_local_storage_rejects_spoofed_mime_type(app):
    storage = LocalStorage()
    # notes.pdf has correct %PDF header, but spoofed MIME type "image/png"
    file = FileStorage(stream=BytesIO(b"%PDF-1.5\nhello"), filename="notes.pdf", content_type="image/png")

    with pytest.raises(ValueError, match="MIME type không khớp với định dạng file"):
        storage.save_file(file, "assignments")


def test_local_storage_accepts_txt_without_null_bytes(app):
    storage = LocalStorage()
    file = FileStorage(stream=BytesIO(b"plain text document"), filename="notes.txt", content_type="text/plain")

    saved_path = storage.save_file(file, "assignments")
    assert saved_path.endswith(".txt")


def test_local_storage_rejects_txt_with_null_bytes(app):
    storage = LocalStorage()
    file = FileStorage(stream=BytesIO(b"some text\x00with null bytes"), filename="notes.txt", content_type="text/plain")

    with pytest.raises(ValueError, match="File văn bản chứa ký tự không hợp lệ"):
        storage.save_file(file, "assignments")
