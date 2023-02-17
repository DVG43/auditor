import time

from rest_framework import serializers

from subscription.models import (
    Subscription,
    TariffPeriod,
    Tariff,
    TPI,
    PaymentDetails,
    Currency,
    CardPayment,
    BankTransfer,
    TinkoffResponse,
    SertificatePayment
)


class TariffPeriodSerializer(serializers.ModelSerializer):
    month_amount = serializers.IntegerField()

    class Meta:
        model = TariffPeriod
        fields = ['month_amount', 'discount']


class TariffSerializer(serializers.ModelSerializer):
    periods = TariffPeriodSerializer(many=True)

    class Meta:
        model = Tariff
        fields = [
            'tariff_name',
            'tariff_description',
            'base_month_price',
            'periods'
        ]


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['currency', 'currency_icon']


class PaymentDetailsSerializer(serializers.ModelSerializer):
    tariffs = serializers.SerializerMethodField(read_only=True)
    currencies = CurrencySerializer(many=True)
    methods = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PaymentDetails
        fields = [
            'currencies',
            'methods',
            'tariffs'
        ]

    def get_tariffs(self, obj):
        tariffs = obj.tariffs.exclude(is_trial=True).first()
        return TariffSerializer(instance=tariffs).data

    def get_methods(self, obj):
        return [m.payment_method for m in obj.methods.all()]


class CurrentTariffSerializer(serializers.ModelSerializer):
    end_date = serializers.SerializerMethodField()
    recurrent = serializers.SerializerMethodField()

    class Meta:
        model = Tariff
        fields = [
            'tariff_name',
            'tariff_description',
            'is_trial',
            'end_date',
            'recurrent',
            'is_student'
        ]

    def get_end_date(self, obj):
        user = self.context
        if user.subscription:
            return user.subscription.end_date

    def get_recurrent(self, obj):
        user = self.context
        if user.subscription:
            return user.subscription.recurrent


class PromocodeSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField(read_only=True)
    code = serializers.CharField()
    discount = serializers.FloatField(read_only=True)


class PaymentSerializer(serializers.ModelSerializer):
    currency = serializers.StringRelatedField(source='currency.__str__')
    promocode = serializers.CharField()


class SertificatePaymentsSerializer(serializers.ModelSerializer):
    promocode = serializers.SerializerMethodField()
    tariff_period = serializers.SerializerMethodField()

    class Meta:
        model = SertificatePayment
        fields = [
            'id',
            'subscription',
            'tariff_period',
            'promocode',
            'created_at'
        ]

    def get_promocode(self, obj):
        return obj.promocode.code

    def get_tariff_period(self, obj):
        return obj.promocode.tariff_period


class SertificatePaymentSerializer(serializers.Serializer):
    promocode = serializers.CharField()


class CardPaymentSerializer(PaymentSerializer):
    payment_id = serializers.IntegerField(source='period', required=True)
    promocode = serializers.CharField()
    subscription_id = serializers.IntegerField(write_only=True)
    paid_at = serializers.SerializerMethodField()
    OrderId = serializers.UUIDField(required=False)

    class Meta:
        model = CardPayment
        fields = [
            'id',
            'payment_id',
            'summ',
            'subscription_id',
            'is_paid',
            'created_at',
            'paid_at',
            'month_qty',
            'OrderId'
        ]

    def get_paid_at(self, obj):
        if obj.paid_at:
            return int(time.mktime(obj.paid_at.timetuple()))
        return None


class BankTransferSerializer(PaymentSerializer):
    class Meta:
        model = BankTransfer
        fields = [
            'id',
            'date',
            'days_amount',
            'summ',
            'currency',
            'title',
            'file',
            'is_paid',
            'promocode',
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    current_tariff = CurrentTariffSerializer(source='tariff')
    payment_options = PaymentDetailsSerializer(source='tariffs')
    payment_history = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'current_tariff',
            'payment_options',
            'payment_history',
        ]

    def get_payment_history(self, obj):
        card_payments = CardPaymentSerializer(
            instance=obj.card_payments.all(), many=True)
        bank_transfers = BankTransferSerializer(
            instance=obj.bank_transfers.all(), many=True)
        sertificate_payments = SertificatePaymentsSerializer(
            instance=obj.sertificate_payments.all(), many=True
        )
        return {
            'card_payments': card_payments.data,
            'bank_transfers': bank_transfers.data,
            'sertificate_payments': sertificate_payments.data,
        }


class TPISerializer(serializers.ModelSerializer):
    class Meta:
        model = TPI
        fields = ['id', 'number', 'title']


class TinkoffResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TinkoffResponse
        fields = '__all__'
