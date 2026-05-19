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

    with pytest.raises(ValueError):
        storage.save_file(file, "assignments")


def test_local_storage_accepts_allowed_extension(app):
    storage = LocalStorage()
    file = FileStorage(stream=BytesIO(b"hello"), filename="notes.pdf", content_type="application/pdf")

    saved_path = storage.save_file(file, "assignments")

    assert saved_path.startswith("assignments/")
    assert saved_path.endswith(".pdf")
