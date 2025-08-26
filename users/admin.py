from django.contrib import admin
from .models import User
from django.utils.html import format_html
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# ======================
# USER ADMIN
# ======================
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser",
        "date_joined"
    )
    list_filter = (
        "is_active", "is_staff", "is_superuser",
        "is_deleted"
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "created", "modified", "id")