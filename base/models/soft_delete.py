from django.db import models


class SoftDeleteMixin(models.Model):
    class Meta:
        abstract = True

    deleted = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
    )

    def soft_delete(self):
        raise NotImplementedError
