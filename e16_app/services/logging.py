import os
from datetime import datetime
from supabase import create_client, Client
from flask import request, current_app

class SupabaseLogger:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if url and key:
            self.client: Client = create_client(url, key)
        else:
            self.client = None

    def log(self, action_type, user_id=None, user_email=None, resource_type=None, resource_id=None, metadata=None, status='success'):
        """
        Ghi log lên Supabase.
        """
        if not self.client:
            # Nếu chưa cấu hình Supabase, chỉ ghi ra console/log file
            current_app.logger.info(f"Log (No Supabase): {action_type} by {user_email}")
            return

        try:
            # Lấy IP của người dùng
            ip_address = request.remote_addr if request else None
            
            data = {
                "user_id": str(user_id) if user_id else None,
                "user_email": user_email,
                "action_type": action_type,
                "resource_type": resource_type,
                "resource_id": str(resource_id) if resource_id else None,
                "metadata": metadata or {},
                "ip_address": ip_address,
                "status": status,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.client.table("system_logs").insert(data).execute()
        except Exception as e:
            current_app.logger.error(f"Failed to push log to Supabase: {str(e)}")

# Singleton instance
logger = SupabaseLogger()
