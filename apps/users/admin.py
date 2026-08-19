from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import CustomUser, Profile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email","full_name","role","is_active", "is_staff")
    ordering = ("-created_at",)
    search_fields = ("email", "full_name")
    fieldsets = (
        (None, {"fields":("email", "password")}),
        ("Personal info", {"fields":("full_name", "role")}),
        ("Status", {"fields":("is_active", "is_staff", "is_superuser", "is_email_verified")}),
    )
    add_fieldsets = (
        (None, {
            "classes":("wide",),
            "fields":("email", "full_name", "password1", "password2", "role"),

        }),

    )

admin.site.register(Profile)
