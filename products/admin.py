from django.contrib import admin
from .models import Product, BestSelling, Notification


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'regular_price', 'offer_price', 'stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'stock']
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category', 'image')
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
    readonly_fields = ['created_at', 'updated_at']


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
