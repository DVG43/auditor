from django.contrib import admin

from shootingplans.models import Shootingplan


@admin.register(Shootingplan)
class ShootingplanAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'doc_uuid']
    list_display_links = ['name']
    list_filter = ['owner']
