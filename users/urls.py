from django.urls import path
from . import views
from .views import * 

app_name = 'dashboard'

urlpatterns = [
    # Authentication URLs
    path('', landing_page, name='landing'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard-redirect/', dashboard_redirect, name='dashboard-redirect'),

]