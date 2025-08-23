#!/usr/bin/env python3
"""
File chạy chính cho đồ án
Em tham khảo từ Flask tutorial và chỉnh sửa
"""

import os
import sys

# Thêm src vào path để import được
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.app_factory import create_app

def main():
    """Hàm chính để chạy app"""
    try:
        # Tạo Flask app
        app = create_app()
        
        # Chạy server
        print("🚀 Đang khởi động server...")
        print("📍 URL: http://127.0.0.1:5000")
        print("📖 API Info: http://127.0.0.1:5000/api")
        print("❤️ Health Check: http://127.0.0.1:5000/health")
        print("\n⚡ Nhấn Ctrl+C để dừng server")
        
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True  # Bật debug mode cho development
        )
        
    except Exception as e:
        print(f"❌ Lỗi khởi động server: {e}")
        print("💡 Hãy kiểm tra:")
        print("   - Đã cài đặt requirements.txt chưa?")
        print("   - Port 5000 có bị chiếm không?")
        print("   - Database có kết nối được không?")

if __name__ == "__main__":
    main()
