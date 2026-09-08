from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, NotFound

from core.mixins import APIResponseMixin
from apps.events.models import Event
from apps.tickets.models import TicketTier, Booking
from apps.tickets.serializers import TicketTierSerializer, BookingSerializer, BookingCreateSerializer
from apps.tickets.services import create_booking, cancel_booking
from apps.tickets.selectors import get_bookings_for_user

class TicketTierListCreateView(APIResponseMixin, generics.ListCreateAPIView):
    serializer_class = [TicketTierSerializer]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return TicketTier.objects.filter(event__slug = self.kwargs["event_slug"])

    def perform_create(self, serializer):
        try:
            event = Event.objects.get(slug = self.kwargs["event_slug"])
        except Event.DoesNotExist:
            raise NotFound("Event not found.")
        vendor = getattr(self.request.user, "vendor_profile", None)
        if not vendor or event.vendor_id != vendor.id:
            raise PermissionDenied("Only the event's own vendor can add ticket tiers. ")
        serializer.save(event=event)

class TicketTierDetailView(APIResponseMixin, generics.RetrieveUpdateAPIView):
    serializer_class = TicketTierSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return TicketTier.objects.filter(event__slug = self.kwargs["event_slug"])


class BookingListCreateView(APIResponseMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return BookingCreateSerializer if self.request.method == "POST" else BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(ticket_tier_id = self.kwargs["ticket_tier_pk"], user = self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = BookingCreateSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        booking = create_booking(
            user = request.user, 
            ticket_tier_id=self.kwargs["ticket_tier_pk"],
            quantity= serializer.validated_data["quantity"],

        )
        return self.success(BookingSerializer(booking).data, "Booking created.", status_code=201)


class BookingDetailView(APIResponseMixin, generics.RetrieveDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(ticket_tier_id = self.kwargs["ticket_tier_pk"], user = self.request.user)

    def perform_destroy(self, instance):
        cancel_booking(instance)


class MyBookingsView(APIResponseMixin, generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_bookings_for_user(self.request.user)
