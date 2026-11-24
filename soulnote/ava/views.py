# ava/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ChatEntryForm
from .models import ConversationHistory, Message
from .repositories import ConversationRepository


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
    
@login_required
@require_POST
def submit_message(request):
    form = ChatEntryForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {
                'success': False,
                'errors': form.errors.get_json_data(),
            },
            status=400
        )

    content = form.cleaned_data['user_input']

    conversation_uuid = request.POST.get('conversation_uuid')

    repository = ConversationRepository(request.user)

	# Note to self:
	# transaction.atomic() makes conversation creation and message creation one database transaction. 
	#If the message save fails, the new conversation is rolled back too.
    with transaction.atomic():

        if conversation_uuid:
            conversation = get_object_or_404(
                ConversationHistory,
                conversation_uuid=conversation_uuid,
                user=request.user
            )
        else:
            # Use the first message as the initial conversation title.
            title = content.strip()[:60]

            conversation = repository.create_conversation(
                title=title or "New chat"
            )

        message = repository.create_message(
            conversation=conversation,
            role=Message.Role.USER,
            content=content
        )

    return JsonResponse({
        'success': True,

        'message': {
            'id': message.id,
            'role': message.role,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
        },

        'conversation': {
            'uuid': str(conversation.conversation_uuid),
            'title': conversation.title,
            'url': reverse(
                'ava:conversation',
                kwargs={
                    'conversation_uuid': conversation.conversation_uuid
                }
            ),
        }
    })
