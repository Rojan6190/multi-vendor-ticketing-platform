import secrets

from core.redis_client import get_redis

TICKET_TTL_SECONDS = 30  # only needs to survive the instant between issuing and connecting


def _ticket_key(ticket):
    return f"ws_ticket:{ticket}"


def issue_ws_ticket(user):
    """
    Generates a one-time, short-lived ticket tied to this user, stored in
    Redis. Used INSTEAD of the real JWT in the WebSocket URL, so nothing
    long-lived or reusable ever ends up in a log line or browser history.
    """
    ticket = secrets.token_urlsafe(32)
    get_redis().set(_ticket_key(ticket), str(user.id), ex=TICKET_TTL_SECONDS)
    return ticket


def consume_ws_ticket(ticket):
    """
    Looks up and immediately deletes the ticket (one-time use). Returns
    the user_id it was issued for, or None if it's missing/expired/already used.
    """
    redis_conn = get_redis()
    key = _ticket_key(ticket)
    user_id = redis_conn.get(key)
    if user_id is None:
        return None
    redis_conn.delete(key)  # one-time use - can't be replayed even within the TTL window
    return user_id.decode()