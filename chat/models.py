# apps/chat/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # denormalization for fast listing
    last_message = models.ForeignKey(
        'Message', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    class Meta:
        db_table = 'chat_conversation'

    def __str__(self):
        return f"Conversation {self.pk}"


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # key to unread + read receipts
    last_read_at = models.DateTimeField(default=timezone.make_aware(timezone.datetime.min))

    class Meta:
        unique_together = [('conversation', 'user')]
        db_table = 'chat_conversation_participant'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['conversation', 'last_read_at']),
        ]

    def __str__(self):
        return f"{self.user_id} in {self.conversation_id}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_message'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['conversation', 'sender', 'created_at']),
        ]

    def __str__(self):
        return f"Msg {self.pk} in {self.conversation_id}"
