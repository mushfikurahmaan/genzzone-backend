from django.contrib import admin
from .models import Product, BestSelling, Notification, Category, ProductColor, HeroImage


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    fields = ['name', 'image', 'order', 'is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order', 'is_active', 'created_at']
    list_filter = ['parent', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'slug', 'parent', 'order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            # Only show parent categories (those without a parent) as options
            kwargs["queryset"] = Category.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'regular_price', 'offer_price', 'stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'stock']
    inlines = [ProductColorInline]
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Product Images', {
            'fields': ('image', 'image2', 'image3', 'image4'),
            'description': 'Upload up to 4 product images. The first image is the main/primary image.'
        }),
        ('Pricing', {
            'fields': ('regular_price', 'offer_price'),
            'description': 'Set regular_price (required). Set offer_price (optional) to show a discounted price.'
        }),
        ('Inventory', {
            'fields': ('stock', 'is_active')
        }),
        ('Size options', {
            'fields': ('size_options',),
            'description': 'JSON array of size dimensions, e.g. [{"label": "Shirt Size", "options": ["S", "M", "L"]}, {"label": "Pants Size", "options": ["28", "30", "32"]}]. Leave empty for default "Size: One Size".'
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


@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'subtitle', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    list_editable = ['is_active']
    fieldsets = (
        ('Hero Image', {
            'fields': ('image', 'title', 'subtitle', 'is_active'),
            'description': 'Upload the hero banner image for your homepage. Only one hero image can be active at a time.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
