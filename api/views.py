from django.shortcuts import render
from django.http import HttpResponse
from . import models
from . import serializers
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from django.contrib.auth.hashers import check_password
import re

# Create your views here.
def running(request):
    return HttpResponse("App is running")

class LoginView(APIView):
    def post(self, request):
        # Sử dụng serializer để xác thực dữ liệu đầu vào
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            try:
                # Tìm kiếm người dùng bằng username
                user = models.User.objects.get(username=username)

                # Sử dụng check_password để xác minh mật khẩu đã mã hóa
                if check_password(password, user.password):
                    # Đăng nhập thành công, không cấp token mà chỉ trả về thông báo
                    return Response({
                        "message": "Đăng nhập thành công!"
                    }, status=status.HTTP_200_OK)
                else:
                    # Sai mật khẩu
                    return Response({"error": "Tên đăng nhập hoặc mật khẩu không chính xác."}, status=status.HTTP_401_UNAUTHORIZED)
            except models.User.DoesNotExist:
                # Sai tên đăng nhập
                return Response({"error": "Tên đăng nhập hoặc mật khẩu không chính xác."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class AddUserView(APIView):
    def post(self, request):
        # Kiểm tra dữ liệu
        serializer = serializers.UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully", "user_id": user.id}, status=status.HTTP_201_CREATED)
        
        # Nếu validation thất bại, trả về lỗi
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteUserView(APIView):
    def delete(self, request, user_id):
        try:
            user = models.User.objects.get(id=user_id)
            user.delete()
            return Response({"message": f"User with ID {user_id} deleted successfully"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
class UpdateUserView(APIView):
    def put(self, request, user_id):
        try:
            user = models.User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"User with ID {user_id} updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
class TakeQuizView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user')  # ID của người dùng
        quiz_answers = data.get('answers')  # Câu trả lời của người dùng

        # Kiểm tra nếu thiếu thông tin
        if not user_id or not quiz_answers:
            return Response({
                "error": "Missing required fields: user, answers"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra nếu câu trả lời không hợp lệ
        if not isinstance(quiz_answers, dict):
            return Response({"error": "Answers must be a dictionary"}, status=status.HTTP_400_BAD_REQUEST)

        # Tính toán điểm cho MBTI hoặc Holland
        result_data = {
            'E_score': 0,
            'I_score': 0,
            'S_score': 0,
            'N_score': 0,
            'T_score': 0,
            'F_score': 0,
            'J_score': 0,
            'P_score': 0,
            'R_score': 0,
            'I_score_h': 0,
            'A_score_h': 0,
            'S_score_h': 0,
            'E_score_h': 0,
            'C_score_h': 0,
            'result': '',
            'quiz_type': ''
        }

        # Lặp qua các câu trả lời và tính điểm
        for quiz_id, answer in quiz_answers.items():
            try:
                quiz = models.Quiz.objects.get(id=quiz_id)
            except models.Quiz.DoesNotExist:
                return Response({"error": f"Quiz with id {quiz_id} not found."}, status=status.HTTP_404_NOT_FOUND)

            # Thêm quiz_type vào kết quả
            result_data['quiz_type'] = quiz.quiz_type

            # Tính điểm tùy vào quiz loại
            if quiz.quiz_type == "MBTI":
                if answer == "E":
                    result_data['E_score'] += 1
                elif answer == "I":
                    result_data['I_score'] += 1
                elif answer == "S":
                    result_data['S_score'] += 1
                elif answer == "N":
                    result_data['N_score'] += 1
                elif answer == "T":
                    result_data['T_score'] += 1
                elif answer == "F":
                    result_data['F_score'] += 1
                elif answer == "J":
                    result_data['J_score'] += 1
                elif answer == "P":
                    result_data['P_score'] += 1

            elif quiz.quiz_type == "Holland":
                if answer == "R":
                    result_data['R_score'] += 1
                elif answer == "I":
                    result_data['I_score_h'] += 1
                elif answer == "A":
                    result_data['A_score_h'] += 1
                elif answer == "S":
                    result_data['S_score_h'] += 1
                elif answer == "E":
                    result_data['E_score_h'] += 1
                elif answer == "C":
                    result_data['C_score_h'] += 1

        # Tính ra kết quả cuối cùng cho MBTI - Lấy 4 nhóm cao nhất
        if result_data['quiz_type'] == "MBTI":
            mbti_scores = {
                "E": result_data['E_score'],
                "I": result_data['I_score'],
                "S": result_data['S_score'],
                "N": result_data['N_score'],
                "T": result_data['T_score'],
                "F": result_data['F_score'],
                "J": result_data['J_score'],
                "P": result_data['P_score']
            }

            # Sắp xếp theo điểm giảm dần
            sorted_mbti_scores = sorted(mbti_scores.items(), key=lambda x: x[1], reverse=True)

            # Lấy 4 nhóm cao nhất
            result_data['result'] = ''.join([x[0] for x in sorted_mbti_scores[:4]])

        # Tính ra kết quả cho Holland - Lấy 2 nhóm cao nhất
        elif result_data['quiz_type'] == "Holland":
            holland_scores = {
                "R": result_data['R_score'],
                "I": result_data['I_score_h'],
                "A": result_data['A_score_h'],
                "S": result_data['S_score_h'],
                "E": result_data['E_score_h'],
                "C": result_data['C_score_h']
            }

            # Sắp xếp theo điểm giảm dần
            sorted_holland_scores = sorted(holland_scores.items(), key=lambda x: x[1], reverse=True)

            # Lấy 2 nhóm cao nhất
            result_data['result'] = ''.join([x[0] for x in sorted_holland_scores[:2]])

        # Lưu kết quả vào database
        if result_data['quiz_type'] == "MBTI":
            quiz_id = 1  # Quiz MBTI luôn có quiz_id là 1
        elif result_data['quiz_type'] == "Holland":
            quiz_id = 61  # Quiz Holland luôn có quiz_id là 61
        else:
            quiz_id = None  # Hoặc xử lý trường hợp khác nếu cần

        # Lưu kết quả vào database
        quiz_result = models.QuizResult.objects.create(
            user=user,
            quiz_id=quiz_id,  # Đây chỉ là ví dụ, bạn có thể lưu nhiều bài quiz nếu cần
            E_score=result_data['E_score'],
            I_score=result_data['I_score'],
            S_score=result_data['S_score'],
            N_score=result_data['N_score'],
            T_score=result_data['T_score'],
            F_score=result_data['F_score'],
            J_score=result_data['J_score'],
            P_score=result_data['P_score'],
            R_score=result_data['R_score'],
            I_score_h=result_data['I_score_h'],
            A_score_h=result_data['A_score_h'],
            S_score_h=result_data['S_score_h'],
            E_score_h=result_data['E_score_h'],
            C_score_h=result_data['C_score_h'],
            result=result_data['result'],
            quiz_type=result_data['quiz_type']
        )

        # Trả về kết quả thành công
        return Response({
            "success": True,
            "data": {
                "id": quiz_result.id,
                "user_id": user.id,
                "quiz_id": quiz_result.quiz.id,
                "e_score": result_data['E_score'],
                "i_score": result_data['I_score'],
                "s_score": result_data['S_score'],
                "n_score": result_data['N_score'],
                "t_score": result_data['T_score'],
                "f_score": result_data['F_score'],
                "j_score": result_data['J_score'],
                "p_score": result_data['P_score'],
                "r_score": result_data['R_score'],
                "i_score_h": result_data['I_score_h'],
                "a_score_h": result_data['A_score_h'],
                "s_score_h": result_data['S_score_h'],
                "e_score_h": result_data['E_score_h'],
                "c_score_h": result_data['C_score_h'],
                "result": result_data['result'],
                "quiz_type": result_data['quiz_type']
            },
            "message": "Quiz result saved successfully"
        }, status=status.HTTP_201_CREATED)
