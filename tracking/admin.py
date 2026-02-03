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
    save_on_top = True  # Puts "Save" / "Save and continue" at the top of the add/edit form
    fieldsets = (
        (None, {
            'fields': ('name', 'script_id', 'provider', 'placement', 'order', 'is_active'),
        }),
        ('Script content', {
            'fields': ('script_content', 'noscript_content'),
            'description': 'Paste only the inner JavaScript in Script content (do not include the outer script tags). Optional noscript fallback HTML in Noscript content.',
        }),
    )
