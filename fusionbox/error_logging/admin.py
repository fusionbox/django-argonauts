from django.contrib import admin

from fusionbox.error_logging.models import Logged404
from fusionbox.admin import CsvAdmin


class Logged404Admin(admin.ModelAdmin, CsvAdmin):
    date_hierarchy = 'created_at'
    list_display = ('domain', 'referer', 'is_internal', 'path', 'created_at')
    list_filter = ('domain', 'is_internal')
    search_fields = ('domain', 'referer', 'path')
    readonly_fields = ('domain', 'referer', 'is_internal', 'path', 'created_at')
    actions_on_top = True
    save_on_top = True

    def has_add_permission(self, request):
        return False

admin.site.register(Logged404, Logged404Admin)
