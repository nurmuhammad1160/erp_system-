# finance/views.py
"""
Finance Views - To'lovlar va xarajatlar boshqaruvi
"""
import logging
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.db.models import Sum, Q
from accounts.mixins import AdminRequiredMixin, StudentRequiredMixin
from accounts.models import StudentProfile
from .models import Payment, Expense
from .forms import PaymentForm, ExpenseForm

logger = logging.getLogger(__name__)


# ============================================================================
# PAYMENT VIEWS
# ============================================================================

class PaymentListView(AdminRequiredMixin, ListView):
    """
    Barcha to'lovlarni ko'rish (Admin)
    """
    model = Payment
    template_name = 'finance/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        return Payment.objects.select_related(
            'student__user',
            'recorded_by',
            'approved_by__user'
        ).order_by('-payment_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistika
        context['total_amount'] = Payment.objects.filter(
            status='approved'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        context['pending_amount'] = Payment.objects.filter(
            status='pending'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        context['pending_count'] = Payment.objects.filter(
            status='pending'
        ).count()
        
        return context


class PaymentCreateView(AdminRequiredMixin, CreateView):
    """
    Yangi to'lov qo'shish
    """
    model = Payment
    form_class = PaymentForm
    template_name = 'finance/payment_create.html'
    success_url = reverse_lazy('finance:payment_list')
    
    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.recorded_by = self.request.user
        payment.status = 'pending'
        payment.save()
        
        messages.success(
            self.request,
            f"To'lov {payment.amount} so'm qo'shildi. Tasdiqlashni kutmoqda."
        )
        
        logger.info(
            f"To'lov yaratildi: {payment.amount}",
            extra={'user_id': self.request.user.id, 'payment_id': payment.id}
        )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "To'lovni qo'shishda xatolik."
        )
        return super().form_invalid(form)


class PaymentApproveView(AdminRequiredMixin, UpdateView):
    """
    To'lovni tasdiqlash
    """
    model = Payment
    fields = []  # Hech qanday maydon tahrirlash yo'q
    template_name = 'finance/payment_approve.html'
    success_url = reverse_lazy('finance:payment_list')
    
    def post(self, request, *args, **kwargs):
        payment = self.get_object()
        
        if payment.status == 'approved':
            messages.warning(request, "Bu to'lov allaqachon tasdiqlangan.")
            return redirect('finance:payment_list')
        
        # To'lovni tasdiqlash
        payment.status = 'approved'
        payment.approved_by = request.user.admin_profile
        payment.save()
        
        # Talaba balansini yangilash
        student = payment.student
        student.credit(payment.amount)
        
        messages.success(
            request,
            f"To'lov {payment.amount} so'm tasdiqlandi."
        )
        
        logger.info(
            f"To'lov tasdiqlandi: {payment.id}",
            extra={
                'user_id': request.user.id,
                'payment_id': payment.id,
                'student_id': student.id
            }
        )
        
        return redirect('finance:payment_list')


# ============================================================================
# EXPENSE VIEWS
# ============================================================================

class ExpenseListView(AdminRequiredMixin, ListView):
    """
    Barcha xarajatlarni ko'rish
    """
    model = Expense
    template_name = 'finance/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 20
    
    def get_queryset(self):
        return Expense.objects.select_related(
            'added_by'
        ).order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistika
        context['total_expenses'] = Expense.objects.aggregate(
            Sum('amount')
        )['amount__sum'] or 0
        
        return context


class ExpenseCreateView(AdminRequiredMixin, CreateView):
    """
    Yangi xarajat qo'shish
    """
    model = Expense
    form_class = ExpenseForm
    template_name = 'finance/expense_create.html'
    success_url = reverse_lazy('finance:expense_list')
    
    def form_valid(self, form):
        expense = form.save(commit=False)
        expense.added_by = self.request.user
        expense.save()
        
        messages.success(
            self.request,
            f"Xarajat {expense.category}: {expense.amount} so'm qo'shildi."
        )
        
        logger.info(
            f"Xarajat qo'shildi: {expense.category}",
            extra={'user_id': self.request.user.id, 'expense_id': expense.id}
        )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Xarajatni qo'shishda xatolik."
        )
        return super().form_invalid(form)


# ============================================================================
# STUDENT PAYMENT VIEWS
# ============================================================================

class StudentPaymentHistoryView(StudentRequiredMixin, ListView):
    """
    O'quvchining o'z to'lovlar tarixi
    """
    model = Payment
    template_name = 'student/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 10
    
    def get_queryset(self):
        student = self.request.user.student_profile
        return Payment.objects.filter(
            student=student
        ).order_by('-payment_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        
        context['student'] = student
        context['total_paid'] = Payment.objects.filter(
            student=student,
            status='approved'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        return context