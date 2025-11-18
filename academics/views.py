<<<<<<< HEAD
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
=======
# academics/views.py
"""
Academics Views - Teacher va Student panel
Homework, Attendance, Grades, Submissions
"""
import logging
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView
from django.db.models import Prefetch, Q
from accounts.mixins import TeacherRequiredMixin, StudentRequiredMixin
from accounts.models import StudentProfile, TeacherProfile, User
from courses.models import Course, Group
from .models import Homework, HomeworkSubmission, Attendance
from .forms import HomeworkForm, SubmissionCheckForm, AttendanceSelectForm
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.views import View
from django.db import transaction
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


# ============================================================================
# TEACHER VIEWS
# ============================================================================

class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    """
    O'qituvchi dashboard - FIXED VERSION
    """
    template_name = 'teacher/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            # Get teacher profile
            teacher = user.teacher_profile
            
            # FIXED: O'qituvchining guruhlari - reverse relation
            # OLD (XATO): groups = teacher.groups.all()
            # NEW (TO'G'RI): 
            groups = Group.objects.filter(teacher=teacher).select_related('course')
            
            # FIXED: Jami studentlar - correct query
            # OLD: StudentProfile.objects.filter(groups__in=groups).distinct().count()
            # NEW:
            total_students = 0
            for group in groups:
                total_students += group.students.count()
            
            # Yoki optimized version:
            # from django.db.models import Count
            # total_students = Group.objects.filter(teacher=teacher).aggregate(
            #     total=Count('students', distinct=True)
            # )['total'] or 0
            
            # FIXED: Baholanmagan submissions
            # OLD: homework__group__teacher=teacher
            # NEW: homework__teacher=teacher (agar Homework modelida teacher field bo'lsa)
            unchecked_count = HomeworkSubmission.objects.filter(
                homework__teacher=teacher,
                score__isnull=True
            ).count()
            
            # Recent unchecked submissions (for display)
            recent_unchecked = HomeworkSubmission.objects.filter(
                homework__teacher=teacher,
                score__isnull=True
            ).select_related(
                'student__user',
                'homework',
                'homework__group'
            ).order_by('-submitted_at')[:5]
            
            context.update({
                'teacher': teacher,
                'groups': groups,
                'total_students': total_students,
                'unchecked_submissions': unchecked_count,
                'recent_unchecked': recent_unchecked,
            })
            
            logger.info(
                f"Teacher dashboard: {user.email}",
                extra={'user_id': user.id, 'groups_count': groups.count()}
            )
            
        except TeacherProfile.DoesNotExist:
            # Agar teacher profil yo'q bo'lsa, yaratish
            logger.warning(f"Teacher profile not found for user: {user.email}")
            teacher = TeacherProfile.objects.create(user=user)
            
            context.update({
                'teacher': teacher,
                'groups': [],
                'total_students': 0,
                'unchecked_submissions': 0,
                'recent_unchecked': [],
            })
            
            messages.info(
                self.request,
                "Sizning profilingiz yaratildi. Admin tomonidan guruhlar tayinlanishini kuting."
            )
            
        except Exception as e:
            logger.error(
                f"Teacher dashboard xatosi: {str(e)}",
                extra={'user_id': user.id, 'error': str(e)}
            )
            
            context['error'] = "Profil yuklanishida xatolik"
            context['teacher'] = None
            context['groups'] = []
            context['total_students'] = 0
            context['unchecked_submissions'] = 0
            context['recent_unchecked'] = []
            
            messages.error(
                self.request,
                "Dashboard yuklanishida xatolik yuz berdi."
            )
        
        return context


