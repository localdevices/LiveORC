from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# from ..models import User
from ..models.user import User
#

# User = get_user_model()
USERNAME_FIELD = User.USERNAME_FIELD

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("name", "email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("name", "email",)

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
EDIT_FIELDS = REQUIRED_FIELDS + EDITABLE_FIELDS + ("groups", "user_permissions", "institute")
#
#
class UserAdmin(DjangoUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

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
            {"fields": EDIT_FIELDS + ("password",)},
        ),
        # ("Password", {"fields": ("password",)}),
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