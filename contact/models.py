from django.db import models

from fusionbox.behaviors import Timestampable

class Submission(Timestampable):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=320)
    comment = models.TextField(blank = True)

    class Meta:
        ordering = ('-created_at',)

class Recipient(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=320)
    is_active = models.BooleanField(help_text = u"Only recipients with this field checked will receive contact form submissions")

    class Meta:
        ordering = ('name', 'email')
