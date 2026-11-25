# ava/services/conversation_service.py

from django.conf import settings
from django.db import transaction

from ava.models import Message
from ava.repositories import ConversationRepository
from ava.services.ai_service import AvaAIService


class ConversationServiceError(Exception):
	"""Base exception for conversation service failures."""
	pass

class AvaGenerationError(ConversationServiceError):
	"""Raised when inference fails after the user's message is saved."""

	def __init__(self, message, conversation, user_message):
		super().__init__(message)
		self.conversation = conversation
		self.user_message = user_message

class ConversationNotFoundError(ConversationServiceError):
	"""Raised when a conversation doesn't exist or isn't owned by the user."""
	pass


class ConversationService:
	HISTORY_LIMIT = 20

	def __init__(self, user):
		if not user or not user.is_authenticated:
			raise ConversationServiceError(
				"An authenticated user is required."
			)

		self.user = user
		self.repository = ConversationRepository(user)
		self.ai_service = AvaAIService()

		self.system_prompt = getattr(
			settings,
			"AVA_SYSTEM_PROMPT",
			(
				"You are Ava, the reflective AI companion in SoulNote. "
				"Respond naturally, thoughtfully and conversationally. "
				"Listen carefully, acknowledge emotions and ask meaningful "
				"questions when appropriate. Do not expose internal reasoning."
			)
		)

	def send_message(self, user_input, conversation_uuid=None):
		"""
		Save a user's message, generate Ava's response,
		and persist the assistant response.
		"""

		user_input = (user_input or "").strip()

		if not user_input:
			raise ConversationServiceError(
				"Message content cannot be empty."
			)

		# Retrieve an existing conversation or create a new one.
		if conversation_uuid:
			try:
				conversation = self.repository.get_conversations().get(
					conversation_uuid=conversation_uuid
				)
			except (
				self.repository.get_conversations().model.DoesNotExist,
				ValueError,
				TypeError
			):
				raise ConversationNotFoundError(
					"Conversation not found."
				)
		else:
			conversation = None

		# Persist the conversation and user's message.
		with transaction.atomic():

			if conversation is None:
				conversation = self.repository.create_conversation(
					title=user_input[:60]
				)

			user_message = self.repository.create_message(
				conversation=conversation,
				role=Message.Role.USER,
				content=user_input
			)

		# Retrieve recent conversation history.
		history = list(
			self.repository.get_messages(conversation)
		)[-self.HISTORY_LIMIT:]

		# Construct the model's conversational context.
		messages = [
			{
				"role": "system",
				"content": self.system_prompt
			}
		]

		for message in history:
			if message.role in (
				Message.Role.USER,
				Message.Role.ASSISTANT
			):
				messages.append({
					"role": message.role,
					"content": message.content
				})

		# Generate Ava's response outside the database transaction.
		try:
			assistant_response = self.ai_service.generate_response(
				messages
			)

		except Exception as error:
		    raise AvaGenerationError(
				"Your message was saved, but Ava could not generate a response.",
				conversation=conversation,
				user_message=user_message
			) from error

		# Persist Ava's response.
		with transaction.atomic():

			assistant_message = self.repository.create_message(
				conversation=conversation,
				role=Message.Role.ASSISTANT,
				content=assistant_response
			)

		return {
			"conversation_uuid": str(conversation.conversation_uuid),
			"user_message": user_message,
			"assistant_message": assistant_message,
			"reply": assistant_response
		}
