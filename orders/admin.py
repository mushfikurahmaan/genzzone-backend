from django.contrib import admin
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem
from .steadfast_service import SteadfastService
import logging

logger = logging.getLogger(__name__)


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
    list_display = ['id', 'customer_name', 'customer_email', 'total_amount', 'status', 'get_steadfast_status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'session_key', 'steadfast_tracking_code']
    readonly_fields = ['session_key', 'created_at', 'updated_at', 'steadfast_consignment_id', 'steadfast_tracking_code', 'steadfast_status']
    inlines = [OrderItemInline]
    list_editable = ['status']
    fieldsets = (
        ('Order Information', {
            'fields': ('status', 'total_amount', 'session_key')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip', 'shipping_country')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Steadfast Integration', {
            'fields': ('steadfast_consignment_id', 'steadfast_tracking_code', 'steadfast_status'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_steadfast_status(self, obj):
        """Display Steadfast status in list view"""
        if obj.steadfast_consignment_id:
            return f"Sent (ID: {obj.steadfast_consignment_id})"
        return "Not Sent"
    get_steadfast_status.short_description = 'Steadfast Status'
    get_steadfast_status.admin_order_field = 'steadfast_consignment_id'

    actions = ['send_to_steadfast']

    def send_to_steadfast(self, request, queryset):
        """Admin action to send selected orders to Steadfast"""
        success_count = 0
        error_count = 0
        
        for order in queryset:
            # Check if order is already sent to Steadfast
            if order.steadfast_consignment_id:
                self.message_user(
                    request,
                    f"Order #{order.id} has already been sent to Steadfast (Consignment ID: {order.steadfast_consignment_id})",
                    level=messages.WARNING
                )
                error_count += 1
                continue
            
            # Prepare item description from order items
            item_descriptions = []
            total_lot = 0
            
            for order_item in order.items.all():
                item_desc = f"{order_item.quantity}x {order_item.product.name}"
                if order_item.product_size:
                    item_desc += f" (Size: {order_item.product_size})"
                item_descriptions.append(item_desc)
                total_lot += order_item.quantity
            
            item_description = "; ".join(item_descriptions)
            
            # Create invoice ID from order ID
            invoice = f"ORD-{order.id}"
            
            # Send order to Steadfast
            steadfast_service = SteadfastService()
            
            steadfast_response = steadfast_service.create_order(
                invoice=invoice,
                recipient_name=order.customer_name,
                recipient_phone=order.customer_phone,
                recipient_address=order.shipping_address,
                cod_amount=float(order.total_amount),
                recipient_email=order.customer_email if order.customer_email else None,
                note=order.notes if order.notes else None,
                item_description=item_description,
                total_lot=total_lot,
                delivery_type=0  # 0 for home delivery
            )
            
            # Update order with Steadfast tracking information if successful
            if steadfast_response.get('status') == 200 and steadfast_response.get('consignment'):
                consignment = steadfast_response['consignment']
                order.steadfast_consignment_id = consignment.get('consignment_id')
                order.steadfast_tracking_code = consignment.get('tracking_code', '')
                order.steadfast_status = consignment.get('status', '')
                order.status = 'processing'  # Update order status to processing
                order.save()
                logger.info(f"Order {order.id} successfully sent to Steadfast with consignment ID {order.steadfast_consignment_id}")
                success_count += 1
            else:
                error_message = steadfast_response.get('message', 'Unknown error')
                logger.warning(f"Failed to send order {order.id} to Steadfast: {error_message}")
                self.message_user(
                    request,
                    f"Failed to send Order #{order.id} to Steadfast: {error_message}",
                    level=messages.ERROR
                )
                error_count += 1
        
        # Show summary message
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully sent {success_count} order(s) to Steadfast.",
                level=messages.SUCCESS
            )
        if error_count > 0 and success_count == 0:
            self.message_user(
                request,
                f"Failed to send {error_count} order(s) to Steadfast. Please check the error messages above.",
                level=messages.ERROR
            )
    
    send_to_steadfast.short_description = "Send selected orders to Steadfast"
