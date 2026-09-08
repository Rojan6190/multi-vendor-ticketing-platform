from rest_framework.test import APITestCase
from rest_framework import status

from apps.users.models import CustomUser
from apps.vendors.models import VendorProfile
from apps.events.models import Category, Venue, Event
from apps.tickets.models import TicketTier
from core.constants import UserRole, VendorStatus, EventStatus


class TicketBookingTests(APITestCase):
    def setUp(self):
        vendor_user = CustomUser.objects.create_user(
            email="vendor@example.com", password="Pass1234", full_name="Vendor", role=UserRole.ORGANIZER
        )
        self.vendor = VendorProfile.objects.create(user=vendor_user, business_name="Biz", status=VendorStatus.APPROVED)
        self.attendee = CustomUser.objects.create_user(email="attendee@example.com", password="Pass1234", full_name="Att")
        category = Category.objects.create(name="Music")
        venue = Venue.objects.create(name="Hall", address="St", city="KTM")
        self.event = Event.objects.create(
            vendor=self.vendor, category=category, venue=venue, title="Concert", description="...",
            status=EventStatus.PUBLISHED, start_datetime="2027-01-01T18:00:00Z", end_datetime="2027-01-01T22:00:00Z",
        )
        self.tier = TicketTier.objects.create(event=self.event, name="General", price=500, total_quantity=2)

    def test_booking_reduces_availability(self):
        self.client.force_authenticate(self.attendee)
        response = self.client.post(f"/api/v1/ticket-tiers/{self.tier.id}/bookings/", {"quantity": 2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.tier.refresh_from_db()
        self.assertEqual(self.tier.sold_quantity, 2)

    def test_overbooking_rejected(self):
        self.client.force_authenticate(self.attendee)
        response = self.client.post(f"/api/v1/ticket-tiers/{self.tier.id}/bookings/", {"quantity": 3})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)