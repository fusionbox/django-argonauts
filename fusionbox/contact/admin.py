import csv

from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse

from fusionbox.contact.models import Submission, Recipient

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'list_comment', 'created_at')
    readonly_fields = ('created_at', 'name', 'email', 'comment')
    class Meta:
        model = Submission

    class Media:
        css = {
                'all': ('contact.css',)
                }

    actions = ('export_csv',)

    def list_comment(self, submission):
        return submission.comment[:200]
    list_comment.short_description = 'Comment'

    def has_add_permission(self, *args, **kwargs):
        return False

    csv_fields = ('name', 'email', 'comment', 'created_at',)
    def export_csv(self, request, queryset):
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % self.model._meta.db_table
        writer = csv.writer(response)
        writer.writerow(self.csv_fields)
        for obj in queryset.all():
            writer.writerow([getattr(obj, field) for field in self.csv_fields])
        return response


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
