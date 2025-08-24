from django.contrib import admin
from .models import TeacherProfile, ParentProfile, Student, LessonPlan

admin.site.register(TeacherProfile)
admin.site.register(ParentProfile)
admin.site.register(Student)
admin.site.register(LessonPlan)