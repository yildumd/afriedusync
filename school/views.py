from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import School, TeacherProfile, ParentProfile, Student, LessonPlan, Club, Course, Assignment
from django import forms

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('Proprietor', 'Proprietor'),
        ('HeadTeacher', 'HeadTeacher'),
        ('ViceAdmin', 'Vice Admin'),
        ('ViceAcademics', 'Vice Academics'),
        ('Teacher', 'Teacher'),
        ('Parent', 'Parent'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    school = forms.ModelChoiceField(queryset=School.objects.all(), required=False)

    class Meta:
        model = UserCreationForm.Meta.model
        fields = UserCreationForm.Meta.fields + ('role', 'school')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            school = form.cleaned_data['school']
            group = Group.objects.get(name=role)
            user.groups.add(group)
            if role == 'Teacher':
                TeacherProfile.objects.create(user=user, school=school)
            elif role == 'Parent':
                ParentProfile.objects.create(user=user, school=school)
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

@login_required
def dashboard(request):
    user_groups = request.user.groups.values_list('name', flat=True)
    if 'Proprietor' in user_groups:
        return render(request, 'proprietor_dashboard.html')
    elif 'HeadTeacher' in user_groups:
        return render(request, 'headteacher_dashboard.html')
    elif 'ViceAdmin' in user_groups or 'ViceAcademics' in user_groups:
        return render(request, 'vice_dashboard.html')
    elif 'Teacher' in user_groups:
        return render(request, 'teacher_dashboard.html')
    elif 'Parent' in user_groups:
        return render(request, 'parent_dashboard.html')
    return render(request, 'home.html', {'user': request.user})

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['courses_taught']

@login_required
def teacher_profile(request):
    if 'Teacher' not in request.user.groups.values_list('name', flat=True):
        return redirect('dashboard')
    profile = TeacherProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Courses updated')
    else:
        form = TeacherProfileForm(instance=profile)
    return render(request, 'teacher_profile.html', {'form': form})

class LessonPlanForm(forms.ModelForm):
    class Meta:
        model = LessonPlan
        fields = ['title', 'objective', 'materials', 'activities']

@login_required
def submit_lesson_plan(request):
    if 'Teacher' not in request.user.groups.values_list('name', flat=True):
        return redirect('dashboard')
    profile = TeacherProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = LessonPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.teacher = request.user
            plan.school = profile.school
            plan.save()
            messages.success(request, 'Lesson plan submitted')
            return redirect('dashboard')
    else:
        form = LessonPlanForm()
    return render(request, 'lesson_plan.html', {'form': form})

@login_required
def parent_view_student(request):
    if 'Parent' not in request.user.groups.values_list('name', flat=True):
        return redirect('dashboard')
    profile = ParentProfile.objects.get(user=request.user)
    students = profile.students.filter(school=profile.school)
    assignments = Assignment.objects.filter(course__student__in=students, school=profile.school)
    return render(request, 'parent_view.html', {'students': students, 'assignments': assignments})

class LessonPlanApprovalForm(forms.ModelForm):
    rejection_reason = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = LessonPlan
        fields = ['approved', 'rejection_reason']

@login_required
def approve_lesson_plan(request):
    if 'HeadTeacher' not in request.user.groups.values_list('name', flat=True):
        return redirect('dashboard')
    lesson_plans = LessonPlan.objects.filter(school__in=TeacherProfile.objects.filter(user=request.user).values('school'))
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        plan = LessonPlan.objects.get(id=plan_id)
        form = LessonPlanApprovalForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lesson plan "{plan.title}" updated')
            return redirect('approve_lesson_plan')
    else:
        form = LessonPlanApprovalForm()
    return render(request, 'approve_lesson_plan.html', {'lesson_plans': lesson_plans, 'form': form})