# soulnote/urls.py

from django.contrib import admin
from django.urls import path, include  

urlpatterns = [
    path('admin/', admin.site.urls),
    # Main SoulNote Application
    path('', include('diary.urls')),  # Routes root URL to our diary app
    # Ava AI Companion
    path('ava-companion', include('ava.urls')),
]
