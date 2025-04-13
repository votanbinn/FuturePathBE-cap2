from django.db import models

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'role']


class Quiz(models.Model):
    quiz_type = models.CharField(max_length=255, choices=[('MBTI', 'MBTI'), ('Holland', 'Holland')])
    content = models.CharField(max_length=255)
    option1 = models.CharField(max_length=225, null=True, blank=True)
    option2 = models.CharField(max_length=225, null=True, blank=True)
    category = models.CharField(max_length=255, choices=[('E/I', 'E/I'), ('S/N', 'S/N'), ('T/F', 'T/F'), 
                                                         ('J/P', 'J/P'), ('R/I', 'R/I'), ('A/S', 'A/S'), 
                                                         ('E/C', 'E/C')])

    def __str__(self):
        return self.content


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_type = models.CharField(max_length=255, default="default_quiz_type")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    E_score = models.IntegerField(null=True)
    I_score = models.IntegerField(null=True)
    S_score = models.IntegerField(null=True)
    N_score = models.IntegerField(null=True)
    T_score = models.IntegerField(null=True)
    F_score = models.IntegerField(null=True)
    J_score = models.IntegerField(null=True)
    P_score = models.IntegerField(null=True)
    R_score = models.IntegerField(null=True)
    I_score_h = models.IntegerField(null=True)
    A_score_h = models.IntegerField(null=True)
    S_score_h = models.IntegerField(null=True)
    E_score_h = models.IntegerField(null=True)
    C_score_h = models.IntegerField(null=True)
    result = models.CharField(max_length=20)

    def __str__(self):
        return f"QuizResult for {self.user.username}"


class UserAnswer(models.Model):
    quiz_result = models.ForeignKey(QuizResult, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    select_option = models.CharField(max_length=1, choices=[('a', 'Option A'), ('b', 'Option B')])
    category = models.CharField(max_length=255, choices=[('E/I', 'E/I'), ('S/N', 'S/N'), ('T/F', 'T/F'),
                                                         ('J/P', 'J/P'), ('R/I', 'R/I'), ('A/S', 'A/S'),
                                                         ('E/C', 'E/C')])

    def __str__(self):
        return f"Answer for {self.quiz_result}"


class ChatbotHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class ChatSystemHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ForumPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)


class BannedUserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    banned_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_status = models.CharField(max_length=10)


class RevenueManagement(models.Model):
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    report_date = models.DateTimeField(auto_now_add=True)


class ExpertInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expertise = models.CharField(max_length=255)
    experience_years = models.IntegerField()


class ConsultantSchedule(models.Model):
    expert = models.ForeignKey(ExpertInformation, on_delete=models.CASCADE)
    available_date = models.DateField()
    available_time = models.TimeField()


class ExpertWithdrawInformation(models.Model):
    expert = models.ForeignKey(ExpertInformation, on_delete=models.CASCADE)
    bank_account = models.CharField(max_length=255)
    withdraw_amount = models.DecimalField(max_digits=10, decimal_places=2)


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserProfileManagement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_data = models.TextField()


class ForumContentManagement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)