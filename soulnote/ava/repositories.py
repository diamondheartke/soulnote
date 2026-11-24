
# ava/repositories.py

from django.utils import timezone
from .models import ConversationHistory, Message


class ConversationRepository:

    def __init__(self, user):
        self.user = user

    def create_conversation(self, title="New chat"):
        return ConversationHistory.objects.create(
            user=self.user,
            title=title
        )

    def create_message(self, conversation, role, content):

        if conversation.user_id != self.user.pk:
            raise PermissionError(
                "You cannot modify another user's conversation."
            )

        try:
            role = Message.Role(role)
        except ValueError as exc:
            raise ValueError(
                f"{role} is not a recognised role!"
            ) from exc

        content = content.strip()

        if not content:
            raise ValueError("Message content cannot be empty.")

        message = Message.objects.create(
            conversation=conversation,
            role=role,
            content=content
        )

        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['updated_at'])

        return message

    def get_messages(self, conversation):

        if conversation.user_id != self.user.pk:
            raise PermissionError(
                "You cannot access another user's conversation."
            )

        return conversation.messages.all()

    def get_conversations(self):
        return self.user.conversations.all()
