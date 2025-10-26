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
from accounts.models import StudentProfile
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