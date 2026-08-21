from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

from core.utils import generate_otp

OTP_TTL_SECONDS = 300   # 5mins

def _cache_keys(user_id, purpose):
    return f"otp:{purpose}:{user_id}"

def generate_and_send_otp(user, purpose="email_verification"):
    code = generate_otp()
    cache.set(_cache_keys(user.id, purpose), code, timeout=OTP_TTL_SECONDS)

    send_mail(
        subject="Your verification code",
        message=f"Your OTP is {code}. It expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

def verify_otp(user, code, purpose="email_verification"):
    key = _cache_keys(user.id, purpose)
    cached_code = cache.get(key)

    if cached_code is None:
        return False, "OTP expired or not found."
    if cached_code != code:
        return False, "Invalid OTP."

    cache.delete(key)   #one-time use
    return True, None