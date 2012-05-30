from django.contrib import admin

from .models import Submission


class NewsletterAdmin(admin.ModelAdmin):
    readonly_fields = ('email', 'created_at')

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(Submission, NewsletterAdmin)
