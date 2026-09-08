from django.db import transaction
from django.utils import timezone

from core.exceptions import ValidationException, ConflictException
from core.constants import BookingStatus
from apps.tickets.models import TicketTier, Booking


@transaction.atomic
def create_booking(user, ticket_tier_id, quantity):
    # select_for_update locks this row until commit — two concurrent
    # requests can't both read "3 left" and both succeed in booking 3.
    tier = TicketTier.objects.select_for_update().get(pk=ticket_tier_id)

    if tier.sales_end and tier.sales_end < timezone.now():
        raise ValidationException("Ticket sales have closed for this tier.")
    if tier.available_quantity < quantity:
        raise ConflictException(f"Only {tier.available_quantity} tickets left.")

    tier.sold_quantity += quantity
    tier.save(update_fields=["sold_quantity"])

    return Booking.objects.create(   #it is essentially a shortcut for booking = Booking(.......)-> booking.save()
        user=user,
        ticket_tier=tier,
        quantity=quantity,
        unit_price=tier.price,
        total_amount=tier.price * quantity,
        status=BookingStatus.PENDING,   # flips to CONFIRMED once payment succeeds — Day 9
    )


@transaction.atomic
def cancel_booking(booking):
    if booking.status in (BookingStatus.CANCELLED, BookingStatus.EXPIRED):
        return booking

    tier = TicketTier.objects.select_for_update().get(pk=booking.ticket_tier_id)
    tier.sold_quantity = max(0, tier.sold_quantity - booking.quantity)
    tier.save(update_fields=["sold_quantity"])

    booking.status = BookingStatus.CANCELLED
    booking.save(update_fields=["status"])
    return booking


"""
Before cancellation:

total = 100
sold = 50
available = 50

Booking quantity = 3

After cancellation:

total = 100
sold = 47
available = 53
"""