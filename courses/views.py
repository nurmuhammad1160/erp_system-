 # courses/views_admin.py - FIXED VERSION
"""
Admin Panel Views - Fixed for your models
"""
import logging
from tokenize import group

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import (
    TemplateView, ListView, DetailView, 
    CreateView, UpdateView, DeleteView, View
)
from django.urls import reverse_lazy, reverse
from django.db.models import Count, Q, Avg
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

from accounts.mixins import AdminRequiredMixin
from accounts.models import User, TeacherProfile, StudentProfile
from courses.models import Course, Group
from academics.models import Homework, HomeworkSubmission, Attendance

# forms
from .forms import *

logger = logging.getLogger(__name__)

User = get_user_model()


# ============================================================================
# DASHBOARD - FIXED
# ============================================================================

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """
    Admin Dashboard - Fixed for your Group model
    """
    template_name = 'admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic counts
        total_users = User.objects.count()
        total_students = User.objects.filter(type='student').count()
        total_teachers = User.objects.filter(type__in=['teacher', 'support_teacher']).count()
        total_admins = User.objects.filter(type__in=['admin', 'manager']).count()
        
        total_courses = Course.objects.count()
        total_groups = Group.objects.count()
        
        # Active counts - FIXED: using correct fields
        active_users = User.objects.filter(is_active=True).count()
        
        # Group model - use 'status' instead of 'is_active'
        active_groups = Group.objects.filter(status='active').count()
        
        # This month registrations
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_users_this_month = User.objects.filter(
            date_joined__gte=month_start
        ).count()
        
        # Recent users (last 10)
        recent_users = User.objects.all().order_by('-date_joined')[:10]
        
        # Recent submissions
        recent_submissions = HomeworkSubmission.objects.select_related(
            'student__user', 'homework'
        ).order_by('-submitted_at')[:10]
        
        # Recent attendance
        recent_attendance = Attendance.objects.select_related(
            'student__user', 'group'
        ).order_by('-date')[:10]
        
        # User registration trend (last 6 months)
        registration_data = []
        for i in range(6):
            month_date = now - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            
            # Calculate month end safely
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            count = User.objects.filter(
                date_joined__gte=month_start,
                date_joined__lte=month_end
            ).count()
            
            registration_data.append({
                'month': month_start.strftime('%B'),
                'count': count
            })
        
        registration_data.reverse()
        
        # Top courses by enrollment
        top_courses = Course.objects.annotate(
            student_count=Count('groups__students', distinct=True)
        ).order_by('-student_count')[:5]
        
        context.update({
            # Counts
            'total_users': total_users,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_admins': total_admins,
            'total_courses': total_courses,
            'total_groups': total_groups,
            
            # Active
            'active_users': active_users,
            'active_groups': active_groups,
            
            # This month
            'new_users_this_month': new_users_this_month,
            
            # Recent data
            'recent_users': recent_users,
            'recent_submissions': recent_submissions,
            'recent_attendance': recent_attendance,
            
            # Charts data
            'registration_data': registration_data,
            'top_courses': top_courses,
        })
        
        logger.info(f"Admin dashboard accessed by {self.request.user.email}")
        
        return context


# ============================================================================
# USER MANAGEMENT - Same as before
# ============================================================================

class AdminUserListView(AdminRequiredMixin, ListView):
    """
    Barcha foydalanuvchilar ro'yxati
    """
    model = User
    template_name = 'admin/users/list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        
        # Filter by role
        role = self.request.GET.get('role', '')
        if role:
            queryset = queryset.filter(type=role)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Stats
        context.update({
            'total_count': User.objects.count(),
            'student_count': User.objects.filter(type='student').count(),
            'teacher_count': User.objects.filter(type__in=['teacher', 'support_teacher']).count(),
            'admin_count': User.objects.filter(type__in=['admin', 'manager']).count(),
            
            # Filters
            'current_role': self.request.GET.get('role', ''),
            'current_status': self.request.GET.get('status', ''),
            'current_search': self.request.GET.get('search', ''),
        })
        
        return context


