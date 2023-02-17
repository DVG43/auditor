import calendar
import uuid
from datetime import datetime as dt
import time

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, gettext, ugettext
from django_celery_beat.models import PeriodicTask, CrontabSchedule


class TPI(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='tpids',
        verbose_name=_('User')
    )
    number = models.IntegerField(_('Tax payer id'))
    title = models.CharField(_('Tax payer title'), max_length=255)

    class Meta:
        verbose_name = _('Tax payer id')
        verbose_name_plural = _('Tax payer ids')


class PaymentDetails(models.Model):
    only = models.IntegerField(default=1)

    # currencies
    # methods
    # tariffs

    class Meta:
        verbose_name = _('Payment details')
        verbose_name_plural = _('Payment details')


class Currency(models.Model):
    CURRENCIES = (
        ('RUB', _('Russian rouble')),
    )
    payment_details = models.ForeignKey(
        PaymentDetails,
        on_delete=models.CASCADE,
        related_name='currencies'
    )
    currency = models.CharField(
        _('Currency'), max_length=5, choices=CURRENCIES, default=CURRENCIES[0])
    currency_icon = models.CharField(_('Currency icon'), max_length=2, default='₽')

    def __str__(self):
        return f'{self.currency} ({self.currency_icon})'

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')


class PaymentMethod(models.Model):
    PAYMENT_METHODS = (
        ('card', _('Credit/debit card')),
        ('bill', _('Invoice')),
    )
    payment_details = models.ForeignKey(
        PaymentDetails,
        on_delete=models.CASCADE,
        related_name='methods',
        verbose_name=_('Payment details')
    )
    payment_method = models.CharField(
        _('Payment method'), max_length=4, choices=PAYMENT_METHODS)

    def __str__(self):
        return self.get_payment_method_display()

    class Meta:
        verbose_name = _('Payment method')
        verbose_name_plural = _('Payment methods')


class Tariff(models.Model):
    payment_details = models.ForeignKey(
        PaymentDetails,
        on_delete=models.CASCADE,
        related_name='tariffs'
    )
    is_trial = models.BooleanField(_('Is trial'), default=False)
    is_student = models.BooleanField(_('Student tariff'), default=False)
    tariff_name = models.CharField(_('Tariff name'), max_length=100)
    tariff_description = models.TextField(_('Tariff description'), max_length=1000)
    base_month_price = models.IntegerField(_('Base price/month'))

    # periods

    def __str__(self):
        return self.tariff_name

    class Meta:
        verbose_name = _('Tariff')
        verbose_name_plural = _('Tariffs')


class TariffPeriod(models.Model):
    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.CASCADE,
        related_name='periods',
        verbose_name=_('Tariff')
    )
    month_amount = models.DecimalField(
        _('Subscription period'), default=0, max_digits=3, decimal_places=1)
    discount = models.FloatField(_('Discount'), default=0)

    def __str__(self):
        return f'{self.month_amount}-month ({self.discount}%)'

    class Meta:
        verbose_name = _('Tariff period')
        verbose_name_plural = _('Tariff periods')


class Subscription(models.Model):
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name=_('User')
    )
    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.CASCADE,
        verbose_name=_('Tariff')
    )
    tariffs = models.ForeignKey(
        PaymentDetails,
        on_delete=models.CASCADE,
        verbose_name=_('Payment details')
    )
    # payment_history
    end_date = models.BigIntegerField(_('Subscription end timestamp'))
    recurrent = models.BooleanField(_('Recurrent active'), default=False)
    recurrent_payment_task = models.ForeignKey(
        PeriodicTask,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Recurrent payment task')
    )
    pay_day = models.DateField(_('Pay day'), null=True)

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    @property
    def end_datetime(self):
        return dt.fromtimestamp(self.end_date)

    def __str__(self):
        return f'Subscription of {self.user.email}'


