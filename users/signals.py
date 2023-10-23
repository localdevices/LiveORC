from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Institute, Member
from LiveORC.utils import choices


@receiver(post_save, sender=Institute)
def create_team(sender, instance=None, created=False, **kwargs):
    if created:
        Member.objects.create(
            institute=instance,
            user=instance.owner,
            role=choices.TeamRole.OWNER
        )