class AdminUserCreateView(AdminRequiredMixin, CreateView):
    """
    Yangi foydalanuvchi yaratish
    """
    model = User
    template_name = 'admin/users/create.html'
    fields = ['first_name', 'last_name', 'email', 'password', 'type', 'is_active']
    success_url = reverse_lazy('admin_panel:user_list')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        # Password hash
        user.set_password(form.cleaned_data['password'])
        user.save()
        
        # Create profile based on type
        if user.type == 'student':
            StudentProfile.objects.get_or_create(user=user)
        elif user.type in ['teacher', 'support_teacher']:
            TeacherProfile.objects.get_or_create(user=user)
        
        messages.success(
            self.request,
            f"✅ Foydalanuvchi muvaffaqiyatli yaratildi: {user.email}"
        )
        
        logger.info(f"User created by admin: {user.email}")
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "❌ Xatolik! Formani to'g'ri to'ldiring."
        )
        return super().form_invalid(form)


class AdminUserDetailView(AdminRequiredMixin, DetailView):
    """
    Foydalanuvchi detallari
    """
    model = User
    template_name = 'admin/users/detail.html'
    context_object_name = 'user_obj'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        
        # Get profile
        profile = None
        if user.type == 'student':
            try:
                profile = user.student_profile
                # Student stats
                context['groups'] = profile.groups.all()
                context['total_submissions'] = HomeworkSubmission.objects.filter(
                    student=profile
                ).count()
                context['total_attendance'] = Attendance.objects.filter(
                    student=profile
                ).count()
            except:
                pass
        
        elif user.type in ['teacher', 'support_teacher']:
            try:
                profile = user.teacher_profile
                # Teacher stats
                context['groups'] = Group.objects.filter(teacher=profile)
                context['total_homeworks'] = Homework.objects.filter(
                    teacher=profile
                ).count()
            except:
                pass
        
        context['profile'] = profile
        
        return context


class AdminUserEditView(AdminRequiredMixin, UpdateView):
    """
    Foydalanuvchini tahrirlash
    """
    model = User
    template_name = 'admin/users/edit.html'
    fields = ['first_name', 'last_name', 'email', 'type', 'is_active']
    
    def get_success_url(self):
        return reverse('admin_panel:user_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(
            self.request,
            f"✅ Foydalanuvchi yangilandi: {form.instance.email}"
        )
        
        logger.info(f"User updated by admin: {form.instance.email}")
        
        return super().form_valid(form)


class AdminUserDeleteView(AdminRequiredMixin, DeleteView):
    """
    Foydalanuvchini o'chirish
    """
    model = User
    template_name = 'admin/users/delete_confirm.html'
    success_url = reverse_lazy('admin_panel:user_list')
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        email = user.email
        
        messages.success(
            request,
            f"✅ Foydalanuvchi o'chirildi: {email}"
        )
        
        logger.warning(f"User deleted by admin: {email}")
        
        return super().delete(request, *args, **kwargs)


class AdminUserBulkActionView(AdminRequiredMixin, View):
    """
    Bulk actions for users
    """
    def post(self, request):
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')
        
        if not user_ids:
            messages.warning(request, "⚠️ Foydalanuvchi tanlanmagan")
            return redirect('admin_panel:user_list')
        
        users = User.objects.filter(id__in=user_ids)
        
        if action == 'delete':
            count = users.count()
            users.delete()
            messages.success(request, f"✅ {count} ta foydalanuvchi o'chirildi")
            
        elif action == 'activate':
            users.update(is_active=True)
            messages.success(request, f"✅ Foydalanuvchilar aktivlashtirildi")
            
        elif action == 'deactivate':
            users.update(is_active=False)
            messages.success(request, f"✅ Foydalanuvchilar deaktivlashtirildi")
        
        return redirect('admin_panel:user_list')


# ============================================================================
# PLACEHOLDER VIEWS (Same as before)
# ============================================================================

class AdminCourseListView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/courses/list.html'

class AdminCourseCreateView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/courses/create.html'

class AdminCourseDetailView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/courses/detail.html'

class AdminCourseEditView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/courses/edit.html'

class AdminCourseDeleteView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/courses/delete_confirm.html'

class AdminGroupListView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/groups/list.html'

