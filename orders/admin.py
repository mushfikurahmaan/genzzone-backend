from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'get_item_count', 'get_total', 'created_at', 'updated_at']
    readonly_fields = ['session_key', 'created_at', 'updated_at']
    inlines = [CartItemInline]

    def get_item_count(self, obj):
        return obj.get_item_count()
    get_item_count.short_description = 'Item Count'

    def get_total(self, obj):
        return f"${obj.get_total():.2f}"
    get_total.short_description = 'Total'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_email', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'session_key']
    readonly_fields = ['session_key', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    list_editable = ['status']
