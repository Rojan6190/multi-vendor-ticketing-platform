from django.urls import path
from apps.authentication.views import(
    RequestEmailVerificationView,
    ConfirmEmailVerificationView,
    GoogleAuthView,
    LogoutView
)

urlpatterns = [
    path("email/verify/request/", RequestEmailVerificationView.as_view(), name="email-verify-request"),
    path("email/verify/confirm/", ConfirmEmailVerificationView.as_view(), name="email-verify-confirm"),
    path("google/", GoogleAuthView.as_view(), name="google-auth"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
]