from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class LoginRequiredMiddleware:
    """
    Middleware that requires authentication for API documentation access.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs that require authentication
        self.protected_urls = [
            '/api/docs/',
            '/api/schema/',
        ]
        
        # URLs that don't require authentication
        self.exempt_urls = [
            '/',
            '/login/',
            '/logout/',
            '/admin/',
        ]
    
    def __call__(self, request):
        # Check if URL requires authentication
        requires_auth = any(
            request.path.startswith(protected_url) 
            for protected_url in self.protected_urls
        )
        
        # Check if URL is exempt from authentication
        is_exempt = any(
            request.path.startswith(exempt_url) 
            for exempt_url in self.exempt_urls
        )
        
        if requires_auth and not request.user.is_authenticated:
            logger.info(f"Redirecting unauthenticated user from {request.path} to login")
            return redirect(f"{reverse('dashboard:landing')}?next={request.path}")
        
        response = self.get_response(request)
        return response