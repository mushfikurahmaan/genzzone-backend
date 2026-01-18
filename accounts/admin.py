from django.contrib import admin
from django.contrib.admin import actions
from .models import LoginLog


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for LoginLog model.
    Deletion is disabled to preserve login history.
    """
    list_display = [
        'user',
        'login_time',
        'ip_address',
        'operating_system',
        'browser',
        'browser_version',
        'device',
    ]
    list_filter = [
        'login_time',
        'operating_system',
        'browser',
    ]
    search_fields = [
        'user__username',
        'user__email',
        'ip_address',
        'operating_system',
        'browser',
    ]
    readonly_fields = [
        'user',
        'login_time',
        'ip_address',
        'operating_system',
        'browser',
        'browser_version',
        'device',
        'user_agent',
    ]
    date_hierarchy = 'login_time'
    ordering = ['-login_time']

    def has_add_permission(self, request):
        """Disable manual addition of login logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deletion of login logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing of login logs."""
        return False

    def get_actions(self, request):
        """Remove delete action from admin."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
