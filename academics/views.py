# academics/views.py
"""
Academics Views - Teacher va Student panel
Homework, Attendance, Grades, Submissions
"""
import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView
from django.db.models import Prefetch, Q
from accounts.mixins import TeacherRequiredMixin, StudentRequiredMixin
from accounts.models import StudentProfile, TeacherProfile, User
from courses.models import Course, Group
from .models import Homework, HomeworkSubmission, Attendance
from .forms import HomeworkForm, SubmissionCheckForm, AttendanceCreateForm

logger = logging.getLogger(__name__)


# ============================================================================
# TEACHER VIEWS
# ============================================================================

class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    """
    O'qituvchi dashboard - Barcha ma'lumotlarni ko'rish
    """
    template_name = 'teacher/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            teacher = user.teacher_profile
            
            # O'qituvchining guruhlari
            groups = teacher.groups.all()
            
            # Jami studentlar
            total_students = StudentProfile.objects.filter(
                groups__in=groups
            ).distinct().count()
            
            # Baholanmagan submissions
            unchecked_count = HomeworkSubmission.objects.filter(
                homework__group__teacher=teacher,
                score__isnull=True
            ).count()
            
            context.update({
                'teacher': teacher,
                'groups': groups,
                'total_students': total_students,
                'unchecked_submissions': unchecked_count,
            })
            
            logger.info(
                f"Teacher dashboard: {user.email}",
                extra={'user_id': user.id, 'groups_count': groups.count()}
            )
            
        except Exception as e:
            logger.error(
                f"Teacher dashboard xatosi: {str(e)}",
                extra={'user_id': user.id}
            )
            context['error'] = "Profil yuklanishida xatolik"
        
        return context


class HomeworkCreateView(TeacherRequiredMixin, CreateView):
    """
    Yangi topshiriq yaratish
    """
    model = Homework
    form_class = HomeworkForm
    template_name = 'teacher/homework_create.html'
    success_url = reverse_lazy('teacher:unscored_homeworks')
    
    def form_valid(self, form):
        homework = form.save(commit=False)
        homework.teacher = self.request.user.teacher_profile
        homework.save()
        
        messages.success(
            self.request,
            f"Topshiriq '{homework.title}' muvaffaqiyatli yaratildi."
        )
        
        logger.info(
            f"Homework yaratildi: {homework.title}",
            extra={'user_id': self.request.user.id, 'homework_id': homework.id}
        )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Topshiriq yaratishda xatolik. Iltimos, tekshiring."
        )
        logger.warning(
            f"Homework create xatosi: {form.errors}",
            extra={'user_id': self.request.user.id}
        )
        return super().form_invalid(form)


class CheckedSubmissionsListView(TeacherRequiredMixin, ListView):
    """
    Baholangan submissions ro'yxati
    """
    model = HomeworkSubmission
    template_name = 'teacher/checked_submissions.html'
    context_object_name = 'submissions'
    paginate_by = 20
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        return HomeworkSubmission.objects.filter(
            homework__teacher=teacher,
            score__isnull=False
        ).select_related(
            'homework__group',
            'student__user'
        ).order_by('-submitted_at')


class UncheckedSubmissionsListView(TeacherRequiredMixin, ListView):
    """
    Baholanmagan submissions ro'yxati
    """
    model = HomeworkSubmission
    template_name = 'teacher/unchecked_submissions.html'
    context_object_name = 'submissions'
    paginate_by = 20
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        return HomeworkSubmission.objects.filter(
            homework__teacher=teacher,
            score__isnull=True
        ).select_related(
            'homework__group',
            'student__user'
        ).order_by('submitted_at')


class SubmissionUpdateView(TeacherRequiredMixin, UpdateView):
    """
    Submissionni baholash (tahrirlash)
    """
    model = HomeworkSubmission
    form_class = SubmissionCheckForm
    template_name = 'teacher/edit_submission.html'
    pk_url_kwarg = 'submission_id'
    context_object_name = 'submission'
    success_url = reverse_lazy('teacher:unscored_homeworks')
    
    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.checked_by = self.request.user
        submission.save()
        
        messages.success(
            self.request,
            f"Baholash muvaffaqiyatli saqlandi: {submission.score}/100"
        )
        
        logger.info(
            f"Submission baholandi: {submission.id} - {submission.score}",
            extra={'user_id': self.request.user.id, 'submission_id': submission.id}
        )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Baholashda xatolik. Iltimos, tekshiring."
        )
        return super().form_invalid(form)


class AttendanceListView(TeacherRequiredMixin, ListView):
    """
    Davomat ro'yxati
    """
    model = Attendance
    template_name = 'teacher/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 50
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        return Attendance.objects.filter(
            group__teacher=teacher
        ).select_related(
            'student__user',
            'group'
        ).order_by('-date')


