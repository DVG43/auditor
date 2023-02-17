from celery import shared_task

from subscription.models import CardPayment


@shared_task(name='recurrent_payment')
def recurrent_payment(payment_id):
    payment = CardPayment.objects.get(pk=payment_id)



