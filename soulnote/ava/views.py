# ava/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .repositories import ConversationRepository

@login_required
def ava_chat_view(request):
	"""
	Renders Ava's conversational interface.

	Authentication is required because Ava is a private
	companion inside the SoulNote application.
	"""
	repository = ConversationRepository(request.user)
	
	active_conversation = None
	messages = []
	
	messages=repository.get_messages(active_conversation)
	
	context = {
		'user': request.user,
		'conversations': repository.get_conversations(),
		'active_conversation': active_conversation,
		'messages': messages,
	}

	return render(request, 'ava/index.html', context)
