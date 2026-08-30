from django.shortcuts import render, redirect, get_object_or_404
from .models import Review
from menu.models import Food


def home(request):
    foods = Food.objects.filter(available=True)
    reviews = Review.objects.all().order_by("-created_at")

    return render(request, "home.html", {
        "foods": foods,
        "reviews": reviews,
    })


def add_review(request):
    if request.method == "POST" and request.user.is_authenticated:

        food = get_object_or_404(
            Food,
            id=request.POST.get("food_id")
        )

        Review.objects.create(
            user=request.user,
            food=food,
            rating=request.POST.get("rating"),
            message=request.POST.get("review"),
        )

    return redirect("home")