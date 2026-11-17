from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.utils import timezone
from accounts.models import Profile
from menu.models import Food
from orders.models import Order


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
    today = timezone.localdate()
    today_sales = Order.objects.filter(
        status=Order.STATUS_COMPLETED,
        created_at__date=today,
    ).aggregate(total=Sum("total"))["total"] or 0

    return render(request, "staff/dashboard.html", {
        "total_foods": Food.objects.count(),
        "available_foods": Food.objects.filter(available=True).count(),
        "total_orders": Order.objects.count(),
        "pending_orders": Order.objects.filter(status=Order.STATUS_PENDING).count(),
        "total_customers": Profile.objects.filter(account_type="customer").count(),
        "today_sales": today_sales,
        "foods": Food.objects.all().order_by("-created_at"),
        "orders": Order.objects.select_related("user").all(),
    })


@staff_required
def add_food(request):
    if request.method == "POST":
        Food.objects.create(
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            category=request.POST.get("category"),
            price=request.POST.get("price"),
            available=True,
            image=request.FILES.get("image")
        )

        messages.success(request, "Food added successfully!")
        return redirect("add_food")

    return render(request, "staff/add_food.html")


@staff_required
def edit_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)

    if request.method == "POST":
        food.name = request.POST.get("name")
        food.description = request.POST.get("description")
        food.category = request.POST.get("category")
        food.price = request.POST.get("price")

        if request.FILES.get("image"):
            food.image = request.FILES["image"]

        food.save()

        messages.success(request, "Food updated successfully!")
        return redirect("edit_food", food_id=food.id)

    return render(request, "staff/edit_food.html", {"food": food})