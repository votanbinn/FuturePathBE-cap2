import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    if not firebase_admin._apps:  # Kiểm tra xem Firebase đã được khởi tạo chưa
        cred = credentials.Certificate('firebase-key.json')  # Đảm bảo đường dẫn đúng
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://futurepath-98ae6-default-rtdb.firebaseio.com/'  # URL Firebase của bạn
        })
