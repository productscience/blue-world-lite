from django.contrib import admin
from join.admin import BlueWorldModelAdmin
from exports.models import DataExport


class DataExportAdmin(BlueWorldModelAdmin):
    """
    A convenience class, to make the export urls visible in django admin
    """
    def has_add_permission(self, request, obj=None):
        return False

    list_display = ('title', 'export_link',)
    fields = ('title', 'description', 'export_link',)
    readonly_fields = ('title', 'description', 'export_link',)

admin.site.register(DataExport, DataExportAdmin)
