# diary/urls.py

from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import home_view, register_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', LoginView.as_view(template_name='diary/login.html'), name='login'),
    
    # LogoutView logs out and redirects to LOGOUT_REDIRECT_URL
    path('logout/', LogoutView.as_view(), name='logout'),
]
