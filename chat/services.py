# apps/chat/services.py
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .models import Conversation, ConversationParticipant, Message

def get_or_create_conversation(user_a, user_b):
    if user_a == user_b:
        raise ValueError("Cannot start a conversation with yourself.")
    # find conversation with both users
    qs = Conversation.objects.filter(
        participants__user=user_a
    ).filter(
        participants__user=user_b
    ).distinct()

    if qs.exists():
        return qs.first(), False

    with transaction.atomic():
        conv = Conversation.objects.create()
        ConversationParticipant.objects.create(conversation=conv, user=user_a)
        ConversationParticipant.objects.create(conversation=conv, user=user_b)
        return conv, True

def send_message(conversation, sender, body):
    msg = Message.objects.create(conversation=conversation, sender=sender, body=body)
    Conversation.objects.filter(pk=conversation.pk).update(last_message=msg, updated_at=timezone.now())
    return msg

def mark_conversation_opened(conversation, user):
    # Resets unread by moving the pointer
    ConversationParticipant.objects.filter(
        conversation=conversation, user=user
    ).update(last_read_at=timezone.now())
