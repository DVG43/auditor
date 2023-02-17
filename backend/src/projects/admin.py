from django.contrib import admin
from projects.models import Project
from storyboards.models import Storyboard


class StoryBoardInLine(admin.StackedInline):
    model = Storyboard
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'owner',
                    'created_at', 'last_modified_date']
    list_display_links = ['name']
    list_filter = ['owner']
    readonly_fields = ['owner', 'created_at', 'last_modified_date', 'deleted_id']
    inlines = [StoryBoardInLine]
