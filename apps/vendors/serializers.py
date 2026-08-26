from rest_framework import serializers
from apps.vendors.models import VendorProfile, VerificationDocument, CommissionRate


class VerificationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationDocument
        fields = ["id", "document_type", "file", "created_at"]
        read_only_fields = ["id", "created_at"]


class VendorApplicationSerializer(serializers.ModelSerializer):
    documents = VerificationDocumentSerializer(many=True, required=False)

    class Meta:
        model = VendorProfile
        fields = [
            "id", "business_name", "business_registration_number",
            "payout_method", "bank_name", "bank_account_number",
            "mobile_wallet_number", "status", "documents", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def create(self, validated_data):
        documents_data = validated_data.pop("documents", [])
        user = self.context["request"].user
        vendor = VendorProfile.objects.create(user=user, **validated_data)
        for doc in documents_data:
            VerificationDocument.objects.create(vendor=vendor, **doc)
        return vendor


#splited VendorProfileSerializer into a base version and an "admin-safe" version
class VendorProfileSerializer(serializers.ModelSerializer):
    """Full serializer — only ever used for the vendor viewing their OWN profile."""
    documents = VerificationDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = VendorProfile
        fields = [
            "id", "business_name", "business_registration_number", "status",
            "rejection_reason", "payout_method", "bank_name",
            "bank_account_number", "mobile_wallet_number", "documents", "created_at",
        ]
        read_only_fields = fields


class VendorProfilePublicSerializer(serializers.ModelSerializer):
    """
    Safe for admin list/detail views, dashboards, or anywhere that isn't
    strictly the vendor's own /me/ endpoint. Payout details are deliberately
    excluded — SRS Section 12: bank/wallet info is sensitive, access must
    be restricted and logged, not just returned to anyone with admin role.
    """
    class Meta:
        model = VendorProfile
        fields = ["id", "business_name", "status", "created_at"]
        read_only_fields = fields


class VendorApprovalSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])
    reason = serializers.CharField(required=False, allow_blank=True)
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)


class CommissionRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionRate
        fields = ["id", "vendor", "rate_percentage", "note", "created_at"]
        read_only_fields = ["id", "created_at"]