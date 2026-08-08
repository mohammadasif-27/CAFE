from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from menu.models import Food
from .models import CartItem, Order, OrderItem

DELIVERY_FEE = Decimal('40.00')


def _add_food_to_cart(user, food):
    cart_item, created = CartItem.objects.get_or_create(user=user, food=food)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return cart_item


def _generate_order_number(order_id):
    return f"CAF-{order_id:04d}"


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


@login_required(login_url='accounts:login')
def update_cart_item(request, item_id):
    if request.method != 'POST':
        return redirect('orders:cart')

    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    action = request.POST.get('action')

    if action == 'increment':
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Increased quantity for {cart_item.food.name}.")
    elif action == 'decrement':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f"Decreased quantity for {cart_item.food.name}.")
        else:
            cart_item.delete()
            messages.success(request, f"Removed {cart_item.food.name} from your cart.")
    elif action == 'remove':
        cart_item.delete()
        messages.success(request, f"Removed {cart_item.food.name} from your cart.")

    return redirect('orders:cart')


@login_required(login_url='accounts:login')
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('food')
    if not cart_items.exists():
        messages.info(request, 'Your cart is empty. Add items before checking out.')
        return redirect('orders:cart')

    subtotal = sum(item.subtotal for item in cart_items)
    total = subtotal + DELIVERY_FEE
    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': DELIVERY_FEE,
        'total': total,
    })


@login_required(login_url='accounts:login')
def place_order(request):
    if request.method != 'POST':
        return redirect('orders:checkout')

    cart_items = CartItem.objects.filter(user=request.user).select_related('food')
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty. Please add items before placing an order.')
        return redirect('orders:cart')

    for item in cart_items:
        if not item.food.available:
            messages.error(request, f"{item.food.name} is no longer available.")
            return redirect('orders:cart')

    subtotal = sum(item.subtotal for item in cart_items)
    total = subtotal + DELIVERY_FEE

    customer_name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    city = request.POST.get('city', '').strip()
    pincode = request.POST.get('pincode', '').strip()

    if not all([customer_name, phone, address, city, pincode]):
        messages.error(request, 'Please complete all delivery details before placing your order.')
        return redirect('orders:checkout')

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            order_number='TEMP',
            customer_name=customer_name,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode,
            subtotal=subtotal,
            delivery_fee=DELIVERY_FEE,
            total=total,
        )
        order.order_number = _generate_order_number(order.id)
        order.save(update_fields=['order_number'])

        order_items = []
        for item in cart_items:
            order_items.append(OrderItem(
                order=order,
                food=item.food,
                quantity=item.quantity,
                price=item.food.price,
                subtotal=item.subtotal,
            ))
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()

    messages.success(request, f"Your order {order.order_number} has been placed successfully.")
    return redirect('orders:order_success', order_number=order.order_number)


@login_required(login_url='accounts:login')
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required(login_url='accounts:login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/my_orders.html', {'orders': orders})
