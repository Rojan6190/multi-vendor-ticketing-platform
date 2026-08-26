from rest_framework.test import APITestCase
from rest_framework import status

from apps.users.models import CustomUser
from apps.vendors.models import VendorProfile
from core.constants import UserRole, VendorStatus


class VendorApplicationTests(APITestCase):
    def setUp(self):
        self.organizer = CustomUser.objects.create_user(
            email="organizer@example.com", password="Pass1234", full_name="Org", role=UserRole.ORGANIZER
        )
        self.admin = CustomUser.objects.create_superuser(
            email="admin@example.com", password="Pass1234", full_name="Admin"
        )

    def test_organizer_can_apply(self):
        self.client.force_authenticate(self.organizer)
        response = self.client.post("/api/v1/vendors/apply/", {"business_name": "Test Events Co"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VendorProfile.objects.count(), 1)

    def test_admin_can_approve_vendor(self):
        vendor = VendorProfile.objects.create(user=self.organizer, business_name="Test Events Co")
        self.client.force_authenticate(self.admin)
        response = self.client.post(f"/api/v1/vendors/{vendor.id}/review/", {"action": "approve"})
        vendor.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(vendor.status, VendorStatus.APPROVED)
        self.assertTrue(hasattr(vendor, "commission_rate"))