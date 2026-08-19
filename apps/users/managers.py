from django.contrib.auth.base_user import BaseUserManager

from core.managers import BaseQuerySet
from core.constants import UserRole

class CustomUserManager(BaseUserManager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db).alive()

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_email_verified", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class AllUsersManager(BaseUserManager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)         #no .alive() filter-> both active and deleted users show up