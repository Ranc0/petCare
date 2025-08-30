# apps/chat/consumers.py
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import Conversation, ConversationParticipant
from .services import send_message, mark_conversation_opened

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4401)
            return

        self.conversation_id = int(self.scope['url_route']['kwargs']['conversation_id'])
        allowed = await self._user_in_conversation(self.user.id, self.conversation_id)
        if not allowed:
            await self.close(code=4403)
            return

        self.group_name = f"conversation_{self.conversation_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get("action")

        if action == "send_message":
            body = (content.get("body") or "").strip()
            if not body:
                return
            msg = await self._send_message(self.user.id, self.conversation_id, body)
            # Broadcast to both participants
            await self.channel_layer.group_send(self.group_name, {
                "type": "chat.message",
                "payload": {
                    "id": msg["id"],
                    "body": msg["body"],
                    "sender_id": msg["sender_id"],
                    "created_at": msg["created_at"],
                    "conversation_id": self.conversation_id,
                    "seen": False,  # receiver hasn't opened yet
                }
            })

        elif action == "open":
            # user opened the chat: reset unread and push read receipt
            now = timezone.now().isoformat()
            await self._mark_opened(self.user.id, self.conversation_id)
            # Notify other participant that their messages up to now are seen
            await self.channel_layer.group_send(self.group_name, {
                "type": "chat.read",
                "payload": {
                    "by_user_id": self.user.id,
                    "last_read_at": now
                }
            })

        elif action == "read":  # optional explicit read
            await self._mark_opened(self.user.id, self.conversation_id)
            await self.channel_layer.group_send(self.group_name, {
                "type": "chat.read",
                "payload": {
                    "by_user_id": self.user.id,
                    "last_read_at": timezone.now().isoformat()
                }
            })

    async def chat_message(self, event):
        await self.send_json(event["payload"])

    async def chat_read(self, event):
        await self.send_json({"type": "read_receipt", **event["payload"]})

    # DB helpers
    @database_sync_to_async
    def _user_in_conversation(self, user_id, conversation_id):
        return ConversationParticipant.objects.filter(
            conversation_id=conversation_id, user_id=user_id
        ).exists()

    @database_sync_to_async
    def _send_message(self, user_id, conversation_id, body):
        conv = Conversation.objects.get(pk=conversation_id)
        # permission guard
        if not ConversationParticipant.objects.filter(conversation=conv, user_id=user_id).exists():
            raise PermissionDenied
        msg = send_message(conv, conv.participants.get(user_id=user_id).user, body)
        return {
            "id": msg.id,
            "body": msg.body,
            "sender_id": msg.sender_id,
            "created_at": msg.created_at.isoformat(),
        }

    @database_sync_to_async
    def _mark_opened(self, user_id, conversation_id):
        conv = Conversation.objects.get(pk=conversation_id)
        user = conv.participants.get(user_id=user_id).user
        mark_conversation_opened(conv, user)