class HomeworkCreateView(TeacherRequiredMixin, CreateView):
    """
    Yangi topshiriq yaratish
    """
    model = Homework
    form_class = HomeworkForm
    template_name = 'teacher/homework/create.html'
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
    template_name = 'teacher/homework/submissions_unchecked.html'
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
    template_name = 'teacher/homework/edit.html'
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
    Davomat ro'yxati - Professional implementation with filters
    """
    model = Attendance
    template_name = 'teacher/attendance/list.html'
    context_object_name = 'attendances'
    paginate_by = 50
    
    def get_queryset(self):
        """
        Queryset with filters and optimizations
        """
        teacher = self.request.user.teacher_profile
        
        # Base queryset - faqat o'qituvchining guruhlari
        queryset = Attendance.objects.filter(
            group__teacher=teacher
        ).select_related(
            'student__user',
            'group',
            'added_by'
        ).order_by('-date', '-created_at')
        
        # FILTER 1: Search by student name or email
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(student__user__email__icontains=search)
            )
        
        # FILTER 2: Filter by group
        group_id = self.request.GET.get('group', '').strip()
        if group_id:
            try:
                queryset = queryset.filter(group_id=int(group_id))
            except ValueError:
                pass
        
        # FILTER 3: Filter by status
        status = self.request.GET.get('status', '').strip()
        if status and status in ['present', 'absent', 'late', 'excused']:
            queryset = queryset.filter(status=status)
        
        # FILTER 4: Filter by date
        date = self.request.GET.get('date', '').strip()
        if date:
            try:
                queryset = queryset.filter(date=date)
            except ValueError:
                pass
        
        # FILTER 5: Date range (optional)
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Context with statistics
        """
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Get filtered queryset for statistics
        filtered_qs = self.get_queryset()
        
        # Calculate statistics using aggregation
        stats = filtered_qs.aggregate(
            total=Count('id'),
            present_count=Count('id', filter=Q(status='present')),
            absent_count=Count('id', filter=Q(status='absent')),
            late_count=Count('id', filter=Q(status='late')),
            excused_count=Count('id', filter=Q(status='excused'))
        )
        
        # O'qituvchining barcha guruhlari (filter uchun)
        teacher_groups = teacher.groups.all().order_by('name')
        
        # Attendance rate calculation
        total = stats['total']
        if total > 0:
            attended = stats['present_count'] + stats['late_count'] + stats['excused_count']
            attendance_rate = round((attended / total) * 100, 1)
        else:
            attendance_rate = 0
        
        context.update({
            'teacher': teacher,
            'teacher_groups': teacher_groups,
            'total_records': stats['total'],
            'present_count': stats['present_count'],
            'absent_count': stats['absent_count'],
            'late_count': stats['late_count'],
            'excused_count': stats['excused_count'],
            'attendance_rate': attendance_rate,
            # Preserve filter values
            'current_search': self.request.GET.get('search', ''),
            'current_group': self.request.GET.get('group', ''),
            'current_status': self.request.GET.get('status', ''),
            'current_date': self.request.GET.get('date', ''),
        })
        
        logger.info(
            f"Attendance list viewed: Teacher={teacher.user.email}, Records={stats['total']}",
            extra={'user_id': self.request.user.id}
        )
        
        return context


