from django.db import models


class TrackingCode(models.Model):
    """Stores the tracking pixel/script to inject (e.g. Meta Pixel). Paste the full code here."""

    script_content = models.TextField(
        blank=True,
        help_text='Paste your tracking code (e.g. Meta Pixel). You can include <script> tags; they will be stripped before injection.',
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
