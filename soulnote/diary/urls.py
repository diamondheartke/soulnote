# diary/urls.py

from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import RedirectView
from .views import (
					home_view, 
					register_view, 
					landing_view, 
					diary_view, 
					settings_view, 
					delete_account_view, 
					export_data_view,
					import_data_view,
				)

urlpatterns = [
    path('home/', home_view, name='home'),
    path('', RedirectView.as_view(pattern_name='home', permanent=False), name='root'),
    path('landing-page/', landing_view, name='landing'),
    path('register/', register_view, name='register'),
    path('login/', LoginView.as_view(template_name='diary/login.html'), name='login'),
    path('diary-space', diary_view, name='diary-space'),
    path('settings/', settings_view, name='settings'),
    
    # ---- Delete Account view ----
    path('delete-account', delete_account_view, name='delete-account'),
    
    # ---- Data export view ----
    path('export-data', export_data_view, name='export-data'),
    
    # ---- Data import view ----
    path('import-data', import_data_view, name='import-data'),
    
    # LogoutView logs out and redirects to LOGOUT_REDIRECT_URL
    path('logout/', LogoutView.as_view(), name='logout'),
]
