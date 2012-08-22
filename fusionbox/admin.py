import csv

from django.http import HttpResponse
from django.forms.models import fields_for_model
from django.contrib import admin

class CsvAdmin(object):
    """
    Adds an 'export as csv option to a model admin. To determine what fields to
    use, it checks the `csv_fields` property, then the `fields` property, then
    the `fields_for_model`
    """

    csv_fields = None

    actions = ('export_csv',)

    def export_csv(self, request, queryset):
        fields = self.csv_fields or self.fields or fields_for_model(self.model).keys()
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % self.model._meta.db_table
        writer = csv.writer(response)
        writer.writerow(fields)
        for obj in queryset.all():
            writer.writerow([getattr(obj, field) for field in fields])
        return response


class SingletonAdmin(admin.ModelAdmin):
    """
    Admin class for 'singleton' models, that should only have one instance
    across the site, like a single homepage video.

    Allows adding objects only when there are none existing. After that it only
    allows changing. Never allows deletion.
    """

    def has_add_permission(self, request, *args, **kwargs):
        return self.model._default_manager.count() == 0

    def has_delete_permission(self, request, *args, **kwargs):
        return False

    def get_actions(self, request):
        actions = super(SingletonAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
