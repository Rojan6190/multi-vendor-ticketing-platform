from django.urls import path
from apps.vendors.views import (
    VendorApplicationView, VendorMeView, VendorDocumentUploadView,
    VendorApprovalView, VendorDashboardView,
)

urlpatterns = [
    path("apply/", VendorApplicationView.as_view(), name="vendor-apply"),
    path("me/", VendorMeView.as_view(), name="vendor-me"),
    path("documents/", VendorDocumentUploadView.as_view(), name="vendor-documents"),
    path("dashboard/", VendorDashboardView.as_view(), name="vendor-dashboard"),
    path("<uuid:pk>/review/", VendorApprovalView.as_view(), name="vendor-review"),
]