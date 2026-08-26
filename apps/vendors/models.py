from django.db import models
from django.conf import settings

from core.models import BaseModel
from core.constants import VendorStatus, DocumentType, PayoutMethod
from core.validators import validate_file_size, validate_document_file


class VendorProfile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendor_profile")
    business_name = models.CharField(max_length=255)
    business_registration_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=VendorStatus.choices, default=VendorStatus.PENDING)
    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="vendor_reviews",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # payout details — access restricted at the permission/view layer, see below
    payout_method = models.CharField(max_length=20, choices=PayoutMethod.choices, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    mobile_wallet_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.business_name} ({self.status})"

    @property
    def is_approved(self):
        return self.status == VendorStatus.APPROVED


class VerificationDocument(BaseModel):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    file = models.FileField(
        upload_to="organizer_docs/",
        validators=[validate_file_size, validate_document_file],
    )

    def __str__(self):
        return f"{self.vendor.business_name} - {self.document_type}"


class CommissionRate(BaseModel):
    vendor = models.OneToOneField(VendorProfile, on_delete=models.CASCADE, related_name="commission_rate")
    rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)  # platform's cut
    note = models.CharField(max_length=255, blank=True)  # e.g. "negotiated rate, see contract"

    def __str__(self):
        return f"{self.vendor.business_name} - {self.rate_percentage}%"