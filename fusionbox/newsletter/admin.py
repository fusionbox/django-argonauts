from django.contrib import admin

from newsletter.models import *

class NewsletterAdmin(admin.ModelAdmin):
    readonly = ('email','created_at')

admin.site.register(Entry, BlogAdmin)
