from django.contrib import admin
from .models import TrackingCode


@admin.register(TrackingCode)
class TrackingCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'updated_at']
    list_editable = ['is_active']
    list_filter = ['is_active']
    save_on_top = True
    fieldsets = (
        (None, {
            'fields': ('script_content', 'is_active'),
            'description': 'Paste your tracking code (e.g. Meta Pixel). You can include <script> tags.',
        }),
    )
