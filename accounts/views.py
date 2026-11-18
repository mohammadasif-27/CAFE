from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseNotAllowed
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import RegisterForm, ProfileUpdateForm
from .models import Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():

            # Get account type and owner code
            account_type = form.cleaned_data['account_type']
            owner_code = request.POST.get('owner_code')

            # Check owner code
            if account_type == "owner" and (
                not settings.OWNER_ACCESS_CODE
                or owner_code != settings.OWNER_ACCESS_CODE
            ):
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

    next_url = request.POST.get('next') or request.GET.get('next', '')
    if request.method == 'POST':
        identifier = request.POST.get('login')
        password = request.POST.get('password')

        user = authenticate(request, username=identifier, password=password)
        if user is None and identifier:
            matching_users = User.objects.filter(email__iexact=identifier)
            if matching_users.count() == 1:
                user = authenticate(
                    request,
                    username=matching_users.get().username,
                    password=password,
                )

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back!")

            pending_action = request.session.pop('pending_cart_action', None)
            if isinstance(pending_action, dict):
                from menu.models import Food
                from orders.services import add_food_to_cart

                food_id = pending_action.get('food_id')
                action = pending_action.get('action')
                food = None
                if isinstance(food_id, int) and action in {'add', 'order_now'}:
                    food = Food.objects.filter(id=food_id, available=True).first()

                if food is None:
                    messages.error(request, "That menu item is no longer available.")
                    return redirect('home')
                else:
                    add_food_to_cart(user, food, request=request)
                    messages.success(request, f"Added {food.name} to your cart.")
                    return redirect('orders:cart')

            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            profile = Profile.objects.filter(user=user).first()
            if user.is_staff or (profile and profile.account_type == "owner"):
                return redirect("dashboard")

            return redirect('home')

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html", {"next": next_url})


def logout_view(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


@login_required
def profile_view(request):
    from orders.models import Order

    orders = Order.objects.filter(user=request.user)
    return render(request, "accounts/profile.html", {
        "orders_count": orders.count(),
        "completed_orders": orders.filter(status=Order.STATUS_COMPLETED).count(),
        "pending_orders": orders.filter(status=Order.STATUS_PENDING).count(),
        "recent_orders": orders[:5],
    })


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