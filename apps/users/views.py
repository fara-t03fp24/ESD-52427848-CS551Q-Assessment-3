from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
import logging
import os
from .forms import UserRegistrationForm, UserUpdateForm, CustomAuthenticationForm

logger = logging.getLogger(__name__)


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
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
            
            # Redirect to the page user was trying to access, or to products list
            next_url = request.GET.get('next')
            if next_url and next_url.startswith('/'):  # Only redirect to internal URLs
                return redirect(next_url)
            return redirect('products:product_list')
    else:
        form = CustomAuthenticationForm()
        
        # If user was redirected to login, show a message
        if request.GET.get('next'):
            messages.info(request, 'Please log in to access that page.')
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out. Come back soon to discover more amazing 3D models!')
    return redirect('products:product_list')


@login_required
def profile_update(request):
    if request.method == 'POST':
        logger.info(f"FILES: {request.FILES}")
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            if 'avatar' in request.FILES:
                avatar_file = request.FILES['avatar']
                logger.info(f"Processing avatar file: {avatar_file.name}")
                
                # Delete old avatar if it exists
                if request.user.avatar:
                    try:
                        old_path = request.user.avatar.path
                        if os.path.exists(old_path):
                            os.remove(old_path)
                            logger.info(f"Deleted old avatar: {old_path}")
                    except Exception as e:
                        logger.error(f"Error deleting old avatar: {e}")

                # Save new avatar
                try:
                    file_name = f"users/avatars/{request.user.id}_{avatar_file.name}"
                    file_path = default_storage.save(file_name, avatar_file)
                    logger.info(f"Saved new avatar to: {file_path}")
                    
                    # Update user model
                    request.user.avatar = file_path
                    request.user.save()
                except Exception as e:
                    logger.error(f"Error saving new avatar: {e}")
                    messages.error(request, "There was an error uploading your profile picture. Please try again.")
                    return redirect('users:profile')

            form.save()
            messages.success(request, 'Your 3D printing marketplace profile has been updated!')
            return redirect('users:profile')
        else:
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
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