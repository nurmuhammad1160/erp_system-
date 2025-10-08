from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Homework, HomeworkSubmission
from courses.models import Course, Group
from accounts.models import StudentProfile
from .models import LessonSchedule
from django.contrib.auth.models import User



# =======================================================================================
# ==============================STUDENT=VIEWS=START======================================
# =======================================================================================


def dashboard(request):
    """dashboard of the student acts like a homepage for a student
       gives all the information related to student """
    student = get_object_or_404(StudentProfile, user=request.user)

    groups = student.groups.all()
    courses = Course.objects.filter(groups__students=student).distinct()
    homeworks = Homework.objects.filter(group__students=student).distinct()
    schedules = LessonSchedule.objects.filter(group__students=student).distinct()
    context = {
        'homeworks': homeworks,
        'courses': courses,
        'students': student,
        'groups': groups,
        'schedules': schedules,
    }

    return render(request, 'student/dashboard.html', context)


def courses(request):
    """a list of courses that student have"""
    student = get_object_or_404(StudentProfile, user=request.user)
    courses = Course.objects.filter(groups__students=student).distinct()
    context = {
        'courses': courses,
        }
    return render(request, 'student/courses.html', context)


def grades(request):
    """returnes a homeworks student uploaded with every field included scores"""
    student = get_object_or_404(StudentProfile, user=request.user)
    courses = Course.objects.filter(groups__students=student).distinct()
    homeworksubs = HomeworkSubmission.objects.filter(group__students=student).distinct()

    context = {
        'courses': courses,
        'homeworksubs': homeworksubs, #contains grades in scores field

    }


def homework(request, pk):
    """this function  is used to show the selected homework and upload the homework with file.
       checks the homework wether done or note and sends corresponding responce"""
    student = get_object_or_404(StudentProfile, user=request.user)
    homework = get_object_or_404(Homework, pk=pk)

    existing_submission = HomeworkSubmission.objects.filter(
        homework=homework,
        student=student
    ).first()

    if request.method == 'POST' and not existing_submission:
        existing_submission = HomeworkSubmission.objects.create(
            homework=homework,
            student=student,
            file=request.FILES.get('file'),
            text=request.POST.get('text', ''),
        )

    context = {
        'student': student.user,
        'homework': homework,
        'submission': existing_submission,  # pass to template
    }
    return render(request, 'student/homework.html', context)


def profile(request):
    """this function is used to show the student profile page and can edit partialy or fully"""
    student = get_object_or_404(StudentProfile, user=request.user)
    additional_info = User.objects.get(student_profile=student)
    context = {
        'student': student,
        'additional_info': additional_info,
    }
    return render(request, 'student/profile.html', context)


# =======================================================================================
# ==============================STUDENT=VIEWS=END========================================
# =======================================================================================



