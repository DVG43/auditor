import time
from datetime import datetime, timedelta

import rest_framework.parsers
from django.contrib.auth import get_user_model as User
from django.utils import timezone
from rest_framework import viewsets, views
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsOwner
from subscription.errors import errors
from subscription.models import (
    CardPayment, Promocode,
    SertificatePayment,
    Tariff,
    Subscription
)
from subscription.serializers import (
    SubscriptionSerializer,
    CardPaymentSerializer,
    TinkoffResponseSerializer,
    SertificatePaymentSerializer,
    SertificatePaymentsSerializer,
    PromocodeSerializer
)
from subscription.utils import (
    check_or_create_student_tariff,
    student_tariff_activate
)


class SubscriptionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        serializer = SubscriptionSerializer(
            instance=user.subscription, context=request.user)
        return Response(serializer.data)


class SubscriptionCancelView(views.APIView):
    permission_classes = [IsOwner]

    def post(self, request):
        user = self.request.user
        user.subscription.recurrent = False
        user.subscription.save()
        serializer = SubscriptionSerializer(
            instance=user.subscription, context=request.user)
        return Response(serializer.data)


class CardPaymentViewSet(viewsets.ModelViewSet):
    queryset = CardPayment.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    serializer_class = CardPaymentSerializer

    def create(self, request, *args, **kwargs):
        subscription = request.user.subscription
        request.data.update({'subscription_id': subscription.id})
        response = super().create(request, *args, **kwargs)
        payment = CardPayment.objects.get(pk=response.data['id'])
        return Response({'OrderId': payment.OrderId})

    def perform_destroy(self, instance):
        if not instance.is_paid:
            instance.delete()


class TinkoffResponseReceiver(views.APIView):
    parser_classes = [rest_framework.parsers.JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = TinkoffResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response('OK')


class PromocodeView(views.APIView):
    throttle_scope = 'promocodes'
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        if not code:
            raise ValidationError({'error': errors['empty']})
        promocode = Promocode.objects.filter(code=code.upper()).first()
        if promocode and (promocode.start <= datetime.now().date() <= promocode.end):
            is_student = promocode.is_student
            if is_student:
                if promocode.amount_of_use > 0:
                    is_valid = True
                else:
                    is_valid = False
            else:
                is_valid = True
            discount = promocode.discount
        else:
            is_valid = False
            is_student = False
            discount = 0

        data = {
            'code': code,
            'is_valid': is_valid,
            'discount': discount,
            'is_student': is_student,
        }
        return Response(data)


class SertificatePaymentViewSet(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SertificatePaymentSerializer

    def post(self, request):
        check_or_create_student_tariff()
        if not request.data['promocode']:
            raise ValidationError({'error': errors['empty']})
        promocode = request.data['promocode']
        code = Promocode.objects.filter(code=promocode.upper()).first()
        user = User().objects.filter(email=request.user).first()
        if code:
            student_tariff_activate(code, user)
            return Response('Student tariff activated')
        else:
            raise ValidationError({'error': errors['invalid']})


class SertificatePaymentsViewSet(viewsets.ModelViewSet):
    queryset = SertificatePayment.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    serializer_class = SertificatePaymentsSerializer
