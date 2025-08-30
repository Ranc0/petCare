# apps/chat/api/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, ConversationParticipant
from .serializers import ConversationListSerializer, MessageSerializer
from .services import get_or_create_conversation, send_message, mark_conversation_opened
from .queries import conversations_with_last_and_unread

class ConversationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationListSerializer

    def get_queryset(self):
        return conversations_with_last_and_unread(self.request.user)


class ConversationCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        other_username = request.data.get('username')
        if not other_username:
            return Response({"detail": "user_username is required"}, status=400)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_user = get_object_or_404(User, username=other_username)
        conv, created = get_or_create_conversation(request.user, other_user)
        return Response({"conversation_id": conv.id, "created": created})


class MessageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        conv = get_object_or_404(Conversation, pk=conversation_id, participants__user=self.request.user)
        return conv.messages.select_related('sender', 'conversation').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        # Mark as opened when fetching messages
        conversation_id = self.kwargs['conversation_id']
        conv = get_object_or_404(Conversation, pk=conversation_id, participants__user=request.user)
        mark_conversation_opened(conv, request.user)
        return super().list(request, *args, **kwargs)


class MessageCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        conversation_id = self.kwargs['conversation_id']
        conv = get_object_or_404(Conversation, pk=conversation_id, participants__user=request.user)
        body = request.data.get('body', '').strip()
        if not body:
            return Response({"detail": "Message body required"}, status=400)
        msg = send_message(conv, request.user, body)
        serializer = self.get_serializer(msg, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
