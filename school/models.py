# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses_taught = models.TextField(blank=True)  # e.g., "Math, Science"

    def __str__(self):
        return self.user.username

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    students = models.ManyToManyField('Student', blank=True)  # Parents can view multiple students

    def __str__(self):
        return self.user.username

class Student(models.Model):
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=50)  # e.g., "SS1"
    attendance = models.IntegerField(default=0)  # e.g., days attended
    grades = models.TextField(blank=True)  # e.g., "Math: 85, English: 90"
    behavior_notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

class LessonPlan(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    objective = models.TextField()
    materials = models.TextField()
    activities = models.TextField()
    approved = models.BooleanField(default=False)
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title