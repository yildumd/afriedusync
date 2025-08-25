from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import School, TeacherProfile, ParentProfile, Student, LessonPlan, Club, Course, Assignment
from django import forms
from django.contrib.auth.models import User

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
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'school')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()
            
            role = form.cleaned_data['role']
            school = form.cleaned_data['school']
            
            # Add user to appropriate group
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)
            
            # Create appropriate profile
            if role == 'Teacher':
                TeacherProfile.objects.create(user=user, school=school)
            elif role == 'Parent':
                ParentProfile.objects.create(user=user, school=school)
            
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'login.html')

def logout_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You have been logged out successfully.')
    logout(request)
    return redirect('landing')

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

@login_required
def dashboard(request):
    """Main dashboard that redirects to role-specific dashboards"""
    user_groups = request.user.groups.values_list('name', flat=True)
    
    if 'Proprietor' in user_groups:
        return redirect('proprietor_dashboard')
    elif 'HeadTeacher' in user_groups:
        return redirect('headteacher_dashboard')
    elif 'ViceAdmin' in user_groups:
        return redirect('vice_dashboard')
    elif 'ViceAcademics' in user_groups:
        return redirect('vice_dashboard')
    elif 'Teacher' in user_groups:
        return redirect('teacher_dashboard')
    elif 'Parent' in user_groups:
        return redirect('parent_dashboard')
    
    # Fallback for users without specific roles
    return render(request, 'home.html', {'user': request.user})

# Role-specific dashboard views
@login_required
def proprietor_dashboard(request):
    if not request.user.groups.filter(name='Proprietor').exists():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return render(request, 'proprietor_dashboard.html')

@login_required
def headteacher_dashboard(request):
    if not request.user.groups.filter(name='HeadTeacher').exists():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return render(request, 'headteacher_dashboard.html')

@login_required
def vice_dashboard(request):
    if not request.user.groups.filter(name__in=['ViceAdmin', 'ViceAcademics']).exists():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return render(request, 'vice_dashboard.html')

@login_required
def teacher_dashboard(request):
    if not request.user.groups.filter(name='Teacher').exists():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get teacher's profile and relevant data
    try:
        profile = TeacherProfile.objects.get(user=request.user)
        lesson_plans = LessonPlan.objects.filter(teacher=request.user).order_by('-created_at')[:5]
        pending_approvals = LessonPlan.objects.filter(teacher=request.user, approved=False).count()
    except TeacherProfile.DoesNotExist:
        profile = None
        lesson_plans = []
        pending_approvals = 0
    
    context = {
        'profile': profile,
        'lesson_plans': lesson_plans,
        'pending_approvals': pending_approvals,
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
def parent_dashboard(request):
    if not request.user.groups.filter(name='Parent').exists():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        profile = ParentProfile.objects.get(user=request.user)
        students = profile.students.all()
        recent_assignments = Assignment.objects.filter(
            course__student__in=students
        ).order_by('-due_date')[:5]
    except ParentProfile.DoesNotExist:
        profile = None
        students = []
        recent_assignments = []
    
    context = {
        'profile': profile,
        'students': students,
        'recent_assignments': recent_assignments,
    }
    return render(request, 'parent_dashboard.html', context)

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['courses_taught']
        widgets = {
            'courses_taught': forms.SelectMultiple(attrs={'class': 'w-full p-2 border rounded-lg'}),
        }

@login_required
def teacher_profile(request):
    if not request.user.groups.filter(name='Teacher').exists():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your courses have been updated successfully!')
            return redirect('teacher_profile')
    else:
        form = TeacherProfileForm(instance=profile)
    
    return render(request, 'teacher_profile.html', {'form': form, 'profile': profile})

class LessonPlanForm(forms.ModelForm):
    class Meta:
        model = LessonPlan
        fields = ['title', 'objective', 'materials', 'activities']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'objective': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg', 'rows': 3}),
            'materials': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg', 'rows': 3}),
            'activities': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg', 'rows': 5}),
        }

@login_required
def submit_lesson_plan(request):
    if not request.user.groups.filter(name='Teacher').exists():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LessonPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.teacher = request.user
            plan.school = profile.school
            plan.save()
            messages.success(request, 'Lesson plan submitted successfully! It is now pending approval.')
            return redirect('teacher_dashboard')
    else:
        form = LessonPlanForm()
    
    return render(request, 'lesson_plan.html', {'form': form})

@login_required
def parent_view_student(request):
    if not request.user.groups.filter(name='Parent').exists():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        profile = ParentProfile.objects.get(user=request.user)
        students = profile.students.all()
        assignments = Assignment.objects.filter(
            course__student__in=students
        ).order_by('-due_date')
    except ParentProfile.DoesNotExist:
        messages.error(request, 'Parent profile not found.')
        return redirect('dashboard')
    
    context = {
        'students': students,
        'assignments': assignments,
    }
    return render(request, 'parent_view.html', context)

class LessonPlanApprovalForm(forms.ModelForm):
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg', 'rows': 3, 'placeholder': 'Optional feedback for the teacher...'}),
        required=False
    )

    class Meta:
        model = LessonPlan
        fields = ['approved', 'rejection_reason']
        widgets = {
            'approved': forms.Select(choices=[(True, 'Approve'), (False, 'Reject')], attrs={'class': 'w-full p-2 border rounded-lg'}),
        }

@login_required
def approve_lesson_plan(request):
    if not request.user.groups.filter(name='HeadTeacher').exists():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    try:
        profile = TeacherProfile.objects.get(user=request.user)
        lesson_plans = LessonPlan.objects.filter(school=profile.school, approved=False).order_by('-created_at')
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        try:
            plan = LessonPlan.objects.get(id=plan_id, school=profile.school)
            form = LessonPlanApprovalForm(request.POST, instance=plan)
            if form.is_valid():
                form.save()
                action = "approved" if plan.approved else "rejected"
                messages.success(request, f'Lesson plan "{plan.title}" has been {action}.')
                return redirect('approve_lesson_plan')
        except LessonPlan.DoesNotExist:
            messages.error(request, 'Lesson plan not found.')
    
    else:
        form = LessonPlanApprovalForm()
    
    context = {
        'lesson_plans': lesson_plans,
        'form': form,
        'pending_count': lesson_plans.count(),
    }
    return render(request, 'approve_lesson_plan.html', context)