class AttendanceCreateView(TeacherRequiredMixin, View):
    """
    Davomat yaratish - WORKING VERSION
    """
    template_name = 'teacher/attendance/create.html'
    
    def get(self, request):
        """
        GET: Guruh va sana tanlash, talabalar ro'yxatini ko'rsatish
        """
        teacher = request.user.teacher_profile
        
        # Selection form
        select_form = AttendanceSelectForm(
            request.GET or None,
            teacher=teacher
        )
        
        context = {
            'select_form': select_form,
            'teacher': teacher,
        }
        
        # Agar guruh va sana tanlangan bo'lsa
        if request.GET.get('group') and request.GET.get('date'):
            try:
                group_id = int(request.GET.get('group'))
                date_str = request.GET.get('date')
                
                # Guruh tekshiruvi
                group = get_object_or_404(
                    Group,
                    id=group_id,
                    teacher=teacher
                )
                
                # Talabalarni list ga o'girish
                students = list(group.students.filter(
                    user__is_active=True
                ).select_related('user').order_by('user__first_name', 'user__last_name'))
                
                # Mavjud davomatlar
                existing_attendances = Attendance.objects.filter(
                    group=group,
                    date=date_str
                ).select_related('student__user')
                
                existing_dict = {
                    att.student_id: att 
                    for att in existing_attendances
                }
                
                # Har bir student'ga existing_attendance qo'shish
                for student in students:
                    if student.id in existing_dict:
                        student.existing_attendance = existing_dict[student.id]
                    else:
                        student.existing_attendance = None
                
                context.update({
                    'group': group,
                    'date': date_str,
                    'students': students,
                    'has_existing': len(existing_dict) > 0,
                })
                
                logger.info(
                    f"Attendance form loaded: Group={group.name}, Date={date_str}, Students={len(students)}"
                )
                
            except (ValueError, Group.DoesNotExist) as e:
                messages.error(request, "Guruh topilmadi.")
                logger.error(f"Error loading attendance form: {str(e)}")
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """
        POST: Bulk attendance yaratish/yangilash
        """
        teacher = request.user.teacher_profile
        
        try:
            group_id = request.POST.get('group_id')
            date = request.POST.get('date')
            
            # Debug logging
            logger.info(f"POST data received: group_id={group_id}, date={date}")
            logger.info(f"All POST data: {request.POST}")
            
            # Validatsiya
            if not group_id or not date:
                messages.error(request, "Guruh va sana majburiy!")
                logger.warning("Missing group_id or date")
                return redirect('teacher:attendance_create')
            
            # Guruh tekshiruvi
            group = get_object_or_404(
                Group,
                id=group_id,
                teacher=teacher
            )
            
            logger.info(f"Group found: {group.name}")
            
            # Talabalar ro'yxati
            students = group.students.filter(user__is_active=True)
            logger.info(f"Active students count: {students.count()}")
            
            # Bulk attendance yaratish/yangilash
            success_count = 0
            error_count = 0
            errors = []
            
            with transaction.atomic():
                for student in students:
                    # Har bir talaba uchun status olish
                    status_key = f'status_{student.id}'
                    status = request.POST.get(status_key)
                    
                    logger.info(f"Processing student {student.id}: status_key={status_key}, status={status}")
                    
                    if not status:
                        logger.warning(f"No status for student {student.id}")
                        continue
                    
                    try:
                        # FIXED: Note fieldini o'chirdik
                        attendance, created = Attendance.objects.update_or_create(
                            group=group,
                            student=student,
                            date=date,
                            defaults={
                                'status': status,
                                'added_by': request.user
                            }
                        )
                        
                        success_count += 1
                        action = 'created' if created else 'updated'
                        
                        logger.info(
                            f"Attendance {action}: Student={student.user.email}, "
                            f"Status={status}, ID={attendance.id}"
                        )
                        
                    except IntegrityError as e:
                        error_count += 1
                        error_msg = f"Student {student.user.email}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(f"IntegrityError: {error_msg}")
                        
                    except Exception as e:
                        error_count += 1
                        error_msg = f"Student {student.user.email}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(f"Unexpected error: {error_msg}")
            
            # Success message
            if success_count > 0:
                messages.success(
                    request,
                    f"✅ {success_count} ta talabaning davomat ma'lumoti saqlandi!"
                )
                logger.info(f"Bulk attendance success: {success_count} records")
            
            if error_count > 0:
                messages.warning(
                    request,
                    f"⚠️ {error_count} ta xatolik yuz berdi. Detallarga log'da qarang."
                )
                for error in errors:
                    logger.error(f"Error detail: {error}")
            
            # Redirect to attendance list
            return redirect('teacher:attendance_list')
            
        except Exception as e:
            error_msg = f"Davomatni saqlashda xatolik: {str(e)}"
            messages.error(request, error_msg)
            logger.error(
                f"Critical error in attendance save: {error_msg}",
                exc_info=True
            )
            return redirect('teacher:attendance_create')



