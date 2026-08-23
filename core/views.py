from django.shortcuts import render

from menu.models import Food


def home(request):
    foods = Food.objects.filter(available=True)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        print(name, email, phone, message)

    return render(request, "home.html", {"foods": foods})