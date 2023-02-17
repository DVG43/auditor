from django.contrib import admin
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.translation import gettext_lazy as _
from django import forms
import datetime

from subscription.models import (
    Subscription,
    TariffPeriod,
    Tariff,
    TPI,
    Currency,
    PaymentMethod,
    Promocode, BankTransfer, CardPayment,
    School, SertificatePayment, TinkoffResponse
)


class TariffPeriodInLine(admin.TabularInline):
    model = TariffPeriod
    extra = 1
    show_change_link = True


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = [
        'tariff_name', 'tariff_description', 'base_month_price',
        'get_periods'
    ]
    inlines = [TariffPeriodInLine]
    exclude = ['payment_details']
    readonly_fields = ['is_trial']

    @admin.display(description=_('Periods'))
    def get_periods(self, obj):
        if obj.periods.count() == 1:
            return obj.periods.first()
        else:
            return list(obj.periods.all())


class EndDataEditForm(forms.ModelForm):
    end_datetime = forms.SplitDateTimeField(widget=AdminSplitDateTime, label=_('end datetime'))

    class Meta:
        model = Subscription
        fields = ('user', 'tariff', 'recurrent', 'end_datetime', 'end_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['end_datetime'].initial = \
                datetime.datetime.fromtimestamp(kwargs['instance'].end_date)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    form = EndDataEditForm
    list_display = [
        'user', 'end_datetime', 'end_date'
    ]
    search_fields = ['user__email']
    exclude = ['tariffs']
    readonly_fields = ['tariff', 'end_date', 'recurrent']
    list_per_page = 30

    def save_model(self, request, obj, form, change):

        iso_date = form.cleaned_data.get('end_datetime')
        obj.end_date = datetime.datetime.timestamp(iso_date)
        obj.save()

        super(SubscriptionAdmin, self).save_model(request, obj, form, change)


@admin.register(TPI)
class TPIAdmin(admin.ModelAdmin):
    pass


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    exclude = ['payment_details']
    show_change_link = True


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    list_editable = []
    list_display_links = None


class PromocodeInline(admin.TabularInline):
    model = Promocode
    extra = 0


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    inlines = [PromocodeInline]
    pass


@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    list_filter = ['is_student']
    search_fields = ['school']
    readonly_fields = ['total_usage']


@admin.register(SertificatePayment)
class SertificatePaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(BankTransfer)
class BankTransferAdmin(admin.ModelAdmin):
    pass


@admin.register(CardPayment)
class CardPaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(TinkoffResponse)
class TinkoffResponseAdmin(admin.ModelAdmin):
    readonly_fields = [
        'TerminalKey',
        'OrderId',
        'Success',
        'Status',
        'PaymentId',
        'ErrorCode',
        'Amount',
        'CardId',
        'Pan',
        'ExpDate',
        'Token',
        'RebillId'
    ]
