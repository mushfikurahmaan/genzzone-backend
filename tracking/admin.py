from django.contrib import admin
from .models import TrackingCode


@admin.register(TrackingCode)
class TrackingCodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'script_id', 'provider', 'placement', 'order', 'is_active', 'updated_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'placement', 'provider']
    search_fields = ['name', 'script_id', 'provider']
    prepopulated_fields = {'script_id': ('name',)}
    ordering = ['order', 'name']
