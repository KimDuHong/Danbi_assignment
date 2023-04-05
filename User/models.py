from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):

    # First_name and Last_name isn't used
    first_name = models.CharField(
        max_length=100,
        editable=False,
    )
    last_name = models.CharField(
        max_length=100,
        editable=False,
    )

    team = models.ForeignKey(
        "Team.Team",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="members",
    )

    def __str__(self) -> str:
        return f"{self.username}"
