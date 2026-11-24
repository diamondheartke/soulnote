from django.db import models
from django.contrib.auth.models import User

class ChatEntry(models.Model):
	chat_history = (
		User,
		on_delete=models.CASCADE,
		related_name='chat_history'
	)
	
	content = models.TextField()
