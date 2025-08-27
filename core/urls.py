# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog, set_language
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.api.api import CustomTokenObtainPairView, CustomTokenRefreshView


urlpatterns = [
    # Admin
    path(settings.ADMIN_URL, admin.site.urls),
    
    # APIs
    path(f"api/auth/", include("core.auth_urls")),
    path(f"api/token/", CustomTokenObtainPairView.as_view(), name="refresh_token"),
    path(f"api/token/refresh", CustomTokenRefreshView.as_view(), name="obtain_auth_token"),
    path(f"api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(f"api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
    
    # homepage
    # path("", include("project.urls")),
    
]
