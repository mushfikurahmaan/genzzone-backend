from django.db import models


class TrackingCode(models.Model):
    """Stores the tracking pixel/script to inject (e.g. Meta Pixel). Paste the full code here."""

    script_content = models.TextField(
        blank=True,
        help_text='Paste the full pixel code (e.g. Meta Pixel: comments, <script> and <noscript>). Rendered on the frontend as-is.',
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
