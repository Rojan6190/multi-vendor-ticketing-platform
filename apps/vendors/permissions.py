from rest_framework.permissions import BasePermission
from core.constants import VendorStatus

class IsVerifiedVendor(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        vendor = getattr(user, "vendor_profile", None)
        return bool(vendor and vendor.status == VendorStatus.APPROVED)

class IsVendorOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        vendor = obj if hasattr(obj, "status") else getattr(obj, "vendor", None)
        return bool(vendor and vendor.user == request.user)

class IsVendorOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        vendor = obj if hasattr(obj, "status") else getattr(obj, "vendor", None)
        return bool(vendor and vendor.user == request.user)
    