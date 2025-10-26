def user_context(request):
    """
    User role va permissions haqida ma'lumot.
    
    Usage in templates:
        {{ user_role }}
        {{ is_student }}
        {{ is_teacher }}
        {{ is_admin }}
    """
    if not request.user.is_authenticated:
        return {}
    
    user = request.user
    
    return {
        'user_role': user.type,
        'user_type_display': user.get_type_display(),
        'is_student': user.type == 'student',
        'is_teacher': user.type in ['teacher', 'support_teacher'],
        'is_admin': user.type in ['admin', 'manager', 'super_user'],
        'is_superuser': user.is_superuser,
        'notification_count': 0,  # Hozircha 0, keyinchalik real data
    }