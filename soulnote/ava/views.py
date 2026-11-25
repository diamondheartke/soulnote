# ava/views.py

import logging

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ChatEntryForm
from .models import ConversationHistory
from .repositories import ConversationRepository

from .services.conversation_service import (
    ConversationService,
    ConversationServiceError,
    ConversationNotFoundError,
    AvaGenerationError,
)


logger = logging.getLogger(__name__)


def serialize_message(message):
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
    }


def serialize_conversation(conversation):
    return {
        "uuid": str(conversation.conversation_uuid),
        "title": conversation.title,
        "url": reverse(
            "ava:conversation",
            kwargs={
                "conversation_uuid": conversation.conversation_uuid
            }
        ),
    }


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
        "user": request.user,
        "conversations": conversations,
        "active_conversation": active_conversation,
        "messages": messages,
    }

    return render(request, "ava/index.html", context)


@login_required
@require_POST
def submit_message(request):

    form = ChatEntryForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {
                "success": False,
                "errors": form.errors.get_json_data(),
            },
            status=400
        )

    content = form.cleaned_data["user_input"]

    conversation_uuid = (
        request.POST.get("conversation_uuid") or None
    )

    try:

        service = ConversationService(request.user)

        result = service.send_message(
            user_input=content,
            conversation_uuid=conversation_uuid
        )

        conversation = result["assistant_message"].conversation

        return JsonResponse({
            "success": True,

            "message": serialize_message(
                result["user_message"]
            ),

            "assistant_message": serialize_message(
                result["assistant_message"]
            ),

            "conversation": serialize_conversation(
                conversation
            ),
        })

    except ConversationNotFoundError as error:

        return JsonResponse(
            {
                "success": False,
                "error": str(error),
            },
            status=404
        )

    except AvaGenerationError as error:

        # The user's message was saved, even though inference failed.
        return JsonResponse(
            {
                "success": False,
                "error": str(error),

                "message": serialize_message(
                    error.user_message
                ),

                "conversation": serialize_conversation(
                    error.conversation
                ),
            },
            status=502
        )

    except ConversationServiceError as error:

        return JsonResponse(
            {
                "success": False,
                "error": str(error),
            },
            status=400
        )

    except Exception:

        logger.exception("Unexpected error while processing Ava message.")

        return JsonResponse(
            {
                "success": False,
                "error": "An unexpected error occurred while processing your message.",
            },
            status=500
        )
