from django.contrib import admin
from contacts.models import Contact, Position, Department


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'position', 'department', 'owner']
    list_display_links = ['name']
    list_filter = ['owner']
    readonly_fields = ['owner']
    fields = ['name', 'phone', 'email', 'position', 'department']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner']
    list_display_links = ['name']
    list_filter = ['owner']
    readonly_fields = ['owner']
    fields = ['name', 'tag_color']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner']
    list_display_links = ['name']
    list_filter = ['owner']
    readonly_fields = ['owner']
    fields = ['name', 'tag_color']
