from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, reverse
from django.utils.translation import gettext_lazy
from django.views.generic.edit import CreateView
from .models import User
from .admin import FirstUserCreationForm, FirstUserAdmin


class FirstUserCreateView(CreateView):
    model = User
    template_name = 'users/first_user.html'
    form_class = FirstUserCreationForm
    extra_context = {
        "site_header": gettext_lazy("LiveOpenRiverCam"),
        "site_title": gettext_lazy("LiveOpenRiverCam"),
        "index_title": gettext_lazy("Admin dashboard")
    }

    def get(self, request, *args, **kwargs):
        if User.objects.filter(is_superuser=True).count() != 0:
            return redirect(reverse('admin:index'))
        return super().get(request, *args, **kwargs)

    # def render(self, data):
    #     return super().render(data)

    def post(self, request, *args, **kwargs):
        user_form = FirstUserCreationForm(request.POST)
        if user_form.is_valid():
            admin_user = user_form.save(commit=False)
            admin_user.is_superuser = admin_user.is_staff = True
            admin_user.password = make_password(user_form.cleaned_data["password2"])
            admin_user.save()
            login(request, admin_user, "django.contrib.auth.backends.ModelBackend")
            return redirect(reverse('admin:index'))
        else:
            keys = list(user_form.errors.keys())
            messages.error(request, f"{user_form.errors[keys[0]][0]}")
            return redirect('/')

