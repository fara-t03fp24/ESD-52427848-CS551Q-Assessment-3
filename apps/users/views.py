from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserUpdateForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_seller = form.cleaned_data.get('is_seller', False)
            user.save()
            auth_login(request, user)
            messages.success(request, 'Welcome to our 3D printing marketplace! Your account has been created successfully.')
            if user.is_seller:
                messages.info(request, 'Since you registered as a seller, you can now create your shop!')
                return redirect('products:shop_create')
            return redirect('products:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'Welcome back to the 3D printing marketplace!')
            next_url = request.GET.get('next', 'products:product_list')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out. Come back soon to discover more amazing 3D models!')
    return redirect('products:product_list')


@login_required
def profile_update(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your 3D printing marketplace profile has been updated!')
            return redirect('users:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated successfully. Your 3D printing account is now more secure!')
            return redirect('users:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/password_change.html', {'form': form})


@login_required
@require_POST
def become_seller(request):
    user = request.user
    if not user.is_seller:
        user.is_seller = True
        user.save()
        messages.success(request, 'You are now registered as a seller! Create your shop to start selling.')
        return redirect('products:shop_create')
    return redirect('users:profile')