from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

from django.utils.translation import gettext_lazy
from users.models import (
    Institute,
    InstituteMember,
    User,
    Group
)

from .user import UserAdmin

# initiate orc admin site with specific titles and logos

# admin.site.site_title = gettext_lazy("LiveOpenRiverCam")
# admin.site.site_header = gettext_lazy("LiveOpenRiverCam")
# admin.site.index_title = gettext_lazy("Admin dashboard")


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Institute)
admin.site.register(InstituteMember)

# we are not using groups, hence remove (we will have institutes)
# TODO: move user/institute to a separate app called Users and Institutes

