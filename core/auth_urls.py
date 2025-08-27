from django.urls import path

from users.api.api import RegisterAPIView, LogoutView

app_name = 'auth_urls'

urlpatterns = [
    path("register/", RegisterAPIView.as_view()),
    path("logout/", LogoutView.as_view()),
]
