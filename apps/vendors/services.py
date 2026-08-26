from django.utils import timezone
from django.db import transaction

from core.constants import VendorStatus
from apps.vendors.models import VendorProfile, CommissionRate

DEFAULT_COMMISSION_RATE = 10.00

@transaction.atomic
def approve_vendor(vendor: VendorProfile, admin_user, commission_rate=None):
    vendor.status = VendorStatus.APPROVED
    vendor.reviewed_by = admin_user
    vendor.reviewed_at = timezone.now()
    vendor.rejection_reason = ""
    vendor.save(update_fields=["status", "reviewed_by", "rejection_reason"])

    #commission gets set at approval time - this is where "some vendors"
    #negotiate a lower cut" (from the SRS) actually gets applied
    CommissionRate.objects.get_or_create(
        vendor=vendor,
        defaults={"rate_percentage": commission_rate or DEFAULT_COMMISSION_RATE},

    )
    return vendor

def reject_vendor(vendor: VendorProfile, admin_user, reason: str):
    vendor.status = VendorStatus.REJECTED
    vendor.reviewed_by = admin_user
    vendor.reviewed_at = timezone.now()
    vendor.rejection_reason = reason
    vendor.save(update_fields=["status", "reviewed_at", "rejection_reason"])
    return vendor

def get_vendor_dashboard_summary(vendor: VendorProfile):
    # Stub — events/bookings/payments don't exist until Day 6+.
    # Wire in real aggregates once those apps land.
    return {
        "vendor_id": str(vendor.id),
        "status": vendor.status,
        "total_events": 0,
        "total_sales": "0.00",
        "pending_payout": "0.00",
    }
