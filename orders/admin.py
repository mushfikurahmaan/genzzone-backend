from django.contrib import admin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem
from .steadfast_service import SteadfastService
import logging

logger = logging.getLogger(__name__)


class UsedStatusFilter(admin.SimpleListFilter):
    """Filter that only shows statuses that are actually used in orders"""
    title = _('status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        # Get only statuses that exist in the database
        used_statuses = Order.objects.values_list('status', flat=True).distinct()
        status_choices = dict(Order.STATUS_CHOICES)
        return [(status, status_choices.get(status, status)) for status in used_statuses if status in status_choices]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


# Cart admin removed - not needed in admin panel
# CartItemInline and CartAdmin classes removed


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['created_at', 'subtotal_display']
    fields = ['product', 'quantity', 'price', 'product_size', 'subtotal_display', 'created_at']
    
    def subtotal_display(self, obj):
        """Display subtotal for order item"""
        if obj.pk:
            return f"৳{obj.get_subtotal():.2f}"
        return "-"
    subtotal_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'customer_phone', 'total_amount', 'status', 'get_steadfast_status', 'get_item_count', 'created_at']
    list_display_links = ['customer_name']
    list_filter = [UsedStatusFilter, 'created_at', 'shipping_state']
    search_fields = ['customer_name', 'customer_email', 'customer_phone', 'session_key', 'steadfast_tracking_code', 'id']
    readonly_fields = ['session_key', 'created_at', 'updated_at', 'steadfast_consignment_id', 'steadfast_tracking_code', 'steadfast_status', 'status']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('total_amount',)
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip', 'shipping_country')
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

    def get_item_count(self, obj):
        """Display total number of items in order"""
        total_quantity = sum(item.quantity for item in obj.items.all())
        item_count = obj.items.count()
        return f"{item_count} item(s), {total_quantity} total"
    get_item_count.short_description = 'Items'

    actions = ['confirm_order', 'discard_order', 'send_to_steadfast']

    def confirm_order(self, request, queryset):
        """Admin action to confirm order and send to Steadfast"""
        success_count = 0
        error_count = 0
        
        for order in queryset:
            # Check if order is already cancelled
            if order.status == 'cancelled':
                self.message_user(
                    request,
                    f"Order #{order.id} is already cancelled and cannot be confirmed.",
                    level=messages.WARNING
                )
                error_count += 1
                continue
            
            # Check if order is already sent to Steadfast
            if order.steadfast_consignment_id:
                self.message_user(
                    request,
                    f"Order #{order.id} has already been sent to Steadfast (Consignment ID: {order.steadfast_consignment_id})",
                    level=messages.WARNING
                )
                error_count += 1
                continue
            
            # Check if order has items
            if not order.items.exists():
                self.message_user(
                    request,
                    f"Order #{order.id} has no items and cannot be confirmed.",
                    level=messages.ERROR
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
                note=None,
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
                order.status = 'sent'  # Update order status to sent
                order.save()
                logger.info(f"Order {order.id} successfully confirmed and sent to Steadfast with consignment ID {order.steadfast_consignment_id}")
                success_count += 1
            else:
                error_message = steadfast_response.get('message', 'Unknown error')
                logger.warning(f"Failed to confirm order {order.id} and send to Steadfast: {error_message}")
                self.message_user(
                    request,
                    f"Failed to confirm Order #{order.id} and send to Steadfast: {error_message}",
                    level=messages.ERROR
                )
                error_count += 1
        
        # Show summary message
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully confirmed and sent {success_count} order(s) to Steadfast.",
                level=messages.SUCCESS
            )
        if error_count > 0 and success_count == 0:
            self.message_user(
                request,
                f"Failed to confirm {error_count} order(s). Please check the error messages above.",
                level=messages.ERROR
            )
    
    confirm_order.short_description = "Confirm Order (Send to Steadfast)"

    def discard_order(self, request, queryset):
        """Admin action to discard/cancel orders"""
        discarded_count = 0
        skipped_count = 0
        
        for order in queryset:
            # Check if order is already sent to Steadfast
            if order.steadfast_consignment_id:
                self.message_user(
                    request,
                    f"Order #{order.id} has already been sent to Steadfast and cannot be discarded.",
                    level=messages.WARNING
                )
                skipped_count += 1
                continue
            
            # Update order status to cancelled
            order.status = 'cancelled'
            order.save()
            logger.info(f"Order {order.id} has been discarded (cancelled)")
            discarded_count += 1
        
        # Show summary message
        if discarded_count > 0:
            self.message_user(
                request,
                f"Successfully discarded {discarded_count} order(s).",
                level=messages.SUCCESS
            )
        if skipped_count > 0:
            self.message_user(
                request,
                f"Skipped {skipped_count} order(s) that were already sent to Steadfast.",
                level=messages.WARNING
            )
    
    discard_order.short_description = "Discard Order (Cancel)"

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
                note=None,
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
                order.status = 'sent'  # Update order status to sent
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
