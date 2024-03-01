from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from ..models.user import User
from django.contrib.auth.admin import UserAdmin


class FirstUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            'name',
            'email',
            'password1',
            'password2'
            # "is_staff",
            # "is_superuser",
        ]

class FirstUserAdmin(UserAdmin):
    model = User
    add_form = FirstUserCreationForm
    # form = CustomUserChangeForm
    list_display = (
        "name",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "created",
    )

