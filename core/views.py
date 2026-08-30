from django.shortcuts import render, redirect
from menu.models import Food
from .models import Review


def home(request):
    foods = Food.objects.filter(available=True)
    reviews = Review.objects.all()

    return render(request, "home.html", {
        "foods": foods,
        "reviews": reviews,
    })


def add_review(request):
    if request.method == "POST" and request.user.is_authenticated:

        Review.objects.create(
            user=request.user,
            rating=request.POST.get("rating"),
            message=request.POST.get("review"),
        )

    return redirect("home")