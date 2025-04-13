from django.urls import path
from . import views

urlpatterns = [
    path('running/', views.running, name='running'),
    path('login/', views.LoginView.as_view(), name='check login'),
    path('AddUser/', views.AddUserView.as_view(), name='add user'),
    path('DeleteUser/<int:user_id>/', views.DeleteUserView.as_view(), name='delete user'),
    path('UpdateUser/<int:user_id>/', views.UpdateUserView.as_view(), name='update user'),
    path('quiz-result/', views.TakeQuizView.as_view(), name='test quiz'),
]