from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Institute, Member, TeamRole

# if a new institute is made, automatically a new membership is applied
@receiver(post_save, sender=Institute)
def create_member(sender, instance=None, created=False, **kwargs):
    if created:
        Member.objects.create(
            institute=instance,
            user=instance.owner,
            role=TeamRole.OWNER
        )