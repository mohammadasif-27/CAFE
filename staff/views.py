from django.shortcuts import render, redirect
from menu.models import Food


def dashboard(request):
    return render(request, "staff/dashboard.html")


def add_food(request):
    if request.method == "POST":
        Food.objects.create(
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            category=request.POST.get("category"),
            price=request.POST.get("price"),
            available=True,
            image=request.POST.get("image")
        )

        return redirect("add_food")   # Reloads the page after saving

    return render(request, "staff/add_food.html")