class School(models.Model):
    name = models.CharField(_('School name'), max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('School')
        verbose_name_plural = _('Schools')


class Promocode(models.Model):
    code = models.CharField(_('Code'), max_length=50, unique=True)
    discount = models.FloatField(_('Discount'), default=0.0)
    start = models.DateField(_('Start'))
    end = models.DateField(_('End'))
    is_student = models.BooleanField(_('Student promocode'), default=False)
    amount_of_use = models.IntegerField(_('Amount of use'), default=0)
    total_usage = models.IntegerField(_('Total usage'), default=0)
    tariff_period = models.DecimalField(
        _('Tariff period'),
        default=0,
        max_digits=3,
        decimal_places=1
    )
    school = models.ForeignKey(
        School,
        null=True, blank=True,
        on_delete=models.CASCADE,
        verbose_name=_('School'),
        related_name='promocodes'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{str(self.discount * 100)}%: {self.code.upper()}'

    def save(self, *args, **kwargs):
        if self.is_student and not str(self.code).startswith('SCH#'):
            self.code = f'SCH#{str(self.school).upper()}::{self.code.upper()}'
        else:
            self.code = self.code.upper()
        if self._state.adding:
            self.total_usage = self.amount_of_use
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Promocode')
        verbose_name_plural = _('Promocodes')


class SertificatePayment(models.Model):
    created_at = models.BigIntegerField(_('Payment timestamp'), null=True)
    created_dt = models.DateTimeField(auto_now_add=True)
    promocode = models.ForeignKey(
        Promocode,
        on_delete=models.CASCADE,
        verbose_name=_('Promocode'),
        related_name='sertificate_payments'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='sertificate_payments',
        verbose_name=_('Subscription'),
    )

    class Meta:
        verbose_name = _('Students promocode payment')
        verbose_name_plural = _('Students promocode payments')


class Payment(models.Model):
    class Meta:
        abstract = True

    created_at = models.BigIntegerField(_('Payment timestamp'), null=True)
    created_dt = models.DateTimeField(auto_now_add=True)
    period = models.IntegerField(_('Subscription period end'), null=True)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        default=1,
        verbose_name=_('Currency')
    )
    summ = models.IntegerField(_('Order total'))
    month_qty = models.SmallIntegerField(_('Month qty'), default=1)
    is_paid = models.BooleanField(_('Payment complete'), default=False)
    paid_at = models.DateTimeField(_('Paid at'), null=True)
    promocode = models.CharField(_('Promocode'), max_length=50, null=True, blank=True)


class CardPayment(Payment):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='card_payments',
        verbose_name=_('Subscription')
    )
    OrderId = models.UUIDField(default=uuid.uuid4, editable=False)
    recurrent = models.BooleanField(verbose_name=_('Recurrent'), default=True)

    class Meta:
        verbose_name = _('Card payment')
        verbose_name_plural = _('Card payments')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.created_at:
            self.created_at = time.mktime(self.created_dt.timetuple())
            self.save()
        user = self.subscription.user
        next_pay_date = dt.fromtimestamp(self.period)
        next_pay_day = next_pay_date.day
        next_pay_month = next_pay_date.month
        next_pay_year = next_pay_date.year
        last_day_of_pay_month = calendar.monthrange(next_pay_year, next_pay_month)

        crontab_month_map = {
            1: '*',
            3: '*/3',
            6: '*/6',
            12: '*/12'
        }
        if next_pay_day > last_day_of_pay_month[1]:
            next_pay_day = last_day_of_pay_month

        # self.subscription.recurrent_payment_task = PeriodicTask.objects.get_or_create(
        #     name=f'Recurrent payment for {user.email} every {self.month_qty} ({self.summ})rub.',
        #     task='subscription.tasks.recurrent_payment',
        #     crontab=CrontabSchedule.objects.get_or_create(
        #         month_of_year=crontab_month_map[self.month_qty],
        #         day_of_month=next_pay_day
        #     )[0],
        #     start_time=next_pay_date - timedelta(minutes=1),
        #     args=self.id
        # )[0]


def get_invoice_path(instance: 'BankTransfer', filename):
    return f'invoices/{instance.subscription.user.email}/{filename}'


class BankTransfer(Payment):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='bank_transfers',
        verbose_name=_('Subscription')
    )
    title = models.CharField(
        _('Invoice title'), max_length=255, blank=True, null=True)
    file = models.FileField(
        _('Invoice file'), blank=True, null=True, upload_to=get_invoice_path)

    class Meta:
        verbose_name = _('Bank transfer')
        verbose_name_plural = _('Bank transfers')


class TinkoffResponse(models.Model):
    TerminalKey = models.CharField('Номер терминала', max_length=255)
    OrderId = models.UUIDField('Номер заказа')
    Success = models.BooleanField('Выполнен')
    Status = models.CharField('Статус', max_length=255)
    PaymentId = models.PositiveBigIntegerField('ID платежа')
    ErrorCode = models.CharField('Код ошибки', max_length=255)
    Amount = models.IntegerField('Сумма (коп.)')
    CardId = models.IntegerField('ID карты')
    Pan = models.CharField('Номер карты', max_length=255)
    ExpDate = models.CharField('Срок действия карты', max_length=4)
    Token = models.CharField('Подпись', max_length=255)
    RebillId = models.CharField('ID рекуррентного платежа', max_length=255)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        payment = CardPayment.objects.filter(OrderId=self.OrderId).first()
        tariff = Tariff.objects.filter(is_student=False, is_trial=False).first()
        if self.Success and payment:
            payment.is_paid = True
            payment.paid_at = timezone.now()
            payment.save()
            payment.subscription.pay_day = timezone.now().date()
            payment.subscription.tariff = tariff
            payment.subscription.end_date = payment.period
            payment.subscription.recurrent = payment.recurrent
            payment.subscription.save()
        else:
            print(f'OrderId {self.OrderId} not found')
