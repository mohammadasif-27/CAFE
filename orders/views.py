from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from menu.models import Food
from .models import CartItem


def _add_food_to_cart(user, food):
    cart_item, created = CartItem.objects.get_or_create(user=user, food=food)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return cart_item


@login_required(login_url='accounts:login')
def add_to_cart(request, food_id):
    if request.method != 'POST':
        return redirect(request.META.get('HTTP_REFERER', reverse('home')))

    food = get_object_or_404(Food, id=food_id, available=True)
    _add_food_to_cart(request.user, food)

    messages.success(request, f"Added {food.name} to your cart.")
    return redirect(request.META.get('HTTP_REFERER', reverse('home')))


@login_required(login_url='accounts:login')
def order_now(request, food_id):
    if request.method != 'POST':
        return redirect(request.META.get('HTTP_REFERER', reverse('home')))

    food = get_object_or_404(Food, id=food_id, available=True)
    _add_food_to_cart(request.user, food)

    messages.success(request, f"{food.name} is now in your cart. Proceed to checkout.")
    return redirect('orders:cart')


@login_required(login_url='accounts:login')
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('food')
    total = sum(item.subtotal for item in cart_items)
    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })
