from django.contrib import admin

from storyboards.models import Storyboard, Frame, Shot


class ShotInLine(admin.TabularInline):
    model = Shot
    extra = 1
    fields = ['file', 'owner', 'host_frame']
    readonly_fields = ['host_frame']
    show_change_link = True


@admin.register(Frame)
class SbdFrameAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'host_storyboard', 'owner']
    inlines = [ShotInLine]
    fields = ['owner', 'name', 'host_storyboard']
    readonly_fields = ['owner', 'host_storyboard']
    list_filter = ['owner']


class SbdFrameInLine(admin.TabularInline):
    model = Frame
    extra = 1
    fields = ['name']
    show_change_link = True


@admin.register(Storyboard)
class StoryboardAdmin(admin.ModelAdmin):
    inlines = [SbdFrameInLine]
    list_display = ['id', 'name', 'owner', 'doc_uuid']
    list_display_links = ['name']
    list_filter = ['owner']
