from django.contrib import admin
from django.conf import settings

from fusionbox.contact.models import Submission, Recipient
from fusionbox.admin import CsvAdmin

class SubmissionAdmin(admin.ModelAdmin, CsvAdmin):
    list_display = ('name', 'email', 'list_comment', 'created_at')
    readonly_fields = ('created_at', 'name', 'email', 'comment')
    class Meta:
        model = Submission

    class Media:
        css = {
                'all': ('contact.css',)
                }

    def list_comment(self, submission):
        return submission.comment[:200]
    list_comment.short_description = 'Comment'

    def has_add_permission(self, *args, **kwargs):
        return False

class RecipientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active')
    fieldsets = (
                (None, {
                    'fields': ('name', 'email', 'is_active'),
                    'description': u'Use this form to add or change a recipient for contact form submissions',
                    }),
            )
    class Meta:
        model = Recipient

admin.site.register(Submission, SubmissionAdmin)

if hasattr(settings, 'CONTACT_FORM_RECIPIENTS'):
    pass
else:
    admin.site.register(Recipient, RecipientAdmin)
