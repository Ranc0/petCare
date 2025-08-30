# apps/chat/jwt_middleware.py
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication

class JwtAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner
        self.jwt_auth = JWTAuthentication()

    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", []))
        token = None

        # Authorization: Bearer <token>
        auth_header = headers.get(b'authorization', None)
        if auth_header:
            try:
                prefix, token_bytes = auth_header.split()
                if prefix.lower() == b"bearer":
                    token = token_bytes.decode()
            except Exception:
                token = None

        # Fallback: query string ?token=<...>
        if not token:
            qs = parse_qs(scope.get("query_string", b"").decode())
            token = (qs.get("token") or [None])[0]

        user = AnonymousUser()
        if token:
            try:
                validated = self.jwt_auth.get_validated_token(token)
                user = await self._get_user_async(validated)
            except Exception:
                user = AnonymousUser()

        scope['user'] = user
        return await self.inner(scope, receive, send)

    async def _get_user_async(self, validated_token):
        # JWTAuthentication.get_user is sync; call in thread if using async ORM
        from asgiref.sync import sync_to_async
        return await sync_to_async(self.jwt_auth.get_user)(validated_token)
