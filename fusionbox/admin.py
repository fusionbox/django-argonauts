import csv
from django.http import HttpResponse
from django.forms.models import fields_for_model

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
