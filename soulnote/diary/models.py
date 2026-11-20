from django.db import models
from django.contrib.auth.models import User

class DiaryEntry(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	
	content = models.TextField()
	detected_emotions = models.CharField(max_length=50, blank=True, null=True)
	ai_reflection = models.TextField(blank=True, null=True)
	
	ip_address = models.GenericIPAddressField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		# Orders queries newest-first by default
		ordering = ['-created_at']
		verbose_name_plural = "Diary Entries"
		
	def __str__(self):
		# Controls how the entry is labeled in Django's admin panel and shell
		return f"Entry from {self.created_at.strftime('%Y-%m-%d %H:%M')}"
