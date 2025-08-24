from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('profile/', views.teacher_profile, name='teacher_profile'),
    path('lesson-plan/', views.submit_lesson_plan, name='lesson_plan'),
    path('parent-view/', views.parent_view_student, name='parent_view'),
    path('approve-lesson-plan/', views.approve_lesson_plan, name='approve_lesson_plan'),
]