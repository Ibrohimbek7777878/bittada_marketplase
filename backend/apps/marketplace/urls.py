from django.urls import path
from .views import (
    AddToCartView, 
    CartView, 
    RemoveFromCartView, 
    CheckoutView, 
    CreateOrderView,
    CartItemDetailView
)

app_name = 'marketplace'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/item/<int:pk>/', CartItemDetailView.as_view(), name='cart_item_detail'),
    path('checkout/', CheckoutView.as_view(), name='checkout_page'),
    path('order/create/', CreateOrderView.as_view(), name='create_order'),
]
