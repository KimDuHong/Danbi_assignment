from django.db import models

# Create your models here.
class CommonModel(models.Model):

    """common def"""

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    modified_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True
