from django.db import models


class TrackingCode(models.Model):
    """Stores third-party tracking scripts (e.g. Meta Pixel, Google Analytics) to be injected in the frontend."""

    PLACEMENT_CHOICES = [
        ('head', 'Head'),
        ('body', 'Body'),
    ]

    name = models.CharField(max_length=100, help_text='Display name (e.g. Meta Pixel)')
    script_id = models.SlugField(
        max_length=100,
        unique=True,
        help_text='Unique ID for the script tag (e.g. meta-pixel). Used as the script element id.',
    )
    provider = models.CharField(
        max_length=50,
        blank=True,
        help_text='Provider name (e.g. facebook, google) for reference.',
    )
    script_content = models.TextField(
        help_text='JavaScript code to run inside a script tag. Do not include <script> tags.',
    )
    noscript_content = models.TextField(
        blank=True,
        help_text='Optional HTML for <noscript> fallback (e.g. tracking pixel img).',
    )
    placement = models.CharField(
        max_length=10,
        choices=PLACEMENT_CHOICES,
        default='body',
        help_text='Where to inject the script in the page.',
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Order when multiple tracking codes are present (lower first).',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Tracking code'
        verbose_name_plural = 'Tracking codes'

    def __str__(self):
        return self.name
