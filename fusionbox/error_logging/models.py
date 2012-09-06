import hashlib

from django.db import models

from fusionbox import behaviors


def hash_args(*args):
    hasher = hashlib.md5()
    for arg in args:
        hasher.update(str(arg))
    return hasher.hexdigest()


class Logged404(behaviors.Timestampable):
    hash = models.CharField(max_length=255, db_index=True)
    domain = models.CharField(max_length=255, db_index=True)
    referer = models.CharField(max_length=255, db_index=True)
    is_internal = models.BooleanField(blank=True, db_index=True)
    path = models.CharField(max_length=255, db_index=True)

    class Meta:
        ordering = ('-created_at',)
        get_latest_by = 'created_at'

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.hash = hash_args(self.domain, self.referer, self.is_internal, self.path)
        super(Logged404, self).save(*args, **kwargs)
