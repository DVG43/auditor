from django.urls import path, include
from rest_framework.routers import SimpleRouter

from subscription.views import CardPaymentViewSet, TinkoffResponseReceiver, \
    PromocodeView, SertificatePaymentViewSet, SertificatePaymentsViewSet

subs = SimpleRouter()
subs.register('card_payments', CardPaymentViewSet)
subs.register('sertificate_payments', SertificatePaymentsViewSet)


urlpatterns = [
    path('payment_result/', TinkoffResponseReceiver.as_view()),
    path('promocodes/', PromocodeView.as_view()),
    path('sertificate/', SertificatePaymentViewSet.as_view()),
    path('', include(subs.urls)),

]
