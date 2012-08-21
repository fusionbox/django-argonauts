from django.db import models

from fusionbox import behaviors


class Logged404(behaviors.Timestampable):
    domain = models.CharField(max_length=255, db_index=True)
    referer = models.CharField(max_length=255, db_index=True)
    is_internal = models.BooleanField(blank=True, db_index=True)
    path = models.CharField(max_length=255, db_index=True)

    class Meta:
        ordering = ('-created_at',)
        get_latest_by = 'created_at'
        unique_together = ('domain', 'referer', 'path', 'is_internal')
