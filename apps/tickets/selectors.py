from apps.tickets.models import TicketTier, Booking

def get_bookings_for_user(user):
    return Booking.objects.filter(user=user).select_related(
        "ticket_tier", "ticket_tier__event", "ticket_tier__event__vendor"
    )