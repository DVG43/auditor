from django.contrib import admin
from accounts import models
from subscription.models import Subscription


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pkid', 'email', 'first_name', 'last_name', 'phone', 'last_login',
                    'is_active', 'is_staff', 'is_superuser', 'is_verified', 'code', 'document','changed_password_date',)
    fields = ('first_name', 'last_name', 'phone', 'birthday', 'is_active')
    list_display_links = ('email',)
    readonly_fields = ('last_login', 'email', )
    search_fields = ('email', 'first_name', 'last_name',)
    list_filter = (
        ('is_active', admin.BooleanFieldListFilter),
        ('is_staff', admin.BooleanFieldListFilter),
        ('is_superuser', admin.BooleanFieldListFilter),
        ('last_login', admin.DateFieldListFilter),
    )
    inlines = [SubscriptionInline]
