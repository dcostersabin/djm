from django.db import models


class SortNumberMixin(models.Model):
    class Meta:
        abstract = True
        ordering = ("order_no",)

    order_no = models.IntegerField(null=False, blank=True, db_index=True)
