from django.db import transaction
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from core.exceptions import ValidationException, ConflictException
from core.constants import BookingStatus
from core.redis_client import get_redis
from apps.tickets.models import TicketTier, Booking, SeatLock

LOCK_TTL_SECONDS = 120  # checkout hold window


def _lock_key(ticket_tier_id):
    return f"seatlock:{ticket_tier_id}"


def _broadcast(event_slug, payload):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return  # no channel layer configured (e.g. some test runs) — skip quietly
    async_to_sync(channel_layer.group_send)(
        f"event_{event_slug}_seats",
        {"type": "seat_update", "payload": payload},
    )


def get_locked_quantity(ticket_tier_id):
    """Redis is the source of truth for 'how many seats are on hold right now'."""
    raw = get_redis().get(_lock_key(ticket_tier_id))
    return int(raw) if raw else 0


@transaction.atomic
def lock_seats(user, ticket_tier_id, quantity):
    """
    Called when checkout STARTS (before payment). Holds `quantity` seats
    for LOCK_TTL_SECONDS. Redis INCR+EXPIRE is the real enforcement; the
    SeatLock row is just an audit trail an admin could inspect.
    """
    tier = TicketTier.objects.select_related("event").get(pk=ticket_tier_id)
    redis_conn = get_redis()
    key = _lock_key(ticket_tier_id)

    already_locked = get_locked_quantity(ticket_tier_id)
    if tier.available_quantity - already_locked < quantity:
        raise ConflictException("Not enough seats available to lock.")

    pipe = redis_conn.pipeline()
    pipe.incrby(key, quantity)
    pipe.expire(key, LOCK_TTL_SECONDS)  # refreshes TTL on every new lock too — good enough for now
    pipe.execute()

    lock = SeatLock.objects.create(
        ticket_tier=tier, user=user, quantity=quantity,
        expires_at=timezone.now() + timezone.timedelta(seconds=LOCK_TTL_SECONDS),
    )

    _broadcast(tier.event.slug, {
        "type": "seat_locked",
        "ticket_tier_id": str(tier.id),
        "locked_quantity": quantity,
        "available_quantity": tier.available_quantity - get_locked_quantity(tier.id),
    })
    return lock


def release_seat_lock(lock: SeatLock):
    """Call on checkout abandon/payment failure — frees the Redis hold immediately."""
    redis_conn = get_redis()
    redis_conn.decrby(_lock_key(lock.ticket_tier_id), lock.quantity)

    tier = lock.ticket_tier
    _broadcast(tier.event.slug, {
        "type": "seat_released",
        "ticket_tier_id": str(tier.id),
        "released_quantity": lock.quantity,
        "available_quantity": tier.available_quantity - get_locked_quantity(tier.id),
    })
    lock.delete(hard=True)


@transaction.atomic
def create_booking(user, ticket_tier_id, quantity):
    tier = TicketTier.objects.select_for_update().get(pk=ticket_tier_id)

    if tier.sales_end and tier.sales_end < timezone.now():
        raise ValidationException("Ticket sales have closed for this tier.")
    if tier.available_quantity < quantity:
        raise ConflictException(f"Only {tier.available_quantity} tickets left.")

    tier.sold_quantity += quantity
    tier.save(update_fields=["sold_quantity"])

    booking = Booking.objects.create(
        user=user, ticket_tier=tier, quantity=quantity,
        unit_price=tier.price, total_amount=tier.price * quantity,
        status=BookingStatus.PENDING,
    )

    _broadcast(tier.event.slug, {
        "type": "seat_sold",
        "ticket_tier_id": str(tier.id),
        "sold_quantity": quantity,
        "available_quantity": tier.available_quantity,
    })
    return booking


@transaction.atomic
def cancel_booking(booking):
    if booking.status in (BookingStatus.CANCELLED, BookingStatus.EXPIRED):
        return booking

    tier = TicketTier.objects.select_for_update().get(pk=booking.ticket_tier_id)
    tier.sold_quantity = max(0, tier.sold_quantity - booking.quantity)
    tier.save(update_fields=["sold_quantity"])

    booking.status = BookingStatus.CANCELLED
    booking.save(update_fields=["status"])

    _broadcast(tier.event.slug, {
        "type": "seat_released",
        "ticket_tier_id": str(tier.id),
        "released_quantity": booking.quantity,
        "available_quantity": tier.available_quantity,
    })
    return booking

# TODO (Day 10): a Celery Beat task should sweep expired SeatLock rows whose
# Redis key has already lapsed, so the audit table doesn't grow stale rows.