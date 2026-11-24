# ava/repositories.py
 
from ava.models import ConversationHistory, Message
from django.utils import timezone
 
class ConversationRepository:
	def __init__(self, user):
		self.user = user
		
	def create_conv(self, title="New Chat"):
		conversation = ConversationHistory.objects.create(
			user=self.user,
			title=title
		)

		return conversation
		
	def create_message(self, conversation, role, content):
		if role.lower() in ('assistant', 'user', 'tool', 'system'):
			pass
		else:
			raise ValueError(f"{role} is not a recognised role!")
			
		if conversation.user_id != self.user.pk:
			raise PermissionError("You cannot modify another user's conversation.")
			
		content = content.strip()
		if not content:
			raise ValueError("Message content cannot be empty.")
		
		Message = Message.objects.create(
			conversation=self.conv,
			role=Message.Role(role),
			content=content
		)
		
		# update time stamp
		conversation.updated_at = timezone.now()
		conversation.save(updated_fields=['updated_at'])
		
		return Message
		
	def get_messages(self, conversation):
		if conversation.user_id != self.user.pk:
			raise PermissionError("You cannot access another user's conversation.")
			
		history = conversation.Message.all()
		
		return history
		
	def get_conversations(self):
		return self.user.conversations.all()
