import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

class StorageService:
    @staticmethod
    def save_file(file, folder="uploads"):
        """
        Saves a file and returns its relative path/URL.
        In a real production app, this would upload to S3/Cloud Storage.
        """
        if not file:
            return None
            
        filename = secure_filename(file.filename)
        # Add UUID to prevent collisions
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        
        upload_path = os.path.join(current_app.static_folder, folder)
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            
        file.save(os.path.join(upload_path, unique_filename))
        return f"{folder}/{unique_filename}"

    @staticmethod
    def delete_file(file_path):
        """Deletes a file from storage."""
        if not file_path:
            return
            
        full_path = os.path.join(current_app.static_folder, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
