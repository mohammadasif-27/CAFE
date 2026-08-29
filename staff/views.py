from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from menu.models import Food


@login_required
def dashboard(request):
    return render(request, "staff/dashboard.html")


@login_required
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


@login_required
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