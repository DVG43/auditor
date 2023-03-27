from django.contrib import admin

from .models import CategoryForTemplate, Template


@admin.register(CategoryForTemplate)
class TagForTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    fields = ('name', 'slug',)
    list_display_links = ('name',)
    search_fields = ('name',)
    readonly_fields = ('slug',)

@admin.register(Template)
class TagForTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_text', 'created_at', 'last_modified_date',)
    fields = ('name', 'template_text', 'example', 'result', 'is_common', 'owner',)
    list_display_links = ('name',)
    readonly_fields = ('created_at', 'last_modified_date',)
    search_fields = ('name', 'template_text',)
