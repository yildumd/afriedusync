from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.teacher_profile, name='teacher_profile'),
    path('lesson-plan/', views.submit_lesson_plan, name='lesson_plan'),
    path('parent-view/', views.parent_view_student, name='parent_view'),
    path('approve-lesson-plan/', views.approve_lesson_plan, name='approve_lesson_plan'),
    
    # Add these dashboard-specific URLs for better routing
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('headteacher-dashboard/', views.headteacher_dashboard, name='headteacher_dashboard'),
    path('proprietor-dashboard/', views.proprietor_dashboard, name='proprietor_dashboard'),
    path('vice-dashboard/', views.vice_dashboard, name='vice_dashboard'),
    path('parent-dashboard/', views.parent_dashboard, name='parent_dashboard'),
]