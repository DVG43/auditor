from django.contrib import admin
from django.contrib.admin import display

from common.models import UserColumn, UserCell, UserChoice, StandardIcon


class ChoiceInline(admin.StackedInline):
    model = UserChoice
    extra = 1


@admin.register(UserColumn)
class UserColumnAdmin(admin.ModelAdmin):
    list_display = ['id', 'column_name', 'column_type', 'get_cells',
                    'get_choices',
                    'owner']
    list_display_links = ['column_name']
    list_filter = ['owner']
    readonly_fields = ['column_type', 'owner']
    inlines = []

    @display(description='In usercells')
    def get_cells(self, obj):
        ret = [cell.id for cell in obj.cells.all()]
        return ret

    def get_inlines(self, request, obj):
        if obj.column_type == 'select':
            return [ChoiceInline]
        return []

    @display(description='Choices')
    def get_choices(self, obj):
        choices = obj.choices.all()
        ret = [f'{choice.id}: {choice.choice}' for choice in choices]
        return ret


@admin.register(UserCell)
class UserCellAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'host_usercolumn_id',
        'get_column_name',
        'get_column_type',
        'cell_content',
        'owner'
    ]
    list_filter = ['owner']
    readonly_fields = ['host_usercolumn', 'owner']

    @display(description='Name')
    def get_column_name(self, obj):
        return obj.usercolumn.column_name

    @display(description='Type')
    def get_column_type(self, obj):
        return obj.host_usercolumn.column_type

@admin.register(StandardIcon)
class StandardIconAdmin(admin.ModelAdmin):
    """A class for working with the StandardIcon model in the admin panel."""
    list_display = ('id', 'is_active', )
    list_filter = ('is_active',)
    fields = ('icon_image', 'is_active',)
