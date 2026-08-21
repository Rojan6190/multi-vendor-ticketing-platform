from django.db import models
from core.models import BaseModel

class SocialAccount(BaseModel):
    """
    Links a CustomUser to a third-party identity provider.
    Keyed on provider_uid (Google's `sub` claim) — NOT email — because
    email can change or be reused, but `sub` is permanent and unique per
    Google account. This is what stops us from silently merging accounts
    just because two emails happen to match.
    """
    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="social_accounts"
    )
    provider = models.CharField(max_length=20)  # "google", later "apple" etc
    provider_uid = models.CharField(max_length=255)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("provider", "provider_uid")

    def __str__(self):
        return f"{self.provider}:{self.provider_uid} -> {self.user.email}"