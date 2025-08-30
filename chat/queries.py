# apps/chat/queries.py
from django.db.models import OuterRef, Subquery, Count, Q, Max, DateTimeField, F, ExpressionWrapper
from django.db.models.functions import Coalesce
from .models import Conversation, ConversationParticipant, Message

# apps/chat/queries.py
from django.db.models import OuterRef, Subquery, F
from django.contrib.auth import get_user_model

User = get_user_model()

def conversations_with_last_and_unread(user):
    my_participant = ConversationParticipant.objects.filter(
        conversation=OuterRef('pk'), user=user
    ).values('last_read_at')[:1]

    unread = Message.objects.filter(
        conversation=OuterRef('pk'),
        created_at__gt=Subquery(my_participant),
    ).exclude(sender=user).values('conversation').annotate(
        c=Count('id')
    ).values('c')[:1]

    # Get the other participant's ID
    other_participant = ConversationParticipant.objects.filter(
        conversation=OuterRef('pk')
    ).exclude(user=user).values('user_id')[:1]

    qs = Conversation.objects.filter(
        participants__user=user
    ).select_related('last_message').annotate(
        my_last_read_at=Subquery(my_participant),
        unread_count=Coalesce(Subquery(unread), 0),
        last_message_text=F('last_message__body'),
        last_message_at=F('last_message__created_at'),
        last_message_sender_id=F('last_message__sender_id'),
        other_user_id=Subquery(other_participant),
    ).order_by('-last_message_at', '-updated_at')

    return qs
