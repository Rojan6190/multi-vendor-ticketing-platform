from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from core.mixins import APIResponseMixin
from core.permissions import IsAdmin
from apps.vendors.models import VendorProfile
from apps.vendors.serializers import (
    VendorApplicationSerializer, VendorProfileSerializer,
    VendorApprovalSerializer, VerificationDocumentSerializer,
)
from apps.vendors.services import approve_vendor, reject_vendor, get_vendor_dashboard_summary


class VendorApplicationView(APIResponseMixin, generics.CreateAPIView):
    """POST /api/v1/vendors/apply/ — organizer applies to become a vendor."""
    serializer_class = VendorApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if hasattr(request.user, "vendor_profile"):
            return self.error("You have already applied as a vendor.", status_code=409)
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        vendor = serializer.save()
        return self.success(VendorProfileSerializer(vendor).data, "Vendor application submitted.", status_code=201)


class VendorMeView(APIResponseMixin, generics.RetrieveAPIView):
    """GET /api/v1/vendors/me/ — vendor checks their own status/profile."""
    serializer_class = VendorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        vendor = getattr(self.request.user, "vendor_profile", None)
        if vendor is None:
            raise ValidationError("You have not applied as a vendor yet.")
        return vendor


class VendorDocumentUploadView(APIResponseMixin, generics.CreateAPIView):
    """POST /api/v1/vendors/documents/ — upload extra KYC docs after applying."""
    serializer_class = VerificationDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        vendor = getattr(request.user, "vendor_profile", None)
        if vendor is None:
            return self.error("Apply as a vendor before uploading documents.", status_code=404)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendor=vendor)
        return self.success(serializer.data, "Document uploaded.", status_code=201)


class VendorApprovalView(APIResponseMixin, APIView):
    """POST /api/v1/vendors/<id>/review/ — admin approves or rejects."""
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            vendor = VendorProfile.objects.get(pk=pk)
        except VendorProfile.DoesNotExist:
            return self.error("Vendor application not found.", status_code=404)

        serializer = VendorApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data["action"]

        if action == "approve":
            vendor = approve_vendor(
                vendor, request.user,
                commission_rate=serializer.validated_data.get("commission_rate"),
            )
            message = "Vendor approved."
        else:
            vendor = reject_vendor(
                vendor, request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
            message = "Vendor rejected."

        return self.success(VendorProfileSerializer(vendor).data, message)


class VendorDashboardView(APIResponseMixin, APIView):
    """GET /api/v1/vendors/dashboard/ — summary stub; real data lands Day 6+."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        vendor = getattr(request.user, "vendor_profile", None)
        if vendor is None or vendor.status != "approved":
            return self.error("Only approved vendors have a dashboard.", status_code=403)
        return self.success(get_vendor_dashboard_summary(vendor))