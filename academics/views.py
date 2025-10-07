from django.shortcuts import render
from .models import Homework, HomeworkSubmission
from courses.models import Course, Group
from accounts.models import StudentProfile
from django.shortcuts import get_object_or_404
# Create your views here.

# ============STUDENT=UCHUN=VIEWLAR================================================

def courseslist(request):
    """this function will return a list of all courses and groups for the student"""
    student = get_object_or_404(StudentProfile, user=request.user)
    groups = Group.objects.filter(students = request.user)
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


    """Render the grades page for a student"""

    student = StudentProfile.objects.get(user=request.user)
    homeworksubmissions = HomeworkSubmission.objects.filter(student=student) #grades are included

    # Student courses
    groups = Group.objects.filter(students=request.user)
    courses = Course.objects.filter(groups=groups)
    homeworks = Homework.objects.filter(group=student.group).order_by('-id')

    context = {
        'courses': courses,  # student’s courses
        'submissions': homeworksubmissions,  # contains .score and .homework
        'homeworks': homeworks,
    }

    return render(request, 'student/grades.html', context)


def student_homework(request, pk):
    """this function  is used to show the selected homework and upload the homework with file.
    checks the homework wether done or note and sends corresponding responce"""
    student = get_object_or_404(StudentProfile, user=request.user)
    homework = get_object_or_404(Homework, pk=pk)

    # Check if already submitted
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


def student_profile(request):
    """Student can edit and see its own profile information."""
    student = StudentProfile.objects.get(user=request.user)
    context = {
        'student': student.user,

            }
    return render(request, 'student/student_page.html', context)


# ============STUDENT=UCHUN=VIEWLAR================================================





