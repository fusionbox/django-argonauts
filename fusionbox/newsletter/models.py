from django.db import models

from fusionbox.behaviors import Timestampable

class Submission(Timestampable):
    email = models.EmailField('Email', unique=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Newsletter Submission'
        verbose_name_plural = 'Newsletter Submissions'

    def __unicode__(self):
        return "%s (%s)" % (self.email,
                self.created_at.strftime("%Y-%m-%d %H:%M:%S"))
