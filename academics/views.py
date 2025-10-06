from django.shortcuts import render
from .models import Homework, HomeworkSubmission
from courses.models import Course, Group
from accounts.models import StudentProfile, User
# Create your views here.

# ============STUDENT=UCHUN=VIEWLAR================================================

def courseslist(request):
    """this function will return a list of all courses and groups for the student"""
    student = StudentProfile.objects.get(user=request.user)
    groups = Group.objects.filter(studets = request.user)
    courses = Course.objects.filter(groups = groups)

    context = {
        'courses': courses,
        'groups': groups,
    }
    return render(request, 'student/courses.html', context)


def dashboard(request):
    """this function will return the dashboard of the student. contains the iformtion of the student"""
    student = StudentProfile.objects.get(user=request.user)
    homeworks = Homework.objects.filter(group=student.group).order_by('-id')
    student_groups = Group.objects.filter(students=student)

    context = {
        'homeworks': homeworks,
        'student_groups': student_groups,
        'student': student,
    }

    return render(request, 'student/dashboard.html', context)


def grades(request):
    """this function is used to render the grades page"""
    student = StudentProfile.objects.get(user=request.user)
    courses = Course.objects.filter(groups = student.group).order_by('-id')
    homeworks = HomeworkSubmission.objects.filter(homework=courses)
    context = {
        'homeworks': homeworks, #studentni baholarini homeworkning scores fieldidan olsa boladi HomeworkSubmission.score
        'courses': courses, #studentni kursalari
    }
    return render(request, 'student/grades.html', context)


def student_homework(request, pk):
    """this function  is used to show the selected homework and upload the homework with file.
    checks the homework wether done or note and sends corresponding responce"""
    student = StudentProfile.objects.get(user=request.user)
    homework = Homework.objects.get(pk=pk)

    # Check if already submitted
    existing_submission = HomeworkSubmission.objects.filter(
        homework=homework,
        student=student
    ).first()

    if request.method == 'POST' and not existing_submission:
        HomeworkSubmission.objects.create(
            homework=homework,
            student=student,
            file=request.FILES.get('file'),
            text=request.POST.get('text', ''),
        )
        # refresh submission info
        existing_submission = HomeworkSubmission.objects.get(homework=homework, student=student)

    context = {
        'student': student.user,
        'homework': homework,
        'submission': existing_submission,  # pass to template
    }
    return render(request, 'student/homework.html', context)


def student_profile(request):
    """Student can edit and see its own profile information."""
    student = StudentProfile.objects.get(user=request.user)
    email = student.user.email
    first_name = student.user.first_name
    last_name = student.user.last_name
    phone = student.user.phone
    avatar = student.user.avatar
    context = {
        'student': student.user,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'phone': phone,
        'avatar': avatar,
            }
    return render(request, 'student/student_page.html', context)


# ============STUDENT=UCHUN=VIEWLAR================================================





