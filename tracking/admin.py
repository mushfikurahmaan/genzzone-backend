from django.contrib import admin
from .models import TrackingCode


@admin.register(TrackingCode)
class TrackingCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'pixel_id', 'is_active', 'updated_at']
    list_editable = ['is_active']
    list_filter = ['is_active']
    save_on_top = True
    fields = ('pixel_id', 'is_active')
