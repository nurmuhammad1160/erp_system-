from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model

from .models import Homework, HomeworkSubmission, LessonSchedule
from courses.models import Course, Group
from accounts.models import StudentProfile

User = get_user_model()


# =======================================================================================
# ============================== STUDENT VIEWS START ====================================
# =======================================================================================


@login_required
def dashboard(request):
    """Dashboard for the student — shows all related info"""
    student = get_object_or_404(StudentProfile, user=request.user)

    groups = student.groups.all()
    courses = Course.objects.filter(groups__students=student).distinct()
    homeworks = Homework.objects.filter(group__students=student).distinct()
    schedules = LessonSchedule.objects.filter(group__students=student).distinct()

    context = {
        'student': student,
        'groups': groups,
        'courses': courses,
        'homeworks': homeworks,
        'schedules': schedules,
    }
    #permission_classes = [StudentRequiredMixin]

    return render(request, 'student/dashboard.html', context)


@login_required
def courses(request):
    """List of courses for a student"""
    student = get_object_or_404(StudentProfile, user=request.user)
    courses = Course.objects.filter(groups__students=student).distinct()
    context = {'student': student, 'courses': courses}
    return render(request, 'student/courses.html', context)


@login_required
def grades(request):
    """Homeworks uploaded by the student with scores"""
    student = get_object_or_404(StudentProfile, user=request.user)
    courses = Course.objects.filter(groups__students=student).distinct()
    homeworksubs = HomeworkSubmission.objects.filter(student=student).select_related('homework')

    context = {
        'student': student,
        'courses': courses,
        'homeworksubs': homeworksubs,  # contains grades in scores field
    }
    return render(request, 'student/grades.html', context)


@login_required
def homework(request, pk):
    """Show a homework and allow student to upload a submission"""
    student = get_object_or_404(StudentProfile, user=request.user)
    homework = get_object_or_404(Homework, pk=pk)

    existing_submission = HomeworkSubmission.objects.filter(
        homework=homework, student=student
    ).first()

    if request.method == 'POST' and not existing_submission:
        HomeworkSubmission.objects.create(
            homework=homework,
            student=student,
            file=request.FILES.get('file'),
            text=request.POST.get('text', ''),
        )
        return redirect('student:homework', pk=homework.pk)

    context = {
        'student': student,
        'homework': homework,
        'submission': existing_submission,
    }
    return render(request, 'student/homework.html', context)


@login_required
def profile(request):
    """Show and edit the student profile"""
    student = get_object_or_404(StudentProfile, user=request.user)

    context = {
        'student': student,
        'user': student.user,  # you already have the linked user
    }
    return render(request, 'student/profile.html', context)


# =======================================================================================
# ============================== STUDENT VIEWS END ======================================
# =======================================================================================
