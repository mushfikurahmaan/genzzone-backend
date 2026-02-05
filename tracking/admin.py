from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import TrackingCode


@admin.register(TrackingCode)
class TrackingCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'updated_at']
    list_editable = ['is_active']
    list_filter = ['is_active']
    save_on_top = True
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 18, 'cols': 80, 'style': 'font-family: monospace;'})},
    }
    fieldsets = (
        (None, {
            'fields': ('script_content', 'is_active'),
            'description': (
                'Paste your full pixel code here (e.g. Meta Pixel). Include everything: comments, '
                '<script>...</script> and <noscript>...</noscript>. It will be rendered on the frontend as-is.'
            ),
        }),
    )
