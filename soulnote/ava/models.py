# ava/models.py

import uuid

from django.db import models
from django.contrib.auth.models import User

class ConversationHistory(models.Model):
	conversation_uuid = models.UUIDField(
		default=uuid.uuid4,
		editable=False,
		unique=True
	)
	
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='conversations'
	)
	
	title = models.CharField(max_length=150, blank=False, default="New chat", null=False)
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['-updated_at']
		verbose_name="Conversation"
		verbose_name_plural = "Conversations"
		
	def __str__(self):
		return (
			f"{self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
		)
		
class Message(models.Model):
	class Role(models.TextChoices):
		USER='user', 'User'
		ASSISTANT='assistant', 'Assistant'
		SYSTEM='system', 'System'
		TOOL='tool', 'Tool'
		
	conversation = models.ForeignKey(
		ConversationHistory,
		on_delete=models.CASCADE,
		related_name='messages',
	)
		
	role = models.CharField(max_length=10, choices=Role.choices, blank=False, null=False)
	content = models.TextField(blank=False, null=False)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering=['created_at'] # oldest first
		verbose_name='Message'
		verbose_name_plural='Messages'
	
	def __str__(self):
		return f"{self.role}: {self.content[:50]}"
