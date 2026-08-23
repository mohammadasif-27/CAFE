from django.shortcuts import render

def dashboard(request):
    return render(request, "staff/dashboard.html")

def add_food(request):
    return render(request, "staff/add_food.html")
