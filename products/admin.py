from django.contrib import admin
from django.utils.html import format_html
from .models import Product, BestSelling, Notification


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'regular_price', 'offer_price', 'stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'stock']
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category', 'image', 'image_preview')
        }),
        ('Pricing', {
            'fields': ('regular_price', 'offer_price'),
            'description': 'Set regular_price (required). Set offer_price (optional) to show a discounted price.'
        }),
        ('Inventory', {
            'fields': ('stock', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'image_preview']

    def image_preview(self, obj):
        """Display image preview in admin panel"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border: 1px solid #ddd; border-radius: 4px; padding: 5px; background: #fff;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image uploaded</span>')
    
    image_preview.short_description = 'Image Preview'


@admin.register(BestSelling)
class BestSellingAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__name', 'product__description']
    list_editable = ['order', 'is_active']
    fieldsets = (
        ('Best Selling Configuration', {
            'fields': ('product', 'order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['message', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['message']
    list_editable = ['is_active']
    fieldsets = (
        ('Notification Message', {
            'fields': ('message', 'is_active'),
            'description': 'Only one notification can be active at a time. Activating a notification will deactivate others.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
