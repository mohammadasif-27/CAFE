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

def edit_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)

    if request.method == "POST":
        food.name = request.POST.get("name")
        food.description = request.POST.get("description")
        food.category = request.POST.get("category")
        food.price = request.POST.get("price")

        if request.FILES.get("image"):
            food.image = request.FILES.get("image")

        food.save()

        return redirect("dashboard")

    return render(request, "staff/edit_food.html", {"food": food})