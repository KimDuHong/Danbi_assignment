from django.db import models

# Create your models here.
class Team(models.Model):
    class TeamChoices(models.TextChoices):
        단비 = "단비"
        다래 = "다래"
        블라블라 = "블라블라"
        철로 = "철로"
        땅이 = "땅이"
        해테 = "해태"
        수피 = "수피"

    name = models.CharField(
        max_length=10,
        choices=TeamChoices.choices,
        unique=True,
    )

    def __str__(self) -> str:
        return self.name
