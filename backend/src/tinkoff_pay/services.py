import hashlib
import json
import os
import requests

from .utils import Encoder

# Переменные для работы с API Тинькофф
TINKOFF_INIT_PAY = os.environ.get('TINKOFF_INIT_PAY')
TINKOFF_STATUS_PAY = os.environ.get('TINKOFF_STATUS_PAY')
TINKOFF_TERMINAL_KEY = os.environ.get('TINKOFF_TERMINAL_KEY')
TINKOFF_TERMINAL_PASSWORD = os.environ.get('TINKOFF_TERMINAL_PASSWORD')


class TinkoffAPI:
    _terminal_key = None
    _password_key = None

    def __init__(self, terminal_key=None, password_key=None):
        self._terminal_key = terminal_key
        self._password_key = password_key

    @property
    def password_key(self):
        if not self._password_key:
            self._password_key = TINKOFF_TERMINAL_PASSWORD
        return self._password_key

    @property
    def terminal_key(self):
        if not self._terminal_key:
            self._terminal_key = TINKOFF_TERMINAL_KEY
        return self._terminal_key

    def _token(self, data):
        array = [
            ['Password', self.password_key],
        ]

        if 'TerminalKey' not in data:
            array.append(['TerminalKey', self.terminal_key])

        for k, v in data.items():
            if k == 'Token':
                continue
            if isinstance(v, bool):
                array.append([k, str(v).lower()])
            elif not isinstance(v, list) or not isinstance(v, dict):
                array.append([k, v])

        array.sort(key=lambda i: i[0])
        values = ''.join(map(lambda i: str(i[1]), array))

        gen_token = hashlib.sha256()
        gen_token.update(values.encode())
        return gen_token.hexdigest()

    def request_to_API(self, url, data):
        data.update({
            'TerminalKey': self.terminal_key,
            'Token': self._token(data),
        })

        resp = requests.post(url, data=json.dumps(data, cls=Encoder), headers={'Content-Type': 'application/json'})

        try:
            response = resp.json()
            return response
        except ValueError as e:
            return {'Error': e}

    def init(self, data):
        """
        Инициализация платежа
        TINKOFF_INIT_PAY=https://securepay.tinkoff.ru/v2/Init/
        TINKOFF_STATUS_PAY=https://securepay.tinkoff.ru/v2/GetState/
        """
        # url = 'https://rest-api-test.tinkoff.ru/v2/Init/'
        url = TINKOFF_INIT_PAY

        response = self.request_to_API(url, data)

        return response

    def status(self, payment_id):
        """Проверка статуса платежа"""
        # url = 'https://rest-api-test.tinkoff.ru/v2/GetState'
        url = TINKOFF_STATUS_PAY

        data = {'PaymentId': payment_id}
        response = self.request_to_API(url, data)

        return response
