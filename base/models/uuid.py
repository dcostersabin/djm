from uuid6 import uuid6

from django.db import models


class UUIDPrimaryKeyMixin(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(
        primary_key=True,
        default=uuid6,
        editable=False,
        db_index=True,
    )