class AttendanceCreateView(TeacherRequiredMixin, CreateView):
    """
    Davomat qo'shish
    """
    model = Attendance
    form_class = AttendanceCreateForm
    template_name = 'teacher/attendance_create.html'
    success_url = reverse_lazy('teacher:attendance_list')
    
    def form_valid(self, form):
        attendance = form.save(commit=False)
        attendance.added_by = self.request.user
        attendance.save()
        
        messages.success(
            self.request,
            "Davomat muvaffaqiyatli qayd qilindi."
        )
        
        logger.info(
            f"Davomat qayd qilindi: {attendance.student.user.email}",
            extra={'user_id': self.request.user.id}
        )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Davomatni qayd qilishda xatolik."
        )
        return super().form_invalid(form)
    

class GroupsListView(TeacherRequiredMixin, ListView):
    """
    O'qituvchining guruhlari ro'yxati
    """
    model = Group
    template_name = 'teacher/groups.html'
    context_object_name = 'groups'
    paginate_by = 20
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        return teacher.groups.all().select_related(
            'course',
            'teacher__user'
        ).prefetch_related('students')


class GroupDetailView(TeacherRequiredMixin, DetailView):
    """
    Guruh detallar - studentlar, homework, attendance
    """
    model = Group
    template_name = 'teacher/group_detail.html'
    context_object_name = 'group'
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        return teacher.groups.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = context['group']
        
        # Guruh studentlari
        students = group.students.all().select_related('user')
        
        # Guruh homework'lari
        homeworks = Homework.objects.filter(
            group=group
        ).order_by('-deadline')[:10]
        
        # Yaqinda davomat
        attendances = Attendance.objects.filter(
            group=group
        ).select_related('student__user').order_by('-date')[:20]
        
        context.update({
            'students': students,
            'homeworks': homeworks,
            'recent_attendances': attendances,
            'students_count': students.count(),
        })
        
        return context
    

class MaterialsListView(TeacherRequiredMixin, TemplateView):
    """
    O'qituvchining materiallari ro'yxati
    """
    template_name = 'teacher/materials_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Hozircha oddiy context
        context['teacher'] = teacher
        context['message'] = 'Materiallar tizimi tez orada qo\'shiladi'
        
        return context


class MaterialUploadView(TeacherRequiredMixin, TemplateView):
    """
    Material yuklash
    """
    template_name = 'teacher/material_upload.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'Material yuklash tizimi tez orada qo\'shiladi'
        return context


