from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import logging

# Khởi tạo Flask app
app = Flask(__name__)
CORS(app)

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# Lấy API Key từ biến môi trường
openai.api_key = os.getenv("OPENAI_API_KEY")

# Mặc định dùng model gpt-3.5-turbo, có thể chỉnh sau này
DEFAULT_MODEL = "ft:gpt-3.5-turbo-0125:personal::BLnytmJ2"

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        user_message = request.json.get('message', '').strip()
        if not user_message:
            return jsonify({"reply": "Không có nội dung để xử lý."}), 400

        logging.info(f"User message: {user_message}")

        response = openai.ChatCompletion.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "Bạn là một chatbot tư vấn nghề nghiệp dễ thương, hài hước và thân thiện."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message['content'].strip()
        logging.info(f"Bot reply: {reply}")
        return jsonify({"reply": reply})

    except Exception as e:
        logging.error(f"Lỗi khi gọi OpenAI: {e}")
        return jsonify({"reply": "Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại sau 😥"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
