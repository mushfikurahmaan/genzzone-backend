from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginLog(models.Model):
    """
    Model to track user login history with OS and browser information.
    This model cannot be deleted from the admin panel.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_logs',
        verbose_name='User'
    )
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Login Time'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Address'
    )
    operating_system = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Operating System'
    )
    browser = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Browser'
    )
    browser_version = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='Browser Version'
    )
    device = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Device'
    )
    user_agent = models.TextField(
        blank=True,
        default='',
        verbose_name='User Agent String'
    )

    class Meta:
        verbose_name = 'Login Log'
        verbose_name_plural = 'Login Logs'
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} - {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}"

    def delete(self, *args, **kwargs):
        """Prevent deletion of login logs."""
        raise PermissionError("Login logs cannot be deleted.")
