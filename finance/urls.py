# finance/urls.py
"""
Finance URLs - To'lovlar va xarajatlar
"""
from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Payments - Admin
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/approve/', views.PaymentApproveView.as_view(), name='payment_approve'),
    
    # Expenses - Admin
    path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expenses/create/', views.ExpenseCreateView.as_view(), name='expense_create'),
    
    # Student Payment History
    path('my-payments/', views.StudentPaymentHistoryView.as_view(), name='my_payments'),
]