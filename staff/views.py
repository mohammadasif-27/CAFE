from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import ProtectedError, Sum
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from accounts.models import Profile
from core.models import ContactMessage
from menu.models import Food
from orders.models import Order
from .forms import FoodForm


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        is_owner = Profile.objects.filter(
            user=request.user,
            account_type="owner",
        ).exists()
        if not (request.user.is_staff or is_owner):
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)

    return wrapped_view


@staff_required
def dashboard(request):
    completed_sales = Order.objects.filter(
        status=Order.STATUS_COMPLETED,
    ).aggregate(total=Sum("total"))["total"] or 0

    return render(request, "staff/dashboard.html", {
        "total_foods": Food.objects.count(),
        "available_foods": Food.objects.filter(available=True).count(),
        "total_orders": Order.objects.count(),
        "pending_orders": Order.objects.filter(status=Order.STATUS_PENDING).count(),
        "total_customers": Profile.objects.filter(account_type="customer").count(),
        "completed_sales": completed_sales,
        "foods": Food.objects.all().order_by("-created_at"),
        "orders": Order.objects.select_related("user").all(),
        "contact_messages": ContactMessage.objects.all()[:50],
    })


@staff_required
def add_food(request):
    form = FoodForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
    )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Food added successfully!")
            return redirect("add_food")

    return render(request, "staff/add_food.html", {"form": form})


@staff_required
def edit_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    form = FoodForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=food,
    )

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Food updated successfully!")
            return redirect("edit_food", food_id=food.id)

    return render(request, "staff/edit_food.html", {"food": food, "form": form})


@staff_required
def delete_food(request, food_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    food = get_object_or_404(Food, id=food_id)
    try:
        food.delete()
    except ProtectedError:
        messages.error(request, "This food is part of order history; mark it unavailable instead.")
    else:
        messages.success(request, "Food deleted successfully.")
    return redirect("dashboard")


@staff_required
def complete_order(request, order_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    order = get_object_or_404(Order, id=order_id)
    if order.status == Order.STATUS_PENDING:
        order.status = Order.STATUS_COMPLETED
        order.save(update_fields=["status", "updated_at"])
        messages.success(request, f"Order {order.order_number} marked completed.")
    else:
        messages.info(request, f"Order {order.order_number} is already completed.")
    return redirect("dashboard")