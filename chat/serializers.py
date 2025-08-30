# apps/chat/api/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Conversation, Message, ConversationParticipant
from .queries import conversations_with_last_and_unread

class MessageSerializer(serializers.ModelSerializer):
    seen = serializers.SerializerMethodField()
    # sender_photo = serializers.SerializerMethodField()
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'body', 'sender_username', 'created_at', 'seen']

    def get_seen(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        participants = obj.conversation.participants.all()
        other = next((p for p in participants if p.user_id != request.user.id), None)
        return bool(other and other.last_read_at >= obj.created_at)

    def get_sender_photo(self, obj):
        request = self.context.get('request')
        if obj.sender.user_photo:
            return request.build_absolute_uri(obj.sender.user_photo.url)
        return None

# apps/chat/api/serializers.py
from django.contrib.auth import get_user_model
User = get_user_model()

class ConversationListSerializer(serializers.ModelSerializer):
    unread_count = serializers.IntegerField()
    last_message_text = serializers.CharField()
    last_message_at = serializers.DateTimeField()
    last_message_sender_id = serializers.IntegerField()
    my_last_read_at = serializers.DateTimeField()
    other_user_username = serializers.SerializerMethodField()
    other_user_photo = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'last_message_text', 'last_message_at',
            'last_message_sender_id', 'unread_count', 'my_last_read_at',
            'other_user_username', 'other_user_photo'
        ]

    def get_other_user_username(self, obj):
        try:
            user = User.objects.get(id=obj.other_user_id)
            return user.username
        except User.DoesNotExist:
            return None

    def get_other_user_photo(self, obj):
        try:
            user = User.objects.get(id=obj.other_user_id)
            request = self.context.get('request')
            if user.user_photo:
                return request.build_absolute_uri(user.user_photo.url)
        except User.DoesNotExist:
            return None
        return None

