"""
Django models for fusionbox.newsletter app

"""
from django.db import models

from fusionbox.behaviors import Timestampable

class Submission(Timestampable):
    """
    :class:`Submission` is the basic model for use with the newsletter app.

    It inherits from :class:`fusionbox.behaviors.Timestampable` and contains 
    an :class:`EmailField` with a unique constraint
    """
    email = models.EmailField('Email', unique=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Newsletter Submission'
        verbose_name_plural = 'Newsletter Submissions'

    def __unicode__(self):
        return "%s (%s)" % (self.email,
                self.created_at.strftime("%Y-%m-%d %H:%M:%S"))
