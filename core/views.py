from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from accounts.models import Profile
from activity_tracking.models import CustomerActivity
from activity_tracking.services import record_activity
from menu.models import Food
from .forms import ContactForm, ReviewForm
from .models import ContactMessage, Review


def home(request):
    if request.user.is_authenticated and (
        request.user.is_staff
        or Profile.objects.filter(
            user=request.user,
            account_type="owner",
        ).exists()
    ):
        return redirect("dashboard")

    contact_form = ContactForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and contact_form.is_valid():
        with transaction.atomic():
            ContactMessage.objects.create(**contact_form.cleaned_data)
            record_activity(
                request,
                CustomerActivity.CONTACT,
                page='Contact',
            )
        messages.success(request, "Your message has been sent to CafeHub.")
        return redirect(f"{reverse('home')}#contact")

    foods = Food.objects.filter(available=True)
    reviews = Review.objects.select_related("user").all()

    return render(request, "home.html", {
        "foods": foods,
        "reviews": reviews,
        "contact_form": contact_form,
    })


def add_review(request):
    if request.method == "POST" and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                user=request.user,
                rating=form.cleaned_data["rating"],
                message=form.cleaned_data["message"],
            )
            messages.success(request, "Thank you for your review.")
        else:
            messages.error(request, "Please provide a rating from 1 to 5 and a valid review.")

    return redirect("home")