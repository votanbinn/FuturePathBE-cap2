# firebase_config.py
from firebase_admin import db

def test_firebase_connection():
    try:
        # Khởi tạo Firebase (nếu chưa khởi tạo)
        from firebase_init import initialize_firebase
        initialize_firebase()

        # Thử lấy dữ liệu từ Firebase Realtime Database
        ref = db.reference('/')
        data = ref.get()
        
        if data is not None:
            print("Kết nối thành công và dữ liệu được lấy thành công!")
        else:
            print("Kết nối thành công nhưng không có dữ liệu.")
    
    except Exception as e:
        print(f"Lỗi khi kết nối với Firebase: {e}")
