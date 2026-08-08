from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/order/<int:food_id>/', views.order_now, name='order_now'),
]
