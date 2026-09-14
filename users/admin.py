from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import RegisterForm, UserChangeForm
from users.models import User


# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """User admin model"""

    model = User
    add_form = RegisterForm
    form = UserChangeForm

    ordering = ("id",)

    list_display = ("id", "username", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "telegram_username")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
