from django.db import models
from django.contrib.auth.models import User

class School(models.Model):
    name = models.CharField(max_length=200)
    proprietor = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    courses_taught = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    students = models.ManyToManyField('Student', blank=True)

    def __str__(self):
        return self.user.username

class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=50)
    attendance = models.IntegerField(default=0)
    grades = models.TextField(blank=True)
    behavior_notes = models.TextField(blank=True)
    courses = models.ManyToManyField('Course', blank=True)
    clubs = models.ManyToManyField('Club', blank=True)

    def __str__(self):
        return self.name

class LessonPlan(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    objective = models.TextField()
    materials = models.TextField()
    activities = models.TextField()
    approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Club(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

class Course(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.name

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()

    def __str__(self):
        return self.title