# ALTERNATIVE: Class-based view with FormView
from django.views.generic.edit import FormView

class AttendanceCreateFormView(TeacherRequiredMixin, FormView):
    """
    Alternative implementation using FormView
    """
    template_name = 'teacher/attendance/create.html'
    form_class = AttendanceSelectForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user.teacher_profile
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agar guruh tanlangan bo'lsa
        if self.request.GET.get('group'):
            group_id = self.request.GET.get('group')
            teacher = self.request.user.teacher_profile
            
            try:
                group = Group.objects.get(id=group_id, teacher=teacher)
                students = group.students.filter(
                    user__is_active=True
                ).select_related('user')
                
                context['group'] = group
                context['students'] = students
                context['date'] = self.request.GET.get('date', timezone.now().date())
                
            except Group.DoesNotExist:
                messages.error(self.request, "Guruh topilmadi")
        
        return context
    

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
            avg = Avg('score')
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


# class HomeworkListView(TeacherRequiredMixin, ListView):
#     """
#     Barcha topshiriqlar ro'yxati
#     """
#     model = Homework
#     template_name = 'teacher/homework/list.html'
#     context_object_name = 'homeworks'
#     paginate_by = 20
    
#     def get_queryset(self):
#         teacher = self.request.user.teacher_profile
#         return Homework.objects.filter(
#             teacher=teacher
#         ).select_related('group__course').order_by('-deadline')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['teacher'] = self.request.user.teacher_profile
#         return context
class HomeworkListView(TeacherRequiredMixin, ListView):
    """
    Barcha topshiriqlar ro'yxati - FIXED with counts
    """
    model = Homework
    template_name = 'teacher/homework/list.html'
    context_object_name = 'homeworks'
    paginate_by = 20
    
    def get_queryset(self):
        teacher = self.request.user.teacher_profile
        queryset = Homework.objects.filter(
            teacher=teacher
        ).select_related('group__course').annotate(
            # Jami submissions
            submissions_count=Count('submissions'),
            # Baholanmagan submissions
            ungraded_count=Count('submissions', filter=Q(submissions__score__isnull=True))
        ).order_by('-deadline')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teacher'] = self.request.user.teacher_profile
        
        # Qo'shimcha statistika (ixtiyoriy)
        homeworks = self.get_queryset()
        context['active_count'] = homeworks.filter(deadline__gte=timezone.now()).count()
        context['expired_count'] = homeworks.filter(deadline__lt=timezone.now()).count()
        
        return context

# ============================================================================
# STUDENT VIEWS
# ============================================================================

