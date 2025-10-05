from django.contrib import admin
from .models import Payment, Expense


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'amount', 'payment_date', 'payment_method', 'status', 'recorded_by', 'approved_by')
    list_filter = ('payment_method', 'status', 'payment_date')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'recorded_by__username')
    ordering = ('-payment_date',)

    def student_name(self, obj):
        return obj.student.user.get_full_name()
    student_name.short_description = 'Student'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'date', 'added_by')
    list_filter = ('date',)
    search_fields = ('category', 'added_by__username')
    ordering = ('-date',)
