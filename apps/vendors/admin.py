# admin.py
from django.contrib import admin
from apps.vendors.models import VendorProfile, VerificationDocument, CommissionRate

class VerificationDocumentInline(admin.TabularInline):
    model = VerificationDocument
    extra = 0

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("business_name", "user__email")
    inlines = [VerificationDocumentInline]

@admin.register(CommissionRate)
class CommissionRateAdmin(admin.ModelAdmin):
    list_display = ("vendor", "rate_percentage")