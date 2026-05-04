from django.urls import path
from .views import AddToCartView, CartView, RemoveFromCartView, CheckoutView, CreateOrderView

app_name = 'marketplace'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout_page'),
    path('order/create/', CreateOrderView.as_view(), name='create_order'),
]
