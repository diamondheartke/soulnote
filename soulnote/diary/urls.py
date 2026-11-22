# diary/urls.py

from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import RedirectView
from .views import home_view, register_view, landing_view, diary_view

urlpatterns = [
    path('home/', home_view, name='home'),
    path('', RedirectView.as_view(pattern_name='home', permanent=False), name='root'),
    path('landing-page/', landing_view, name='landing'),
    path('register/', register_view, name='register'),
    path('login/', LoginView.as_view(template_name='diary/login.html'), name='login'),
    path('diary-space', diary_view, name='diary-space'),
    
    # LogoutView logs out and redirects to LOGOUT_REDIRECT_URL
    path('logout/', LogoutView.as_view(), name='logout'),
]
