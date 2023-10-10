from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
# from ..models.user import User


User = get_user_model()
USERNAME_FIELD = User.USERNAME_FIELD
REQUIRED_FIELDS = (USERNAME_FIELD,) + tuple(User.REQUIRED_FIELDS)
EDITABLE_FIELDS = (
    "name",
    "is_staff",
    "active",
    "is_superuser",
)
ADD_FIELDS = (
    REQUIRED_FIELDS
    + EDITABLE_FIELDS
    + (
        "password1",
        "password2",
    )
)
EDIT_FIELDS = REQUIRED_FIELDS + EDITABLE_FIELDS


class UserAdmin(DjangoUserAdmin):
    list_display = (
        "name",
        "email",
        "is_active",
        "is_staff",
        "created",
    )
    fieldsets = (
        (
            None,
            {"fields": EDIT_FIELDS},
        ),
        ("Password", {"fields": ("password",)}),
    )
    add_fieldsets = (
        (
            None,
            {"fields": ADD_FIELDS},
        ),
    )
    readonly_fields = (
        "last_login",
        "created"
    )
    search_fields = (USERNAME_FIELD,)
    ordering = (USERNAME_FIELD,)
    list_filter = ("active", "is_staff")