from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Register your models here.
from core.models.user import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all().order_by('name')])

    get_groups.short_description = "Groups"

    model = User
    list_display = ("email", "username", "get_groups", "is_active", "is_staff")
    list_filter = ("groups__name", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("username", "degree_level", "program", "enrollment_year", "points")}),
        (_("OAuth Info"), {"fields": ("oauth_provider", "oauth_id")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important Dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "is_active", "is_staff", "is_superuser", "groups"),
        }),
        (_("Personal Info"), {"fields": ("degree_level", "program", "enrollment_year", "points")}),
        (_("OAuth Info"), {"fields": ("oauth_provider", "oauth_id")}),
    )

    search_fields = ("email", "username", "oauth_id")
    ordering = ("email",)

    readonly_fields = ("last_login", "created_at", "updated_at")