from urllib.parse import parse_qs

class JwtAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # ✅ Safe imports after Django setup
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from asgiref.sync import sync_to_async

        jwt_auth = JWTAuthentication()

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
                validated = jwt_auth.get_validated_token(token)
                user = await sync_to_async(jwt_auth.get_user)(validated)
            except Exception:
                user = AnonymousUser()

        scope['user'] = user
        return await self.inner(scope, receive, send)
