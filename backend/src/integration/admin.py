from django.contrib import admin

from integration.models.googlesheet import GoogleSheetIntegration, GoogleSheetCredentials
from poll.models.poll import Poll


class GoogleSheetIntegrationModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'is_active',
                    'spreadsheet_url', 'row_count']
    list_display_links = ['id']
    list_filter = ['user']
    search_fields = ['id', 'user']

    class Meta:
        model = GoogleSheetIntegration


class PollModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'owner', 'name', 'image', 'test_mode_global',
        'count_answers', 'last_open']

    class Meta:
        model = Poll


class GoogleSheetCredentialsModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'google_sheet_credetials']
    list_display_links = ['id']
    list_filter = ['user']
    search_fields = ['id', 'user']

    class Meta:
        model = GoogleSheetCredentials


admin.site.register(GoogleSheetIntegration, GoogleSheetIntegrationModelAdmin)
admin.site.register(Poll, PollModelAdmin)
admin.site.register(GoogleSheetCredentials, GoogleSheetCredentialsModelAdmin)
