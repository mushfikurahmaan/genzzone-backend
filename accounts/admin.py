from django.contrib import admin
from django.contrib.admin import actions
from django.contrib.auth.models import User, Group
from .models import LoginLog

try:
    admin.site.unregister(User)
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


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


_original_get_app_list = admin.AdminSite.get_app_list


def _custom_get_app_list(self, request, app_label=None):
    from django.urls import reverse
    app_list = _original_get_app_list(self, request, app_label)

    security_app = {
        'name': 'Security',
        'app_label': 'security',
        'app_url': '#',
        'has_module_perms': True,
        'models': [{
            'name': 'Change Password',
            'object_name': 'ChangePassword',
            'perms': {'add': False, 'change': True, 'delete': False, 'view': False},
            'admin_url': reverse('admin:password_change'),
            'add_url': None,
            'view_only': False,
        }],
    }

    app_dict = {app['app_label']: app for app in app_list}
    ordered = []
    if 'products' in app_dict:
        ordered.append(app_dict['products'])
    ordered.append(security_app)
    if 'accounts' in app_dict:
        ordered.append(app_dict['accounts'])
    for app in app_list:
        if app['app_label'] not in ('products', 'accounts'):
            ordered.append(app)

    return ordered


admin.AdminSite.get_app_list = _custom_get_app_list
