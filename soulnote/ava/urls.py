# ava/urls.py

from django.urls import path
from .views import ava_chat_view, submit_message

app_name = 'ava'

urlpatterns = [
	path('', ava_chat_view, name='chat'),
	path('messages/', submit_message, name='submit-message'),
	path('<uuid:conversation_uuid>/', ava_chat_view, name='conversation'),
]
