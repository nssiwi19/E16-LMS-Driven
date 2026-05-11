import os
import sys

# Thêm thư mục hiện tại vào sys.path để pytest tìm thấy e16_app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
