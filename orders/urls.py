from django.urls import path
from .views import (
    CreateOrderView, CartView, AddToCartView,
    UpdateCartItemView, RemoveCartItemView,
    SendOrderToSteadfastView
)

urlpatterns = [
    path('api/orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('api/cart/', CartView.as_view(), name='cart'),
    path('api/cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('api/cart/items/<int:item_id>/', UpdateCartItemView.as_view(), name='update-cart-item'),
    path('api/cart/items/<int:item_id>/remove/', RemoveCartItemView.as_view(), name='remove-cart-item'),
    path('api/admin/orders/<int:order_id>/send-to-steadfast/', SendOrderToSteadfastView.as_view(), name='send-order-to-steadfast'),
]