class StudentsListView(TeacherRequiredMixin, ListView):
    """
    O'qituvchining barcha studentlari
    """
    model = StudentProfile
    template_name = 'teacher/students_list.html'
    context_object_name = 'students'
    paginate_by = 50
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        
        # O'qituvchining guruhlaridagi barcha studentlar
        return StudentProfile.objects.filter(
            groups__teacher=teacher
        ).distinct().select_related('user').order_by('user__first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        context['teacher'] = teacher
        context['total_students'] = self.get_queryset().count()
        return context
    

class GradesListView(TeacherRequiredMixin, ListView):
    """
    Barcha baholar ro'yxati
    """
    model = HomeworkSubmission
    template_name = 'teacher/grades_list.html'
    context_object_name = 'submissions'
    paginate_by = 50
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        
        return HomeworkSubmission.objects.filter(
            homework__teacher=teacher,
            score__isnull=False
        ).select_related(
            'student__user',
            'homework__group__course',
            'homework'
        ).order_by('-submitted_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Statistika
        total_graded = self.get_queryset().count()
        avg_score = self.get_queryset().aggregate(
            avg=models.Avg('score')
        )['avg'] or 0
        
        context.update({
            'teacher': teacher,
            'total_graded': total_graded,
            'average_score': round(avg_score, 2),
        })
        
        return context


class ScheduleView(TeacherRequiredMixin, TemplateView):
    """
    Dars jadvali
    """
    template_name = 'teacher/schedule.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Hozircha oddiy placeholder
        context['teacher'] = teacher
        context['message'] = 'Dars jadvali tizimi tez orada qo\'shiladi'
        
        return context



class ReportsView(TeacherRequiredMixin, TemplateView):
    """
    Hisobotlar
    """
    template_name = 'teacher/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Hozircha oddiy statistika
        total_students = StudentProfile.objects.filter(
            groups__teacher=teacher
        ).distinct().count()
        
        total_homeworks = Homework.objects.filter(
            teacher=teacher
        ).count()
        
        graded_submissions = HomeworkSubmission.objects.filter(
            homework__teacher=teacher,
            score__isnull=False
        ).count()
        
        context.update({
            'teacher': teacher,
            'total_students': total_students,
            'total_homeworks': total_homeworks,
            'graded_submissions': graded_submissions,
        })
        
        return context
    

class TeacherProfileView(TeacherRequiredMixin, DetailView):
    """
    O'qituvchi profili
    """
    model = TeacherProfile
    template_name = 'teacher/profile.html'
    context_object_name = 'teacher'
    
    def get_object(self):
        return self.request.user.teacher_profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        
        # Qo'shimcha statistika
        teacher = context['teacher']
        context['groups_count'] = teacher.groups.count()
        context['students_count'] = StudentProfile.objects.filter(
            groups__teacher=teacher
        ).distinct().count()
        
        return context


class HomeworkListView(TeacherRequiredMixin, ListView):
    """
    Barcha topshiriqlar ro'yxati
    """
    model = Homework
    template_name = 'teacher/homework_list.html'
    context_object_name = 'homeworks'
    paginate_by = 20
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        return Homework.objects.filter(
            teacher=teacher
        ).select_related('group__course').order_by('-deadline')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teacher'] = self.request.user.teacher_profile
        return context

# ============================================================================
# STUDENT VIEWS
# ============================================================================

class StudentDashboardView(StudentRequiredMixin, TemplateView):
    """
    O'quvchi dashboard
    """
    template_name = 'student/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            student = user.student_profile
            
            # O'quvchining guruhlari
            groups = student.groups.all().select_related('course', 'teacher__user')
            
            # Topshiriqlar
            homeworks = Homework.objects.filter(
                group__in=groups
            ).order_by('-deadline')
            
            # Ballar
            grades = HomeworkSubmission.objects.filter(
                student=student,
                score__isnull=False
            ).select_related('homework').order_by('-submitted_at')[:5]
            
            context.update({
                'student': student,
                'groups': groups,
                'homeworks': homeworks[:5],
                'recent_grades': grades,
            })
            
            logger.info(
                f"Student dashboard: {user.email}",
                extra={'user_id': user.id}
            )
            
        except StudentProfile.DoesNotExist:
            logger.error(
                f"Student profile yo'q: {user.email}",
                extra={'user_id': user.id}
            )
            context['error'] = "Talaba profili topilmadi"
        
        return context


class StudentCourseListView(StudentRequiredMixin, ListView):
    """
    O'quvchining kurslar ro'yxati
    """
    model = Course
    template_name = 'student/courses.html'
    context_object_name = 'courses'
    paginate_by = 10
    
    def get_queryset(self):
        student = self.request.user.student_profile
        return Course.objects.filter(
            groups__students=student
        ).distinct()


class StudentGradesListView(StudentRequiredMixin, ListView):
    """
    O'quvchining baholar ro'yxati
    """
    model = HomeworkSubmission
    template_name = 'student/grades.html'
    context_object_name = 'submissions'
    paginate_by = 20
    
    def get_queryset(self):
        student = self.request.user.student_profile
        return HomeworkSubmission.objects.filter(
            student=student,
            score__isnull=False
        ).select_related(
            'homework__group__course',
            'homework'
        ).order_by('-submitted_at')


class StudentHomeworkDetailView(StudentRequiredMixin, DetailView):
    """
    Topshiriq detallarini ko'rish va submission yuborish
    """
    model = Homework
    template_name = 'student/homework_detail.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'homework'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        homework = context['homework']
        
        # Mavjud submission tekshirish
        submission = HomeworkSubmission.objects.filter(
            homework=homework,
            student=student
        ).first()
        
        context['submission'] = submission
        context['student'] = student
        
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Topshiriq yuborish
        """
        student = request.user.student_profile
        homework = self.get_object()
        
        # Mavjud submission tekshirish
        existing = HomeworkSubmission.objects.filter(
            homework=homework,
            student=student
        ).first()
        
        if existing and existing.score is not None:
            messages.error(
                request,
                "Bu topshiriq allaqachon baholangan."
            )
            return redirect('student:homework', pk=homework.pk)
        
        try:
            if not existing:
                HomeworkSubmission.objects.create(
                    homework=homework,
                    student=student,
                    file=request.FILES.get('file'),
                    text=request.POST.get('text', ''),
                )
                messages.success(
                    request,
                    "Topshiriq muvaffaqiyatli yuborildi!"
                )
                logger.info(
                    f"Submission yuborildi: {homework.title}",
                    extra={'user_id': request.user.id, 'student_id': student.id}
                )
            else:
                # Mavjud submissionni yangilash
                existing.file = request.FILES.get('file') or existing.file
                existing.text = request.POST.get('text', '') or existing.text
                existing.save()
                messages.success(
                    request,
                    "Topshiriq yangilandi!"
                )
        
        except Exception as e:
            logger.error(
                f"Submission error: {str(e)}",
                extra={'user_id': request.user.id}
            )
            messages.error(
                request,
                "Topshiriqni yuborishda xatolik yuz berdi."
            )
        
        return redirect('student:homework', pk=homework.pk)


class StudentProfileView(StudentRequiredMixin, DetailView):
    """
    O'quvchining profili
    """
    model = StudentProfile
    template_name = 'student/profile.html'
    context_object_name = 'student'
    
    def get_object(self):
        return self.request.user.student_profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context