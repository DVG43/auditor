import time
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from subscription.errors import errors
from subscription.models import (
    Tariff,
    PaymentDetails,
    Currency,
    CardPayment,
    SertificatePayment,
    PaymentMethod,
    TariffPeriod,
    Subscription
)

full_description = _('The full plan includes unlimited access to all '
                     'PPM functionality. Unlimited number of '
                     'shootingplans, storyboards, projects. The '
                     'ability to share your documents and follow the '
                     'development of PPM.')


def check_or_create_subscription_objects():
    trial_tariff = Tariff.objects.filter(is_trial=True)
    if not trial_tariff:
        pd = PaymentDetails.objects.create()
        trial_description = _('Don`t worry - all your data, collected '
                              'shootingplans and storyboards securely stored. '
                              'To continue using PPM, choose the duration of '
                              'the subscription and pay for it.')
        trial = Tariff.objects.create(
            payment_details=pd,
            is_trial=True,
            tariff_name=_('Trial period one month'),
            tariff_description=trial_description,
            base_month_price=0
        )
        TariffPeriod.objects.create(tariff=trial, month_amount='1')

        full = Tariff.objects.create(
            payment_details=pd,
            is_trial=False,
            tariff_name=_('Full access'),
            tariff_description=full_description,
            base_month_price=900
        )
        TariffPeriod.objects.create(tariff=full, month_amount=1, discount=0)
        TariffPeriod.objects.create(tariff=full, month_amount=3, discount=10)
        TariffPeriod.objects.create(tariff=full, month_amount=6, discount=15)
        TariffPeriod.objects.create(tariff=full, month_amount=12, discount=25)

        Currency.objects.create(
            payment_details=pd,
            currency='RUB',
            currency_icon='₽'
        )
        PaymentMethod.objects.create(
            payment_details=pd,
            payment_method='card'
        )
        PaymentMethod.objects.create(
            payment_details=pd,
            payment_method='bill'
        )


def check_or_create_student_tariff():
    student_tariff = Tariff.objects.filter(is_student=True)
    if not student_tariff:
        pd = PaymentDetails.objects.first()
        Tariff.objects.create(
            payment_details=pd,
            is_trial=False,
            is_student=True,
            tariff_name=_('Student tariff'),
            tariff_description=full_description,
            base_month_price=0
        )


def student_tariff_activate(code, user):
    if not code.is_student:
        raise ValidationError({'error': errors['invalid']})
    if not (code.start <= datetime.now().date() <= code.end):
        raise ValidationError({'error': errors['expired']})
    if code.amount_of_use <= 0:
        raise ValidationError({'error': errors['amount']})

    subscription = Subscription.objects.get(user=user)
    sert_payments = SertificatePayment.objects.filter(subscription=subscription)
    if sert_payments:
        raise ValidationError({'error': errors['already']})
    card_payments = CardPayment.objects.filter(
        subscription=subscription,
        is_paid=True
    )
    if card_payments:
        raise ValidationError({'error': errors['paid']})

    student_end_date = timezone.now() + timedelta(
        days=float(code.tariff_period) * 30
    )
    student_end_unix = int(time.mktime(student_end_date.timetuple()))
    student_tariff = Tariff.objects.filter(is_student=True).first()

    subscription.user = user
    subscription.tariff = student_tariff
    subscription.tariffs_id = 1
    subscription.end_date = student_end_unix
    subscription.recurrent = False
    subscription.save()

    SertificatePayment.objects.create(
        created_at=int(time.mktime(timezone.now().timetuple())),
        promocode=code,
        subscription=subscription
    )
    code.amount_of_use -= 1
    code.save()
