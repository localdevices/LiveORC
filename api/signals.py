from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Institute, InstituteMember
from LiveORC.utils import choices


@receiver(post_save, sender=Institute)
def create_team(sender, instance=None, created=False, **kwargs):
    if created:
        InstituteMember.objects.create(
            institution=instance,
            member=instance.owner,
            role=choices.TeamRole.OWNER
        )