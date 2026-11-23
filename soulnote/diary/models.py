# diary/models.py

import uuid

from django.db import models
from django.contrib.auth.models import User

class DiaryEntry(models.Model):
	entry_uuid = models.UUIDField(
		default=uuid.uuid4,
		editable=False,
		null=True
	)
	
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diary_entries')
	
	content = models.TextField()
	detected_emotions = models.CharField(max_length=50, blank=True, null=True)
	ai_reflection = models.TextField(blank=True, null=True)
	
	ip_address = models.GenericIPAddressField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		# Orders queries newest-first by default
		ordering = ['-created_at']
		verbose_name_plural = "Diary Entries"
		
		constraints = [
			models.UniqueConstraint(
				fields=['user', 'entry_uuid'],
				name='unique_entry_uuid_per_user'
			)
		]
		
	def __str__(self):
		# Controls how the entry is labeled in Django's admin panel and shell
		return f"Entry from {self.created_at.strftime('%Y-%m-%d %H:%M')}"
		

class DiaryEntryRevision(models.Model):
    entry = models.ForeignKey(
        DiaryEntry,
        on_delete=models.CASCADE,
        related_name='revisions'
    )

    revision_number = models.PositiveIntegerField()

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['revision_number']
        constraints = [
            models.UniqueConstraint(
                fields=['entry', 'revision_number'],
                name='unique_diary_entry_revision'
            )
        ]
        verbose_name = 'Diary Entry Revision'
        verbose_name_plural = 'Diary Entry Revisions'

    def __str__(self):
        return (
            f"Revision {self.revision_number} "
            f"of entry {self.entry.entry_uuid}"
        )

