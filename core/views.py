from django.shortcuts import render

from menu.models import Food


def home(request):
    foods = Food.objects.filter(available=True)
    return render(request, "home.html", {"foods": foods})