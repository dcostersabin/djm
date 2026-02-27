from django.db import models


class TimestampsMixin(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
