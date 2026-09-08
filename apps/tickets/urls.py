from django.urls import path
from apps.tickets.views import (
    TicketTierListCreateView, TicketTierDetailView,
    BookingListCreateView, BookingDetailView, MyBookingsView,
)

urlpatterns = [
    path("my-bookings/", MyBookingsView.as_view(), name="my-bookings"),
    path("events/<slug:event_slug>/ticket-tiers/", TicketTierListCreateView.as_view(), name="tier-list"),
    path("events/<slug:event_slug>/ticket-tiers/<uuid:pk>/", TicketTierDetailView.as_view(), name="tier-detail"),
    path("ticket-tiers/<uuid:ticket_tier_pk>/bookings/", BookingListCreateView.as_view(), name="booking-list"),
    path("ticket-tiers/<uuid:ticket_tier_pk>/bookings/<uuid:pk>/", BookingDetailView.as_view(), name="booking-detail"),
]