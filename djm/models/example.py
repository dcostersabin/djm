"""Example model – replace or remove and add your own in djm.models."""
from django.db import models
from base.models import UUIDPrimaryKeyMixin


class Example(UUIDPrimaryKeyMixin):
    class Meta(UUIDPrimaryKeyMixin.Meta):
        db_table = "example"

    name = models.CharField(max_length=100)