# ================ABDUJABBOR=============================================================
class AdminGroupCreateView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/groups/create.html'

    def get(self, request):
        form = GroupForm()
        return self.render_to_response({'form':form})

    def post(self, request):
        form = GroupForm(request.POST)
        if form.is_valid():
            new_group = form.save()
            return redirect('admin_panel:group_detail', pk=new_group.pk)

        return  self.render_to_response({'form':form})

class AdminGroupDetailView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/groups/detail.html'
    

    def get(self, pk):
        group = Group.objects.get(pk=pk)
        return self.render_to_response({'group':group})

class AdminGroupEditView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/groups/edit.html'

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        form = GroupUpdateForm(instance=group)
        return self.render_to_response({"form": form, 'group': group})

    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        form = GroupUpdateForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:group_detail', pk=pk)



class AdminGroupDeleteView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/groups/delete_confirm.html'
    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        return self.render_to_response({'group':group})

    def post(self, request, pk):
        grou = Group.objects.get(pk=pk)
        grou.delete()
        return redirect('admin_panel:group_list')

class AdminGroupEnrollView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/groups/enroll.html'

    def get(self, request):
        form = GroupAddStudentsForm()
        return self.render_to_response({'from': form})

    def post(self, request):
        form = GroupAddStudentsForm(request.POST)
        if form.is_valid():
            new_student = form.save()
            return redirect('admin_panel:group_enroll', pk=new_student.pk)

        return self.render_to_response({'from': form})

class AdminGroupRemoveStudentView(AdminRequiredMixin, View):

    def get(self, request, pk):
        student = StudentProfile.objects.get(pk=pk)
        return self.render_to_response({'student': student})

    def post(self, request, pk):
        messages.info(request, "Studentni chopamiz!")
        stud = StudentProfile.objects.get(pk=pk)
        stud.delete()
        return redirect('admin_panel:user_list', pk=group_pk)

class AdminReportsView(AdminRequiredMixin, TemplateView):
    template_name = 'admin/reports/overview.html'

    def get(self, request):
        from django.contrib.auth import get_user_model
        from django.db.models import Count
        from academics.models import Course, Group, Enrollment

        User = get_user_model()

        # ========= USER ANALYTICS =========
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()

        new_users_week = User.objects.filter(
            date_joined__gte=datetime.now() - timedelta(days=7)
        ).count()

        # ========= COURSE ANALYTICS =========
        total_courses = Course.objects.count()
        published_courses = Course.objects.filter(is_published=True).count()

        course_enrollment_counts = (
            Course.objects.annotate(students=Count("enrollment")).order_by("-students")
        )

        # Top 5 popular courses
        top_courses = course_enrollment_counts[:5]

        no_student_courses = course_enrollment_counts.filter(students=0).count()

        # ========= GROUP ANALYTICS =========
        total_groups = Group.objects.count()

        group_sizes = (
            Group.objects.annotate(students=Count("students")).order_by("-students")
        )

        empty_groups = group_sizes.filter(students=0).count()

        # ========= ENROLLMENT ANALYTICS =========
        total_enrollments = Enrollment.objects.count()

        enrollments_last_30_days = Enrollment.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=30)
        ).count()

        # ========= ACTIVITY HEATMAP (optional) =========
        daily_signup_data = (
            User.objects
            .extra(select={'day': "date(date_joined)"})
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        context = {
            # Users
            "total_users": total_users,
            "active_users": active_users,
            "staff_users": staff_users,
            "new_users_week": new_users_week,

            # Courses
            "total_courses": total_courses,
            "published_courses": published_courses,
            "top_courses": top_courses,
            "no_student_courses": no_student_courses,

            # Groups
            "total_groups": total_groups,
            "empty_groups": empty_groups,

            # Enrollments
            "total_enrollments": total_enrollments,
            "enrollments_last_30_days": enrollments_last_30_days,

            # Charts
            "daily_signup_data": list(daily_signup_data),
        }

        return self.render_to_response(context)



# ==========NURMUHAMMAAD==================================
class AdminExportView(AdminRequiredMixin, View):
    def get(self, request, export_type):
        messages.info(request, f"Export {export_type} - Coming soon")
        return redirect('admin_panel:reports')