class StudentDashboardView(StudentRequiredMixin, TemplateView):
    """
    Professional Student Dashboard with complete statistics
    """
    template_name = 'student/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            student = user.student_profile
            
            # Guruhlar
            groups = student.groups.all().select_related(
                'course', 
                'teacher__user'
            )
            
            # Kurslar (distinct)
            courses = Course.objects.filter(
                groups__students=student
            ).distinct()
            
            # Topshiriqlar statistikasi
            now = timezone.now()
            
            # Barcha topshiriqlar
            all_homeworks = Homework.objects.filter(
                group__in=groups
            )
            
            # Pending (yuborilmagan)
            pending_homeworks = all_homeworks.exclude(
                submissions__student=student
            ).filter(deadline__gte=now)
            
            # Submitted (yuborilgan, baholanmagan)
            submitted_homeworks = HomeworkSubmission.objects.filter(
                student=student,
                score__isnull=True
            )
            
            # Graded (baholangan)
            graded_homeworks = HomeworkSubmission.objects.filter(
                student=student,
                score__isnull=False
            )
            
            # Overdue (muddati o'tgan)
            overdue_homeworks = all_homeworks.exclude(
                submissions__student=student
            ).filter(deadline__lt=now)
            
            # O'rtacha ball
            average_score = graded_homeworks.aggregate(
                avg=Avg('score')
            )['avg'] or 0
            
            # Yaqinda baholangan topshiriqlar
            recent_grades = graded_homeworks.select_related(
                'homework__group__course'
            ).order_by('-submitted_at')[:5]
            
            # Kelayotgan topshiriqlar (deadline yaqin)
            upcoming_homeworks = pending_homeworks.order_by('deadline')[:5]
            
            # Davomat statistikasi
            total_attendance = Attendance.objects.filter(
                student=student
            ).count()
            
            present_count = Attendance.objects.filter(
                student=student,
                status='present'
            ).count()
            
            # Attendance rate
            if total_attendance > 0:
                attendance_rate = round((present_count / total_attendance) * 100, 1)
            else:
                attendance_rate = 0
            
            # So'nggi 30 kun ichidagi davomat
            thirty_days_ago = now.date() - timedelta(days=30)
            recent_attendance = Attendance.objects.filter(
                student=student,
                date__gte=thirty_days_ago
            ).count()
            
            context.update({
                'student': student,
                'groups': groups,
                'courses': courses,
                
                # Homework stats
                'total_homeworks': all_homeworks.count(),
                'pending_count': pending_homeworks.count(),
                'submitted_count': submitted_homeworks.count(),
                'graded_count': graded_homeworks.count(),
                'overdue_count': overdue_homeworks.count(),
                
                # Average score
                'average_score': round(average_score, 1),
                
                # Recent data
                'recent_grades': recent_grades,
                'upcoming_homeworks': upcoming_homeworks,
                
                # Attendance
                'total_attendance': total_attendance,
                'present_count': present_count,
                'attendance_rate': attendance_rate,
                'recent_attendance_count': recent_attendance,
                
                # Counts
                'groups_count': groups.count(),
                'courses_count': courses.count(),
            })
            
            logger.info(
                f"Student dashboard loaded: {user.email}",
                extra={'user_id': user.id}
            )
            
        except Exception as e:
            logger.error(
                f"Student dashboard error: {str(e)}",
                extra={'user_id': user.id},
                exc_info=True
            )
            context['error'] = "Ma'lumotlarni yuklashda xatolik"
            template_name = 'erors/404.html'
        
        return context


