from django.contrib import admin

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

    def list_comment(self, submission):
        return submission.comment[:200]

    def has_add_permission(self, *args, **kwargs):
        return False

    list_comment.short_description = 'Comment'

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
admin.site.register(Recipient, RecipientAdmin)
