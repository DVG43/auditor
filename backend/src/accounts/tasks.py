import requests

from django_celery import app
from smtplib import SMTPRecipientsRefused

from django.conf import settings
from templated_email import send_templated_mail
from rest_framework.exceptions import ValidationError


@app.task(name="send_email_msg")
def send_email_msg(to_email, context, template):
    try:
        return send_templated_mail(
            template_name=template,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            context=context
        )
    except SMTPRecipientsRefused:
        raise ValidationError({'error': 'email not valid'})


@app.task(name="crm_deal_update")
def crm_deal_update(b24_deal_id: int, signal: str):
    URL_DEAL_MOVE = 'https://auditorpro.bitrix24.ru/rest/1/tmanclcqyl3kp154/crm.deal.update'
    signal_map = {
        'email_verified': 'C54:UC_8UK7KT',
        'subscription_ended': 'C54:PREPARATION',
    }
    if b24_deal_id:
        body = {
            "id": b24_deal_id,
            "fields":
                {
                    "STAGE_ID": signal_map[signal],
                    # "PROBABILITY": 70
                }
        }
        res = requests.post(url=URL_DEAL_MOVE, json=body)
        if res.status_code == 200:
            result = res.json()
            if 'result' in result and result['result'] > 0:
                print(f'44 Accounts.tasks: Deal {b24_deal_id} updated')
            elif 'error' in result:
                print(f'46 Accounts.tasks: Response failed: {result["error"]}')
