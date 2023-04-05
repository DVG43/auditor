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


class GoogleSheetCredentialsModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'google_sheet_credentials']
    list_display_links = ['id']
    list_filter = ['user']
    search_fields = ['id', 'user']

    class Meta:
        model = GoogleSheetCredentials


admin.site.register(GoogleSheetIntegration, GoogleSheetIntegrationModelAdmin)
admin.site.register(GoogleSheetCredentials, GoogleSheetCredentialsModelAdmin)
