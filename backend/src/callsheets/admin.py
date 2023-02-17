from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from callsheets.models import Callsheet, CallsheetLogo, LocationMap, Location


class LocationMapInline(NestedStackedInline):
    model = LocationMap
    extra = 0
    list_display = ['id', 'file', 'host_location', 'owner']
    list_display_links = ['id']
    list_filter = ['host_location', 'owner']
    fields = ['file', 'host_location', 'owner']
    fk_name = 'host_location'


class LocationInline(NestedStackedInline):
    model = Location
    extra = 0
    inlines = [LocationMapInline]
    list_display = ['id', 'address', 'host_callsheet', 'owner']
    list_display_links = ['id']
    list_filter = ['host_callsheet']
    fields = [
        'owner',
        'host_callsheet',
        'address',
        'check_in', 'check_out', 'start_motor', 'stop_motor', 'shift_type'
    ]
    fk_name = 'host_callsheet'


class CallsheetLogoInline(NestedStackedInline):
    model = CallsheetLogo
    extra = 0
    fields = ['file', 'owner']
    fk_name = 'host_callsheet'


class CallsheetAdmin(NestedModelAdmin):
    model = Callsheet
    list_display = ['id', 'name', 'date', 'get_userfields', 'owner', 'doc_uuid']
    list_display_links = ['name']
    list_filter = ['owner']
    inlines = [CallsheetLogoInline, LocationInline]
    readonly_fields = [
        'owner', 'last_modified_user',
        'last_modified_date', 'deleted_since',
        'deleted_id', 'host_project'
    ]
    fields = [
        'owner',
        'host_project',
        'date',
        'name',
        'film_day', 'start_time', 'end_time',
        'lunch_type', 'lunch_time', 'shift_type', 'contact',
        'sunrise', 'sunset', 'weather',
        'last_modified_user',
        'last_modified_date', 'deleted_since',
        'temp', 'max_temp', 'min_temp', 'city',
        'lat', 'lng',
        'delete_id', 'doc_uuid',
    ]

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)

    def get_userfields(self, obj):
        return [uf.cell_content for uf in obj.userfields.all()]


admin.site.register(Callsheet, CallsheetAdmin)