class StudentHomeworkListView(StudentRequiredMixin, ListView):
    """
    Student homework list with filters
    """
    model = Homework
    template_name = 'student/homework_list.html'
    context_object_name = 'homeworks'
    paginate_by = 20
    
    def get_queryset(self):
        student = self.request.user.student_profile
        groups = student.groups.all()
        
        # Base queryset
        queryset = Homework.objects.filter(
            group__in=groups
        ).select_related(
            'group__course',
            'teacher__user'
        ).order_by('-deadline')
        
        # Filter by status
        status = self.request.GET.get('status', '')
        
        if status == 'pending':
            # Yuborilmagan
            queryset = queryset.exclude(
                submissions__student=student
            ).filter(deadline__gte=timezone.now())
            
        elif status == 'submitted':
            # Yuborilgan, baholanmagan
            queryset = queryset.filter(
                submissions__student=student,
                submissions__score__isnull=True
            )
            
        elif status == 'graded':
            # Baholangan
            queryset = queryset.filter(
                submissions__student=student,
                submissions__score__isnull=False
            )
            
        elif status == 'overdue':
            # Muddati o'tgan
            queryset = queryset.exclude(
                submissions__student=student
            ).filter(deadline__lt=timezone.now())
        
        # Filter by course
        course_id = self.request.GET.get('course', '')
        if course_id:
            queryset = queryset.filter(group__course_id=course_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Submission status for each homework
        homeworks = context['homeworks']
        for homework in homeworks:
            submission = HomeworkSubmission.objects.filter(
                homework=homework,
                student=student
            ).first()
            homework.submission = submission
        
        # Courses for filter
        courses = Course.objects.filter(
            groups__students=student
        ).distinct()
        
        context.update({
            'student': student,
            'courses': courses,
            'current_status': self.request.GET.get('status', ''),
            'current_course': self.request.GET.get('course', ''),
        })
        
        return context


class StudentAttendanceHistoryView(StudentRequiredMixin, ListView):
    """
    Student attendance history with statistics
    """
    model = Attendance
    template_name = 'student/attendance_history.html'
    context_object_name = 'attendances'
    paginate_by = 50
    
    def get_queryset(self):
        student = self.request.user.student_profile
        
        queryset = Attendance.objects.filter(
            student=student
        ).select_related(
            'group__course',
            'added_by'
        ).order_by('-date')
        
        # Filter by date range
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by group
        group_id = self.request.GET.get('group', '')
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Statistics
        filtered_qs = self.get_queryset()
        
        stats = filtered_qs.aggregate(
            total=Count('id'),
            present_count=Count('id', filter=Q(status='present')),
            absent_count=Count('id', filter=Q(status='absent')),
            late_count=Count('id', filter=Q(status='late')),
            excused_count=Count('id', filter=Q(status='excused'))
        )
        
        # Attendance rate
        total = stats['total']
        if total > 0:
            attended = stats['present_count'] + stats['late_count'] + stats['excused_count']
            attendance_rate = round((attended / total) * 100, 1)
        else:
            attendance_rate = 0
        
        # Groups for filter
        groups = student.groups.all()
        
        context.update({
            'student': student,
            'groups': groups,
            'total_records': stats['total'],
            'present_count': stats['present_count'],
            'absent_count': stats['absent_count'],
            'late_count': stats['late_count'],
            'excused_count': stats['excused_count'],
            'attendance_rate': attendance_rate,
            'current_status': self.request.GET.get('status', ''),
            'current_group': self.request.GET.get('group', ''),
            'current_date_from': self.request.GET.get('date_from', ''),
            'current_date_to': self.request.GET.get('date_to', ''),
        })
        
        return context


# Keep existing views (improved versions)
class StudentCourseListView(StudentRequiredMixin, ListView):
    """
    Student courses list
    """
    model = Course
    template_name = 'student/courses.html'
    context_object_name = 'courses'
    paginate_by = 10
    
    def get_queryset(self):
        student = self.request.user.student_profile
        return Course.objects.filter(
            groups__students=student
        ).distinct().prefetch_related('groups')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Add groups for each course
        courses = context['courses']
        for course in courses:
            course.student_groups = course.groups.filter(
                students=student
            ).select_related('teacher__user')
        
        context['student'] = student
        return context


class StudentGradesListView(StudentRequiredMixin, ListView):
    """
    Student grades list with statistics
    """
    model = HomeworkSubmission
    template_name = 'student/grades.html'
    context_object_name = 'submissions'
    paginate_by = 20
    
    def get_queryset(self):
        student = self.request.user.student_profile
        
        queryset = HomeworkSubmission.objects.filter(
            student=student,
            score__isnull=False
        ).select_related(
            'homework__group__course',
            'homework__teacher__user'
        ).order_by('-submitted_at')
        
        # Filter by course
        course_id = self.request.GET.get('course', '')
        if course_id:
            queryset = queryset.filter(homework__group__course_id=course_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        # Statistics
        filtered_qs = self.get_queryset()
        
        average_score = filtered_qs.aggregate(
            avg=Avg('score')
        )['avg'] or 0
        
        highest_score = filtered_qs.aggregate(
            max=Sum('score')
        )['max'] or 0
        
        # Courses for filter
        courses = Course.objects.filter(
            groups__students=student
        ).distinct()
        
        context.update({
            'student': student,
            'courses': courses,
            'average_score': round(average_score, 1),
            'highest_score': highest_score,
            'total_graded': filtered_qs.count(),
            'current_course': self.request.GET.get('course', ''),
        })
        
        return context


class StudentHomeworkDetailView(StudentRequiredMixin, DetailView):
    """
    Homework detail with submission
    """
    model = Homework
    template_name = 'student/homework_detail.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'homework'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        homework = context['homework']
        
        # Submission
        submission = HomeworkSubmission.objects.filter(
            homework=homework,
            student=student
        ).first()
        
        context.update({
            'submission': submission,
            'student': student,
            'can_submit': submission is None or submission.score is None,
            'is_overdue': homework.deadline < timezone.now(),
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Submit or update homework
        """
        student = request.user.student_profile
        homework = self.get_object()
        
        # Check if already graded
        existing = HomeworkSubmission.objects.filter(
            homework=homework,
            student=student
        ).first()
        
        if existing and existing.score is not None:
            messages.error(
                request,
                "Bu topshiriq allaqachon baholangan. Qayta yuborish mumkin emas."
            )
            return redirect('student:homework_detail', pk=homework.pk)
        
        # Check deadline
        if homework.deadline < timezone.now():
            messages.warning(
                request,
                "Topshiriq muddati o'tgan, lekin yuborildi."
            )
        
        try:
            file = request.FILES.get('file')
            text = request.POST.get('text', '').strip()
            
            if not file and not text:
                messages.error(request, "Fayl yoki matn majburiy!")
                return redirect('student:homework_detail', pk=homework.pk)
            
            if not existing:
                # Create new submission
                HomeworkSubmission.objects.create(
                    homework=homework,
                    student=student,
                    file=file,
                    text=text,
                )
                messages.success(
                    request,
                    "✅ Topshiriq muvaffaqiyatli yuborildi!"
                )
                logger.info(
                    f"Submission created: {homework.title}",
                    extra={'user_id': request.user.id}
                )
            else:
                # Update existing
                if file:
                    existing.file = file
                if text:
                    existing.text = text
                existing.save()
                
                messages.success(
                    request,
                    "✅ Topshiriq yangilandi!"
                )
                logger.info(
                    f"Submission updated: {homework.title}",
                    extra={'user_id': request.user.id}
                )
        
        except Exception as e:
            logger.error(
                f"Submission error: {str(e)}",
                extra={'user_id': request.user.id},
                exc_info=True
            )
            messages.error(
                request,
                "❌ Topshiriqni yuborishda xatolik yuz berdi."
            )
        
        return redirect('student:homework_detail', pk=homework.pk)


class StudentProfileView(StudentRequiredMixin, DetailView):
    """
    Student profile with statistics
    """
    model = StudentProfile
    template_name = 'student/profile.html'
    context_object_name = 'student'
    
    def get_object(self):
        return self.request.user.student_profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Statistics
        total_submissions = HomeworkSubmission.objects.filter(
            student=student
        ).count()
        
        graded_submissions = HomeworkSubmission.objects.filter(
            student=student,
            score__isnull=False
        ).count()
        
        average_score = HomeworkSubmission.objects.filter(
            student=student,
            score__isnull=False
        ).aggregate(avg=Avg('score'))['avg'] or 0
        
        total_attendance = Attendance.objects.filter(
            student=student
        ).count()
        
        present_count = Attendance.objects.filter(
            student=student,
            status='present'
        ).count()
        
        if total_attendance > 0:
            attendance_rate = round((present_count / total_attendance) * 100, 1)
        else:
            attendance_rate = 0
        
        context.update({
            'user': self.request.user,
            'total_submissions': total_submissions,
            'graded_submissions': graded_submissions,
            'average_score': round(average_score, 1),
            'total_attendance': total_attendance,
            'attendance_rate': attendance_rate,
            'groups': student.groups.all(),
        })
        
        return context
    
>>>>>>> main
