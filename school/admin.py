from django.contrib import admin
from .models import School, TeacherProfile, ParentProfile, Student, LessonPlan, Club, Course, Assignment

admin.site.register(School)
admin.site.register(TeacherProfile)
admin.site.register(ParentProfile)
admin.site.register(Student)
admin.site.register(LessonPlan)
admin.site.register(Club)
admin.site.register(Course)
admin.site.register(Assignment)