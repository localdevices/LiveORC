from django.core.management.base import BaseCommand, CommandError
from users.models import Group
# from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import logging

READ_PERMISSIONS = ['view', ]  # For now only view permission by default for all, others include add, delete, change
WRITE_PERMISSIONS = ['view', 'add', 'change', 'delete']

# Add your groups here, app and model code
MODELS = [
    ('api', 'video'),
    ('api', 'site'),
    ('api', 'timeseries'),
    ('api', 'cameraconfig'),
    ('api', 'profile'),
    ('api', 'server'),
    ('api', 'task'),
    ('api', 'recipe'),
]

def add_group_permissions(group_names, model_natural_keys, permissions):
    """
    Add permissions to the provided groups for the listed models.
    Error raised if permission or `ContentType` can't be found.

    :param group_names: iterable of group names
    :param model_natural_keys: iterable of 2-tuples containing natural keys for ContentType
    :param permissions: iterable of str (permission names i.e. add, view)
    """
    # first delete any existing groups
    for group_name in group_names:
        print(f"Creating group {group_name}")
        group, created = Group.objects.update_or_create(name=group_name)

        for model_natural_key in model_natural_keys:
            perm_to_add = []
            for permission in permissions:
                # using the 2nd element of `model_natural_key` which is the
                #  model name to derive the permission `codename`
                permission_codename = f"{permission}_{model_natural_key[1]}"
                try:
                    perm_to_add.append(
                        Permission.objects.get_by_natural_key(
                            permission_codename, *model_natural_key
                        )
                    )
                except Permission.DoesNotExist:
                    # trying to add a permission that doesn't exist; log and continue
                    logging.error(
                        f"permissions.add_group_permissions Permission not found with name {permission_codename!r}."
                    )
                    raise
                except ContentType.DoesNotExist:
                    # trying to add a permission that doesn't exist; log and continue
                    logging.error(
                        "permissions.add_group_permissions ContentType not found with "
                        f"natural name {model_natural_key!r}."
                    )
                    raise

            group.permissions.add(*perm_to_add)
    return

API_READ_GROUP = 'viewers'
API_WRITE_GROUP = 'editors'
READ_GROUPS = [API_READ_GROUP, ]
WRITE_GROUPS = [API_WRITE_GROUP, ]  # Can be used in same way as read users below


class Command(BaseCommand):
    help = "Make a 'viewers' and 'editors' group for administrator convenience"
    # import pdb;pdb.set_trace()
    def handle(self, *args, **options):
        add_group_permissions(READ_GROUPS, MODELS, READ_PERMISSIONS)
        add_group_permissions(WRITE_GROUPS, MODELS, WRITE_PERMISSIONS)
        return




# Setting up the group permissions i.e. read for a group of models
