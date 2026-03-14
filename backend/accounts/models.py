from django.db import models
from django.contrib.auth.models import User
from news.models import Edition


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('reporter', 'Reporter'),
        ('subeditor', 'SubEditor'),
        ('editor', 'Editor'),
        ('paginator', 'Paginator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    edition = models.ForeignKey(
        Edition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    must_change_password = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    if created:

        UserProfile.objects.create(
            user=instance,
            role="reporter"
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):

    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
