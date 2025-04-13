import os
import traceback
from flask import Flask, render_template, request
from dotenv import load_dotenv
from service.gpt_service import suggest_career

# Load environment variables
load_dotenv()

app = Flask(__name__)

class CareerAdvisor:
    @staticmethod
    def get_error_details(error):
        error_messages = {
            "Lỗi xác thực API Key": "API Key không hợp lệ hoặc đã hết hạn.",
            "Vượt quá giới hạn request": "Đã vượt quá giới hạn yêu cầu. Vui lòng thử lại sau.",
            "Không thể kết nối đến OpenAI": "Không thể kết nối đến OpenAI. Vui lòng kiểm tra lại mạng.",
            "Yêu cầu không hợp lệ": "Yêu cầu gửi đến OpenAI không hợp lệ. Hãy kiểm tra dữ liệu đầu vào.",
            "Quá thời gian chờ phản hồi": "Yêu cầu mất quá nhiều thời gian. Hãy thử lại sau hoặc rút gọn dữ liệu."
        }
        for key, message in error_messages.items():
            if key in str(error):
                return message
        return f"Lỗi hệ thống: {str(error)}"

    @staticmethod
    def validate_inputs(mbti, holland, skills, interests):
        mbti = mbti.strip().upper()
        holland = holland.strip().upper()

        valid_mbti = set("EISNTFJP")
        valid_holland = set("RIASEC")

        if len(mbti) != 4 or any(c not in valid_mbti for c in mbti):
            return False, "MBTI phải gồm 4 ký tự hợp lệ (E, I, S, N, T, F, J, P)."

        if len(holland) != 2 or any(c not in valid_holland for c in holland):
            return False, "Holland phải gồm 2 ký tự hợp lệ (R, I, A, S, E, C)."

        if not skills.strip():
            return False, "Vui lòng nhập kỹ năng của bạn."
        if not interests.strip():
            return False, "Vui lòng nhập sở thích của bạn."

        return True, ""

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/career-result', methods=['POST'])
def career_result():
    try:
        # Lấy dữ liệu từ form
        mbti = request.form.get('mbti', '').strip()
        holland = request.form.get('holland', '').strip()
        skills = request.form.get('skills', '').strip()
        interests = request.form.get('interests', '').strip()

        app.logger.info(f"Data received: MBTI={mbti}, Holland={holland}")

        # Validate
        is_valid, msg = CareerAdvisor.validate_inputs(mbti, holland, skills, interests)
        if not is_valid:
            return render_template('error.html', message=msg), 400

        # Gọi GPT
        try:
            suggestion = suggest_career(mbti, holland, skills, interests)
        except Exception as e:
            app.logger.error(f"GPT Error: {str(e)}")
            return render_template('error.html', message=CareerAdvisor.get_error_details(e)), 500

        return render_template('result.html',
                               mbti=mbti,
                               holland=holland,
                               skills=skills,
                               interests=interests,
                               suggestion=suggestion)
    except Exception as e:
        error_trace = traceback.format_exc()
        app.logger.error(f"Unexpected Error: {str(e)}\n{error_trace}")
        return render_template('error.html',
                               message=f"Lỗi hệ thống: {str(e)}<br><pre>{error_trace}</pre>"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
