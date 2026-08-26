from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import RegisterForm, ProfileUpdateForm
from .models import Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():

            # Get account type and owner code
            account_type = request.POST.get('account_type')
            owner_code = request.POST.get('owner_code')

            # Check owner code
            if account_type == "owner" and owner_code != "1234":
                messages.error(request, "Wrong Owner Access Code!")
                return render(request, "accounts/register.html", {"form": form})

            # Create user
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.save()

            # Create profile
            Profile.objects.create(
                user=user,
                account_type=account_type
            )

            messages.success(request, "Account created successfully. Please log in.")
            return redirect('accounts:login')

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        identifier = request.POST.get('login')
        password = request.POST.get('password')

        user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back!")

            # Owner -> Dashboard
            if user.profile.account_type == "owner":
                return redirect("home")

            # Customer -> Home
            return redirect('home')

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            instance=request.user,
            user=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')

    else:
        form = ProfileUpdateForm(
            instance=request.user,
            user=request.user
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {"form": form}
    )