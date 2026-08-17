from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import RegisterForm, ProfileUpdateForm


def register_view(request):
	if request.user.is_authenticated:
		return redirect('home')

	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.first_name = form.cleaned_data.get('first_name')
			user.last_name = form.cleaned_data.get('last_name')
			user.email = form.cleaned_data.get('email')
			user.save()
			messages.success(request, 'Account created successfully. Please log in.')
			return redirect('accounts:login')
		else:
			messages.error(request, 'Please correct the errors below.')
	else:
		form = RegisterForm()

	return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
	if request.user.is_authenticated:
		return redirect('home')

	next_url = request.GET.get('next') or request.POST.get('next') or ''
	if request.method == 'POST':
		# support both 'login' (template) and legacy 'identifier' keys
		identifier = request.POST.get('login', request.POST.get('identifier', '')).strip()
		password = request.POST.get('password', '')

		user = None
		# allow login with email or username
		if '@' in identifier:
			try:
				u = User.objects.get(email__iexact=identifier)
				user = authenticate(request, username=u.username, password=password)
			except User.DoesNotExist:
				user = None
		else:
			user = authenticate(request, username=identifier, password=password)

		if user is not None:
			login(request, user)
			messages.success(request, 'Welcome back to CafeHub!')
			if next_url:
				return redirect(next_url)
			return redirect('home')
		else:
			messages.error(request, 'Invalid username or password.')

	return render(request, 'accounts/login.html', {'next': next_url})


def logout_view(request):
	logout(request)
	messages.success(request, 'You have been logged out successfully.')
	return redirect('home')


@login_required
def profile_view(request):
	orders_count = request.user.orders.count()
	completed_orders = request.user.orders.filter(status='completed').count()
	pending_orders = request.user.orders.filter(status='pending').count()
	recent_orders = request.user.orders.order_by('-created_at')[:5]

	return render(request, 'accounts/profile.html', {
		'orders_count': orders_count,
		'completed_orders': completed_orders,
		'pending_orders': pending_orders,
		'recent_orders': recent_orders,
	})


@login_required
def edit_profile_view(request):
	if request.method == 'POST':
		form = ProfileUpdateForm(request.POST, instance=request.user, user=request.user)
		if form.is_valid():
			form.save()
			messages.success(request, 'Profile updated successfully.')
			return redirect('accounts:profile')
		else:
			messages.error(request, 'Please correct the details below.')
	else:
		form = ProfileUpdateForm(instance=request.user, user=request.user)

	return render(request, 'accounts/edit_profile.html', {'form': form})
