# ava/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .repositories import ConversationRepository
from .models import ConversationHistory


@login_required
def ava_chat_view(request, conversation_uuid=None):
    repository = ConversationRepository(request.user)

    conversations = repository.get_conversations()

    active_conversation = None
    messages = []

    if conversation_uuid:
        active_conversation = get_object_or_404(
            ConversationHistory,
            conversation_uuid=conversation_uuid,
            user=request.user
        )

        messages = repository.get_messages(active_conversation)

    context = {
        'user': request.user,
        'conversations': conversations,
        'active_conversation': active_conversation,
        'messages': messages,
    }

    return render(
        request,
        'ava/index.html',
        context
    )
