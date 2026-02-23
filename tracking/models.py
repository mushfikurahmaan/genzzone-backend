from django.db import models


class TrackingCode(models.Model):
    """Stores the Meta (Facebook) Pixel ID for frontend tracking."""

    pixel_id = models.CharField(
        max_length=50,
        blank=True,
        help_text='Meta (Facebook) Pixel ID (e.g. 1234567890123456).',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Tracking code'
        verbose_name_plural = 'Tracking codes'

    def __str__(self):
        return f"Tracking code #{self.id}"
