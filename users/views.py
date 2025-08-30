from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from typing import Dict, Any
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

def landing_page(request):
    """
    Landing page that shows login form or redirects to API docs if authenticated.
    """
    if request.user.is_authenticated:
        return redirect('/api/docs/')
    
    return render(request, 'index.html')

@csrf_protect
def login_view(request):
    """
    Handle user login with proper error handling and security.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'dashboard/landing.html')
        
        try:
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Log successful login
                    logger.info(f"User {email} logged in successfully")
                    
                    # Update IP address if provided
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0].strip()
                    else:
                        ip = request.META.get('REMOTE_ADDR')
                    
                    if ip and ip != user.ip_address:
                        user.ip_address = ip
                        user.save(update_fields=['ip_address'])
                    
                    # Redirect to API docs
                    next_url = request.GET.get('next', '/api/docs/')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Your account is disabled. Please contact support.')
            else:
                messages.error(request, 'Invalid email or password.')
                logger.warning(f"Failed login attempt for email: {email}")
        
        except Exception as e:
            logger.error(f"Login error for {email}: {str(e)}")
            messages.error(request, 'An error occurred during login. Please try again.')
    
    return render(request, 'dashboard/landing.html')

@login_required
def logout_view(request):
    """
    Handle user logout and redirect to landing page.
    """
    user_email = request.user.email if request.user.is_authenticated else "Unknown"
    logout(request)
    logger.info(f"User {user_email} logged out")
    messages.success(request, 'You have been successfully logged out.')
    return redirect('dashboard:landing')

@login_required
def dashboard_redirect(request):
    """
    Redirect authenticated users to API docs.
    """
    return redirect('/api/docs/')