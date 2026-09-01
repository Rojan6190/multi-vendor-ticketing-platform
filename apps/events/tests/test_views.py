from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status

from apps.users.models import CustomUser
from apps.vendors.models import VendorProfile
from apps.events.models import Category, Venue, Event
from core.constants import UserRole, VendorStatus, EventStatus


class EventTestBase(APITestCase):
    def setUp(self):
        cache.clear()  # versioned cache lives outside the test DB - must clear manually

        self.category = Category.objects.create(name="Music")
        self.venue = Venue.objects.create(name="Hall A", address="123 St", city="Kathmandu")

        self.pending_organizer = CustomUser.objects.create_user(
            email="pending@example.com", password="Pass1234", full_name="Pending Org",
            role=UserRole.ORGANIZER,
        )
        VendorProfile.objects.create(
            user=self.pending_organizer, business_name="Pending Biz", status=VendorStatus.PENDING
        )

        self.approved_organizer = CustomUser.objects.create_user(
            email="approved@example.com", password="Pass1234", full_name="Approved Org",
            role=UserRole.ORGANIZER,
        )
        self.approved_vendor = VendorProfile.objects.create(
            user=self.approved_organizer, business_name="Approved Biz", status=VendorStatus.APPROVED
        )

        self.other_approved_organizer = CustomUser.objects.create_user(
            email="other@example.com", password="Pass1234", full_name="Other Org",
            role=UserRole.ORGANIZER,
        )
        self.other_vendor = VendorProfile.objects.create(
            user=self.other_approved_organizer, business_name="Other Biz", status=VendorStatus.APPROVED
        )

        self.event_payload = {
            "title": "Live Concert",
            "description": "A great night of music.",
            "category_id": str(self.category.id),
            "venue_id": str(self.venue.id),
            "start_datetime": "2027-01-01T18:00:00Z",
            "end_datetime": "2027-01-01T22:00:00Z",
        }


class EventListTests(EventTestBase):
    def test_list_events_public(self):
        response = self.client.get("/api/v1/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")

    def test_draft_event_hidden_from_public(self):
        Event.objects.create(
            vendor=self.approved_vendor, category=self.category, venue=self.venue,
            title="Secret Draft", description="...",
            start_datetime="2027-01-01T18:00:00Z", end_datetime="2027-01-01T22:00:00Z",
            status=EventStatus.DRAFT,
        )
        response = self.client.get("/api/v1/events/")
        titles = [e["title"] for e in response.data["data"]["results"]] if "results" in response.data.get("data", {}) else []
        self.assertNotIn("Secret Draft", titles)


class EventPermissionTests(EventTestBase):
    def test_pending_vendor_cannot_create_event(self):
        self.client.force_authenticate(self.pending_organizer)
        response = self.client.post("/api/v1/events/", self.event_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approved_vendor_can_create_event(self):
        self.client.force_authenticate(self.approved_organizer)
        response = self.client.post("/api/v1/events/", self.event_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().vendor, self.approved_vendor)

    def test_vendor_cannot_edit_others_event(self):
        event = Event.objects.create(
            vendor=self.approved_vendor, category=self.category, venue=self.venue,
            title="Owned by approved_vendor", description="...",
            start_datetime="2027-01-01T18:00:00Z", end_datetime="2027-01-01T22:00:00Z",
            status=EventStatus.PUBLISHED,
        )
        self.client.force_authenticate(self.other_approved_organizer)
        response = self.client.patch(f"/api/v1/events/{event.slug}/", {"title": "Hijacked"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_create_event(self):
        response = self.client.post("/api/v1/events/", self.event_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)