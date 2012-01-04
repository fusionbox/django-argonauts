from django.contrib import admin

from newsletter.models import *

class NewsletterAdmin(admin.ModelAdmin):
    readonly_fields = ('email','created_at')

admin.site.register(Submission, NewsletterAdmin)
