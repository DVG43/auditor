import os
import random
import string
from pprint import pprint

import requests

from accounts.tasks import send_email_msg


def generate_code():
    code = ''.join(random.choice(string.digits) for _ in range(4))
    return code


def send_activation_email(user):
    context = {
        'subject': 'PPM: Код активации',
        'body': 'Привет! Хотим убедиться, что ты не робот. Введи код на '
                'странице регистрации, чтобы активировать учетную запись.',
        'code': str(user.code)
    }
    send_email_msg.delay(user.email, context, 'activation')


def send_reset_password_email(user, password):
    context = {
        'subject': 'PPM: Новый пароль',
        'body': 'Привет! Мы получили запрос на смену пароля. Держи новый:',
        'password': password
    }
    send_email_msg.delay(user.email, context, 'new_password')


def send_change_email(user, new_email):
    context = {
        'subject': 'PPM: Код подтверждения для смены email адреса',
        'body': f'    Здравствуйте!\n'
                f'Для смены адреса электронной почты введите указанный ' 
                f'ниже код в приложении: \n' 
                f'{str(user.code)}\n' 
                f'Адрес будет изменён на {new_email}\n' f'---\n' 
                f'Администрация PPM'
    }
    send_email_msg.delay(new_email, context, 'change_email_confirm')

    context = {
        'subject': 'PPM: Запрос на смену email адреса',
        'body': f'    Здравствуйте!\n'
                f'С Вашего аккаунта поступил запрос на смену адреса '
                f'электронной почты.\n'
                f'Адрес будет изменён на {new_email}\n'
                f'Если Вы не отправляли запрос, срочно свяжитесь с нами!\n'
                f'---\n'
                f'Администрация PPM'
    }
    send_email_msg.delay(user.email, context, 'change_email_warning')


# создание сделки в Битрикс24 с зарегистрировавшимся пользователем
# https://auditorpro.bitrix24.ru/rest/830/4eyrscwhthvye0fb/
URL_CONTACT_LIST = 'https://auditorpro.bitrix24.ru/rest/1328/9i8vnnsahnudwsd8/crm.contact.list'
URL_CONTACT_ADD = 'https://auditorpro.bitrix24.ru/rest/1328/89hyzcvqskkmzphp/crm.contact.add'
URL_DEAL_ADD = 'https://auditorpro.bitrix24.ru/rest/1/0vwi0z9ihwvcaqr8/crm.deal.add'


def crm_contact_check(user):
    """
    Проверка на существование контакта в Б24, по email,
    если такого контакта нет, то выполняется добавление нового контакта
    """
    if not os.getenv("IS_TEST"):
        body = {
            "FILTER": {"EMAIL": user.email},
            "SELECT": ["ID", "NAME", "EMAIL"]
        }
        b24_response = 'ok'

        res = requests.post(url=URL_CONTACT_LIST, json=body)
        if res.status_code == 200:
            result = res.json()
            if 'total' in result and result['total'] == 1:
                user.b24_contact_id = result['result'][0]['ID']
                user.save()
                print(50, 'User found in B24. User_id =', user.b24_contact_id)
            elif 'total' in result and result['total'] > 1:
                print(f'response failed: more than one contacts with this e-mail')
                return None
            elif 'error' in result:
                print(f'response failed:{result["error"]}')
                return None

            # добавление контакта в Б24
            if not user.b24_contact_id and b24_response == 'ok':
                print(64, 'Add new contact to B24')
                body = {
                    "FIELDS": {
                        "NAME": user.first_name,
                        "LAST_NAME": user.last_name,
                        "EMAIL": [
                            {
                                "VALUE_TYPE": "WORK",
                                "VALUE": user.email,
                                "TYPE_ID": "EMAIL"
                            }
                        ]
                    }
                }
                res = requests.post(url=URL_CONTACT_ADD, json=body)
                if res.status_code == 200:
                    result = res.json()
                    if 'result' in result and result['result'] > 0:
                        user.b24_contact_id = result['result']
                        user.b24_deal_id = crm_deal_add(user.b24_contact_id)
                        user.save()
                    elif 'error' in res:
                        print(f'response failed:{result["error"]}')


def crm_deal_add(b24_contact_id):
    """
    добавление сделки для контакта
    """
    body = {
        "FIELDS": {
            "CONTACT_ID": b24_contact_id,
            "TYPE_ID": "SERVICES",
            "CATEGORY_ID": 54,
            "SOURCE_ID": "WEB",
            "SOURCE_DESCRIPTION": "PPM",
        }
    }

    res = requests.post(url=URL_DEAL_ADD, json=body)
    if res.status_code == 200:
        result = res.json()
        if 'result' in result and result['result'] > 0:
            b24_deal_id = result['result']
            print(f'Deal {b24_deal_id} created')
            return b24_deal_id
        elif 'error' in result:
            print(f'response failed:{result["error"]}')
    return 0


def get_upload_path(instance, filename):
    return f"{str(instance.pk)}/{filename}/"
