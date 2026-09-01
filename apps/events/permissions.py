from rest_framework import permissions
from core.constants import VendorStatus

class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Read: anyone. Write: only an APPROVED vendor, and only on their own event.
    Checks VendorProfile.status, not just role — per SRS §3.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not(request.user and request.user.is_authenticated):
            return False
        vendor = getattr(request.user, "vendor_profile", None)
        return bool(vendor and vendor.status == VendorStatus.APPROVED)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.vendor.user_id == request.user.id