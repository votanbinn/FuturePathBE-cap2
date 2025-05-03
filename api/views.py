from django.http import HttpResponse
from . import models
from . import serializers
import os
from dotenv import load_dotenv
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404

def running(request):
    return HttpResponse("App is running")

load_dotenv()  # Tải biến môi trường từ file .env

# Lấy giá trị từ biến môi trường
access_token = os.getenv('ACCESS_TOKEN')

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Kiểm tra thông tin đầu vào
        if not email or not password:
            return Response({"error": "Email và mật khẩu là bắt buộc"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Tìm người dùng qua email
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            raise AuthenticationFailed("Tài khoản không tồn tại")

        # Kiểm tra mật khẩu bằng Django
        if not check_password(password, user.password):
            raise AuthenticationFailed("Sai mật khẩu")

        # Lấy vai trò người dùng
        try:
            user_role = models.UserRole.objects.get(user=user)
            role = models.Role.objects.get(id=user_role.role.id)
        except (models.UserRole.DoesNotExist, models.Role.DoesNotExist):
            raise AuthenticationFailed("Không tìm thấy vai trò")

        # Tạo token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Lưu token vào session
        request.session['access_token'] = access_token

        # Chuẩn bị dữ liệu trả về
        user_response = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": role.name
        }

        # Trả về thông tin người dùng và thông báo đăng nhập thành công
        return Response({
            "success": True,
            "message": "Đăng nhập thành công",
            "user": user_response,
            "expiresIn": 3600  # Token hết hạn sau 1 tiếng
        }, status=status.HTTP_200_OK)
    
    
class AddUserView(APIView):
    def post(self, request):
        serializer = serializers.UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully", "user_id": user.id}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteUserView(APIView):
    def delete(self, request, user_id):
        role_name = request.data.get('role_name')
        if not role_name:
            return Response({"error": "Thiếu role_name"}, status=status.HTTP_400_BAD_REQUEST)

        if role_name != 'admin':
            return Response({"error": "Bạn không có quyền xóa user"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_to_delete = models.User.objects.get(id=user_id)
            user_to_delete.delete()
            return Response({"message": f"User với ID {user_id} đã được xóa thành công"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "Không tìm thấy user cần xóa"}, status=status.HTTP_404_NOT_FOUND)


class UpdateUserView(APIView):
    def put(self, request, user_id):
        role_name = request.data.get('role_name')
        if not role_name:
            return Response({"error": "Thiếu role_name"}, status=status.HTTP_400_BAD_REQUEST)

        if role_name != 'admin':
            return Response({"error": "Bạn không có quyền cập nhật user"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_to_update = models.User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return Response({"error": "Không tìm thấy user cần cập nhật"}, status=status.HTTP_404_NOT_FOUND)

        # Update các trường username, email, password nếu có
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if username:
            user_to_update.username = username
        if email:
            user_to_update.email = email
        if password:
            from django.contrib.auth.hashers import make_password
            user_to_update.password = make_password(password)  # Mã hóa password luôn cho an toàn

        user_to_update.save()

        return Response({"message": f"User với ID {user_id} đã được cập nhật thành công"}, status=status.HTTP_200_OK)
        
class TakeQuizView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user')
        quiz_answers = data.get('answers')

        if not user_id or not quiz_answers:
            return Response({
                "error": "Missing required fields: user, answers"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if not isinstance(quiz_answers, dict):
            return Response({"error": "Answers must be a dictionary"}, status=status.HTTP_400_BAD_REQUEST)

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

        for quiz_id, answer in quiz_answers.items():
            try:
                quiz = models.Quiz.objects.get(id=quiz_id)
            except models.Quiz.DoesNotExist:
                return Response({"error": f"Quiz with id {quiz_id} not found."}, status=status.HTTP_404_NOT_FOUND)

            result_data['quiz_type'] = quiz.quiz_type

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

            sorted_mbti_scores = sorted(mbti_scores.items(), key=lambda x: x[1], reverse=True)

            result_data['result'] = ''.join([x[0] for x in sorted_mbti_scores[:4]])

        elif result_data['quiz_type'] == "Holland":
            holland_scores = {
                "R": result_data['R_score'],
                "I": result_data['I_score_h'],
                "A": result_data['A_score_h'],
                "S": result_data['S_score_h'],
                "E": result_data['E_score_h'],
                "C": result_data['C_score_h']
            }

            sorted_holland_scores = sorted(holland_scores.items(), key=lambda x: x[1], reverse=True)

            result_data['result'] = ''.join([x[0] for x in sorted_holland_scores[:2]])

        if result_data['quiz_type'] == "MBTI":
            quiz_id = 1
        elif result_data['quiz_type'] == "Holland":
            quiz_id = 61
        else:
            quiz_id = None

        quiz_result = models.QuizResult.objects.create(
            user=user,
            quiz_id=quiz_id,
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
        
from firebase_init import initialize_firebase
from firebase_admin import db
from django.utils.timezone import now

initialize_firebase()

class ForumPostView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        title = data.get('title')
        content = data.get('content')

        if not user_id or not title or not content:
            return Response({"error": "User ID, title, and content are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Lấy role đầu tiên của user từ bảng UserRole
        user_role = models.UserRole.objects.filter(user=user).first()
        role_name = user_role.role.name if user_role else "unknown"

        # Lưu bài post vào database
        post = models.ForumPost.objects.create(
            user=user, title=title, content=content, created_at=now()
        )

        # Dữ liệu gửi lên Firebase
        post_data = {
            'post_id': post.id,
            'user_id': user.id,
            'user_name': user.username,
            'role': role_name,
            'title': title,
            'content': content,
            'created_at': post.created_at.isoformat(),
        }

        # Gửi lên Firebase
        ref = db.reference('forum_posts')
        ref.push(post_data)

        # Dữ liệu trả về cho client
        return Response({
            "success": True,
            "data": post_data
        }, status=status.HTTP_201_CREATED)

    
class CommentCreateView(APIView):
    def post(self, request, post_id):
        data = request.data
        user_id = data.get('user_id')
        content = data.get('content')

        if not user_id or not content:
            return Response({"error": "Missing user_id or content"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            post = models.ForumPost.objects.get(id=post_id)
        except models.ForumPost.DoesNotExist:
            return Response({"error": "Forum post not found"}, status=status.HTTP_404_NOT_FOUND)

        comment = models.Comment.objects.create(post=post, user=user, content=content)

        # Push comment data to Firebase in a separate node "comments"
        ref = db.reference('comments')  # Node riêng cho comment
        comment_data = {
            'user_id': user.id,
            'post_id': post.id,
            'content': content,
            'created_at': comment.created_at.isoformat(),
        }

        # Push data to Firebase Realtime Database under the "comments" node
        comment_ref = ref.push(comment_data)

        return Response({
            "message": "Comment created successfully",
            "comment_id": comment.id
        }, status=status.HTTP_201_CREATED)
        
class CreateUserInformationView(APIView):
    def post(self, request):
        serializer = serializers.UserInformationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateUserInformationView(APIView):
    def put(self, request, pk):
        info = get_object_or_404(models.UserInformation, pk=pk)
        serializer = serializers.UserInformationSerializer(info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteUserInformationView(APIView):
    def delete(self, request, pk):
        info = get_object_or_404(models.UserInformation, pk=pk)
        info.delete()
        return Response({"message": "Xóa thành công."}, status=status.HTTP_204_NO_CONTENT)

class CreateConsultationView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        expert_id = data.get('expert_id')
        schedule_id = data.get('schedule_id')
        reason = data.get('reason', '')

        if not user_id or not expert_id or not schedule_id:
            return Response({"error": "Missing user_id, expert_id or schedule_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            expert = models.ExpertInformation.objects.get(id=expert_id)
        except models.ExpertInformation.DoesNotExist:
            return Response({"error": "Expert not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            schedule = models.ConsultantSchedule.objects.get(id=schedule_id)
        except models.ConsultantSchedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)

        consultation = models.Consultation.objects.create(
            user=user,
            expert=expert,
            schedule=schedule,
            reason=reason
        )

        return Response({
            "message": "Consultation created successfully",
            "consultation_id": consultation.id
        }, status=status.HTTP_201_CREATED)
        
class UpdateConsultationView(APIView):
    def put(self, request, pk):
        try:
            consultation = models.Consultation.objects.get(id=pk)
        except models.Consultation.DoesNotExist:
            return Response({"error": "Consultation not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        expert_id = data.get('expert_id')
        schedule_id = data.get('schedule_id')
        reason = data.get('reason', consultation.reason)
        is_confirmed = data.get('is_confirmed', consultation.is_confirmed)

        if expert_id:
            try:
                expert = models.ExpertInformation.objects.get(id=expert_id)
                consultation.expert = expert
            except models.ExpertInformation.DoesNotExist:
                return Response({"error": "Expert not found"}, status=status.HTTP_404_NOT_FOUND)

        if schedule_id:
            try:
                schedule = models.ConsultantSchedule.objects.get(id=schedule_id)
                consultation.schedule = schedule
            except models.ConsultantSchedule.DoesNotExist:
                return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)

        consultation.reason = reason
        consultation.is_confirmed = is_confirmed
        consultation.save()

        return Response({
            "message": "Consultation updated successfully",
            "consultation_id": consultation.id
        }, status=status.HTTP_200_OK)
        
class DeleteConsultationView(APIView):
    def delete(self, request, pk):
        try:
            consultation = models.Consultation.objects.get(id=pk)
        except models.Consultation.DoesNotExist:
            return Response({"error": "Consultation not found"}, status=status.HTTP_404_NOT_FOUND)

        consultation.delete()

        return Response({"message": "Consultation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
class ChatMessageView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        expert_id = data.get('expert_id')
        sender_type = data.get('sender_type')
        message = data.get('message')

        # Kiểm tra dữ liệu đầu vào
        if not user_id or not expert_id or not sender_type or not message:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Lấy user và expert từ cơ sở dữ liệu
        try:
            user = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            expert = models.ExpertInformation.objects.get(id=expert_id)
        except models.ExpertInformation.DoesNotExist:
            return Response({"error": "Expert not found."}, status=status.HTTP_404_NOT_FOUND)

        # Lưu tin nhắn vào cơ sở dữ liệu Django
        chat_message = models.ChatMessage.objects.create(
            user=user,
            expert=expert,
            sender_type=sender_type,
            message=message,
            timestamp=now()
        )

        # Cập nhật Firebase Realtime Database
        ref = db.reference('chat_messages')
        message_data = {
            'user_id': user.id,
            'expert_id': expert.id,
            'sender_type': sender_type,
            'message': message,
            'timestamp': chat_message.timestamp.isoformat(),
        }

        # Push dữ liệu lên Firebase
        firebase_message_ref = ref.push(message_data)
        
        # Cập nhật ID Firebase vào Django
        chat_message.firebase_message_id = firebase_message_ref.key
        chat_message.save()

        # Serialize dữ liệu trả về
        serializer = serializers.ChatMessageSerializer(chat_message)

        return Response({
            "message": "Chat message sent successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
class ChatHistoryView(APIView):
    def get(self, request, user_id, expert_id):
        messages = models.ChatMessage.objects.filter(user_id=user_id, expert_id=expert_id).order_by('timestamp')
        serializer = serializers.ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
class ExpertInformationDetailView(APIView):
    def get(self, request, expert_id):
        try:
            expert = models.ExpertInformation.objects.get(id=expert_id)
        except models.ExpertInformation.DoesNotExist:
            return Response({"error": "Expert not found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize dữ liệu của chuyên gia
        serializer = serializers.ExpertInformationSerializer(expert)

        return Response({"expert": serializer.data}, status=status.HTTP_200_OK)
    
class CreateTransactionView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        expert_id = request.data.get('expert_id')

        if not user_id or not expert_id:
            return Response({"error": "Missing user_id or expert_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = models.User.objects.get(id=user_id)
            expert = models.ExpertInformation.objects.get(id=expert_id)
        except models.User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.ExpertInformation.DoesNotExist:
            return Response({"error": "Expert not found"}, status=status.HTTP_404_NOT_FOUND)

        # Tạo giao dịch với status mặc định là "từ chối" hoặc "hoàn thành" tùy ý
        transaction = models.Transaction.objects.create(
            user=user,
            expert=expert,
            amount=100000.00,
            transaction_status='reject'  # hoặc 'hoàn thành' nếu bạn muốn
        )

        return Response({
            "message": "Transaction created with status 'reject'",
            "transaction_id": transaction.id
        }, status=status.HTTP_201_CREATED)
        
class ConfirmTransactionView(APIView):
    def post(self, request, transaction_id):
        try:
            transaction = models.Transaction.objects.get(id=transaction_id)
        except models.Transaction.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

        if transaction.transaction_status == 'complete':
            return Response({"message": "Transaction already confirmed"}, status=status.HTTP_400_BAD_REQUEST)

        transaction.transaction_status = 'complete'
        transaction.save()

        return Response({"message": "Transaction confirmed successfully"}, status=status.HTTP_200_OK)
    
