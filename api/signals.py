from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Institution, InstitutionMember
from LiveORC.utils import choices

@receiver(post_save, sender=Institution)
def create_team(sender, instance=None, created=False, **kwargs):
    if created:
        InstitutionMember.objects.create(
            institution=instance,
            member=instance.owner,
            role=choices.TeamRole.OWNER
        )