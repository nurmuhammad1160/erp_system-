from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.views import View

from .models import Homework, HomeworkSubmission, LessonSchedule, Grades
from courses.models import Course, Group
from accounts.models import StudentProfile
# mixinlarni import qilamiz
from accounts.mixins import StudentRequiredMixin

User = get_user_model()


# =======================================================================================
# ============================== STUDENT VIEWS START ====================================
# =======================================================================================


class DashboardView(StudentRequiredMixin, View):
    """Dashboard for the student — shows all related info"""

    def get(self, request, *args, **kwargs):
        student = get_object_or_404(StudentProfile, user=request.user)

        # include both many-to-many membership (Group.students) and the student's primary group FK
        groups_qs = student.groups.all()
        if getattr(student, 'group', None):
            primary = student.group
            if primary and primary.pk and not groups_qs.filter(pk=primary.pk).exists():
                groups_qs = groups_qs | Group.objects.filter(pk=primary.pk)

        groups = groups_qs.distinct()
        courses = Course.objects.filter(groups__in=groups).distinct()
        homeworks = list(Homework.objects.filter(group__in=groups).distinct())
        # attach current student's submission (if any) to each homework for easy templating
        submissions = HomeworkSubmission.objects.filter(homework__in=homeworks, student=student).select_related('homework')
        submissions_map = {s.homework_id: s for s in submissions}
        for hw in homeworks:
            hw.submission = submissions_map.get(hw.pk)
        schedules = LessonSchedule.objects.filter(group__in=groups).distinct()

        context = {
            'student': student,
            'groups': groups,
            'courses': courses,
            'homeworks': homeworks,
            'schedules': schedules,
            'title': 'Dashboard',
        }
        return render(request, 'student/dashboard.html', context)


class CoursesView(StudentRequiredMixin, View):
    """List of courses for a student"""

    def get(self, request, *args, **kwargs):
        student = get_object_or_404(StudentProfile, user=request.user)
        groups_qs = student.groups.all()
        if getattr(student, 'group', None):
            primary = student.group
            if primary and primary.pk and not groups_qs.filter(pk=primary.pk).exists():
                groups_qs = groups_qs | Group.objects.filter(pk=primary.pk)

        groups = groups_qs.distinct()
        courses = Course.objects.filter(groups__in=groups).distinct()
        context = {'student': student, 'courses': courses, 'title': 'My Courses'}
        return render(request, 'student/courses.html', context)


class GradesView(StudentRequiredMixin, View):
    """Homeworks uploaded by the student with scores"""

    def get(self, request, *args, **kwargs):
        student = get_object_or_404(StudentProfile, user=request.user)
        groups_qs = student.groups.all()
        if getattr(student, 'group', None):
            primary = student.group
            if primary and primary.pk and not groups_qs.filter(pk=primary.pk).exists():
                groups_qs = groups_qs | Group.objects.filter(pk=primary.pk)

        groups = groups_qs.distinct()
        courses = Course.objects.filter(groups__in=groups).distinct()
        # fetch student submissions and any explicit Grades records
        submissions = HomeworkSubmission.objects.filter(student=student).select_related('homework__group', 'homework__group__course')
        explicit_grades = Grades.objects.filter(student=student).select_related('homework')

        # Build a per-course structure: { course: { assignments: [...], average: Decimal } }
        from collections import defaultdict
        from decimal import Decimal

        course_map = defaultdict(lambda: {'course': None, 'assignments': [], 'average': None})

        # include submissions (prefer per-submission score if present)
        for sub in submissions:
            course = getattr(getattr(sub, 'homework', None), 'group', None)
            course = getattr(course, 'course', None)
            key = course.pk if course else 'ungrouped'
            entry = course_map[key]
            entry['course'] = course
            score = sub.score if getattr(sub, 'score', None) is not None else None
            entry['assignments'].append({
                'title': getattr(getattr(sub, 'homework', None), 'title', 'Assignment'),
                'submitted_at': sub.submitted_at,
                'score': score,
                'submission': sub,
            })

        # include explicit Grades rows (if any) and compute per-course averages
        for g in explicit_grades:
            course = g.course_obj
            key = course.pk if course else 'ungrouped'
            entry = course_map[key]
            entry['course'] = course
            entry['assignments'].append({
                'title': getattr(g.homework_obj, 'title', 'Assignment'),
                'submitted_at': getattr(g.homework, 'submitted_at', None),
                'score': g.average_score,
                'grade_obj': g,
            })

        # finalize averages per course
        for key, entry in course_map.items():
            scores = [Decimal(a['score']) for a in entry['assignments'] if a.get('score') is not None]
            if scores:
                entry['average'] = (sum(scores) / Decimal(len(scores))).quantize(Decimal('0.01'))
            else:
                entry['average'] = None

        course_grades = list(course_map.values())

        context = {
            'student': student,
            'courses': courses,
            'course_grades': course_grades,
            'title': 'Grades',
        }
        return render(request, 'student/grades.html', context)


class HomeworkView(StudentRequiredMixin, View):
    """Show a homework and allow student to upload a submission"""

    def get(self, request, pk, *args, **kwargs):
        student = get_object_or_404(StudentProfile, user=request.user)
        homework = get_object_or_404(Homework, pk=pk)

        existing_submission = HomeworkSubmission.objects.filter(
            homework=homework, student=student
        ).first()

        context = {
            'student': student,
            'homework': homework,
            'submission': existing_submission,
            'title': homework.title if getattr(homework, 'title', None) else 'Homework',
        }
        return render(request, 'student/homework.html', context)

    def post(self, request, pk, *args, **kwargs):
        student = get_object_or_404(StudentProfile, user=request.user)
        homework = get_object_or_404(Homework, pk=pk)

        existing_submission = HomeworkSubmission.objects.filter(
            homework=homework, student=student
        ).first()

        if not existing_submission:
            HomeworkSubmission.objects.create(
                homework=homework,
                student=student,
                file=request.FILES.get('file'),
                text=request.POST.get('text', ''),
            )
        return redirect('student:homework', pk=homework.pk)


class ProfileView(StudentRequiredMixin, View):
    """Show and edit the student profile"""

    def get(self, request, *args, **kwargs):
        student = get_object_or_404(StudentProfile, user=request.user)

        context = {
            'student': student,
            'user': student.user,  # you already have the linked user
            'title': 'Profile',
        }
        return render(request, 'student/profile.html', context)


# =======================================================================================
# ============================== STUDENT VIEWS END ======================================
# =======================================================================================
