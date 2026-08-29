from django.shortcuts import render, redirect
from .models import Review
from menu.models import Food

def home(request):
    foods = Food.objects.filter(available=True)
    reviews = Review.objects.all().order_by("-created_at")

    if request.method == "POST":

        if request.user.is_authenticated:

            Review.objects.create(
                user=request.user,
                rating=request.POST.get("rating"),
                message=request.POST.get("review"),
            )

        return redirect("home")

    return render(request, "home.html", {
        "foods": foods,
        "reviews": reviews,
    })