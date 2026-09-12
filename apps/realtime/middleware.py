from urllib.parse import parse_qs

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from apps.realtime.services import consume_ws_ticket

@database_sync_to_async
def get_user_from_ticket(ticket):
    from apps.users.models import CustomUser

    user_id = consume_ws_ticket(ticket)
    if user_id is None:
        return AnonymousUser()
    try:
        return CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return AnonymousUser


class WSTicketAuthMiddleware(BaseMiddleware):
    """
    WebSocket handshakes can't carry an Authorization header from the
    browser, and putting the real JWT in the URL risks it ending up in
    access logs / browser history. So instead: the client first calls
    POST /api/v1/realtime/ws-ticket/ (normal JWT-authenticated REST call)
    to get a random, single-use, 30-second ticket, then connects with
    that: ws://.../seats/?ticket=<one-time-ticket>
    """
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        ticket = query_string.get("ticket", [None])[0]
        scope["user"] = await get_user_from_ticket(ticket) if ticket else AnonymousUser()
        return await super().__call__(scope, receive, send)


def WSTicketAuthMiddlewareStack(inner):
    return WSTicketAuthMiddleware(inner)