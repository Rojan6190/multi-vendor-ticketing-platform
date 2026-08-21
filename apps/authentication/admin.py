from django.contrib import admin
from apps.authentication.models import SocialAccount


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "provider_uid", "created_at")
    search_fields = ("user__email", "provider_uid")
    list_filter = ("provider",)