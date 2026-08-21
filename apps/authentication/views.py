from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.mixins import APIResponseMixin
from core.throttling import OTPThrottle, BurstRateThrottle
from apps.authentication.serializers import(
    EmailVerificationConfirmSerializer,
    GoogleAuthSerializer,
    LogoutSerializer,
)
from apps.authentication.services import generate_and_send_otp, verify_otp
from apps.authentication.utils import verify_google_token
from apps.authentication.models import SocialAccount
from apps.users.models import CustomUser
from apps.users.serializers import UserSerializer

class RequestEmailVerificationView(APIResponseMixin, APIView):
    permission_classes =[IsAuthenticated]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        if request.user.is_email_verified:
            return self.error("Email already verified.", status_code=400)
        generate_and_send_otp(request.user, purpose="email_verification")
        return self.success(message="Verification code sent to your email.")

class ConfirmEmailVerificationView(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ok, error = verify_otp(request.user, serializer.validated_data["code"], purpose="email_verification")
        if not ok:
            return self.error(error, status_code=400)
        request.user.is_email_verified = True
        request.user.save(update_fields=["is_email_verified"])
        return self.success(message="Email verified successfully.")

class GoogleAuthView(APIResponseMixin, APIView):
    permission_classes=[AllowAny]
    throttle_classes=[BurstRateThrottle]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = verify_google_token(serializer.validated_data["id_token"])
        if payload is None:
            return self.error("Invalid Google token.", status_code=401)

        google_uid = payload["sub"]
        email = payload["email"]
        full_name = payload.get("name", email.split("@")[0])

        social_account = SocialAccount.objects.filter(
            provider="google", provider_uid=google_uid
        ).select_related("user").first()

        if social_account:
            user = social_account.user
            created = False
        else: 
            existing_user = CustomUser.objects.filter(email=email).first()
            if existing_user:
                return self.error(
                    "An account with this email already exists."
                    "Log in normally, then link Google from account settings.",
                    status_code=409,
                )
            user = CustomUser.objects.create_user(
                email=email, password=None, full_name=full_name, is_email_verified=True
            )
            user.set_unusable_password()
            user.save(update_fields=["password"])
            SocialAccount.objects.create(user=user, provider="google", provider_uid=google_uid)
            created = True
        refresh = RefreshToken.for_user(user)
        return self.success(
            {
                "user":UserSerializer(user).data,
                "access":str(refresh.access_token),
                "refresh":str(refresh),
            },
            message = "Account created and logged in." if created else "Login successful."
        )
"""
Google ID token
      ↓
Is the token actually valid?
      ↓
Who is this Google user?
      ↓
Have we seen this Google account before?
      ↓
    YES ────────────────→ Log them in
      │
     NO
      ↓
Does our database already have this email?
      ↓
    YES ────────────────→ Don't merge automatically
      │
     NO
      ↓
Create a new CustomUser
      ↓
Create a SocialAccount linking Google → CustomUser
      ↓
Log them in
"""

class LogoutView(APIResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data = request.data)
        serializer.is_valid(raise_exception= True)

        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            return self.error("Invalid or already-expired token.", status_code=400)
        return self.success(message="Logged out successfully.")