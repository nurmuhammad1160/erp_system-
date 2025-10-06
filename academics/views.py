from django.shortcuts import render
from .models import Homework, HomeworkSubmission
from courses.models import Course, Group
from accounts.models import StudentProfile, User
# Create your views here.


def student_page(request):
    student = StudentProfile.objects.get(user=request.user)
    homeworks = Homework.objects.filter(group=student.group).order_by('-id')[:10]
    student_groups = Group.objects.filter(students=student)
    context = {
        'student': student.user,
        'student_groups' : student_groups,
        'homeworks': homeworks,
        'homework': homeworks[1] if homeworks else None,
        'courses': Course.objects.all(),
         }
    return render(request, 'StudentPage/student_page.html', context)


def student_homework(request, pk):
    student = StudentProfile.objects.get(user=request.user)
    homework = Homework.objects.get(pk=pk)

    context = {
        'student': student.user,
        'homework': homework,
    }
    if request.method == 'POST':
        HomeworkSubmission.objects.create(
            homework=homework,
            student=student,
            file=request.FILES['file'],
            text=request.POST['text'],

        )
        return render(request, 'StudentPage/homework.html', context)
    return render(request, 'StudentPage/homework.html', context)
