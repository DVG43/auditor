import json

from datetime import datetime

# обходим защиту csrf
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, JsonResponse
from django.views import View

from .services import TinkoffAPI


class Tinkoff(View):
    """Класс обработки запросов к API Тинькофф Банк"""
    _tinkoffAPI = None

    @property
    def tinkoffAPI(self):
        if not self._tinkoffAPI:
            self._tinkoffAPI = TinkoffAPI()
        return self._tinkoffAPI

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Отправка данных запроса.
        JSON запроса:
        Amount -> str = Сумма в копейках
        OrderId -> str = id счета на оплату
        Description -> str = Краткое описание платежа
        Receipt -> json = JSON объект с данными чека
        Email, Phone -> = Должен быть указан или один из пунктов, либо оба
        Taxation -> str = Система налогообложения
        Items -> obj = Информация об оплачиваемой услуге
        Name -> str = Наименование (128 символов макс.)
        Price -> int = Цена в копейках
        Quantity -> float = Кол-во
        Amount -> int = Сумма в копейках
        Tax -> str = Ставка налога

        Пример:
        {
            "Amount":"50000",
            "OrderId":"49",
            "Description":"Подарочная карта на 500 рублей",
            "Receipt": {
                "Email":"a@test.ru",
                "Phone":"+79031234567",
                "Taxation":"patent",
                "Items": [
                    {
                        "Name":"Наименование товара 1",
                        "Price":50000,
                        "Quantity":1.00,
                        "Amount":50000,
                        "Tax":"none"
                    }
                ]
            }
        }
        """
        data = json.loads(request.body.decode())
        result = self.tinkoffAPI.init(data)

        # Отправляем номер платежа в сессию, чтобы можно было подтянуть его через GET
        try:
            request.session['PaymentId'] = result['PaymentId']
            request.session['Payment_created'] = str(datetime.now())
            return HttpResponse(result['PaymentURL'])
        except:
            return JsonResponse(result, status=400)

    def get(self, request, *args, **kwargs):
        """Принимаем запрос с использованием сессии

        Success -> bool = Успешность операции
        ErrorCode -> str = Код ошибки, '0' - если успех
        Message -> str = Краткое описание ошибки
        TerminalKey -> str = Идентификатор терминала
        Status -> str = Статус транзакции
        PaymentId -> str = Уникальный номер транзакции
        OrderId -> str = Уникальный номер счета на оплату
        Amount -> int = Сумма в копейках
        Payment_created -> str = Дата и время проведения транзакции в случае успеха

        Пример:
        {
            "Success": true,
            "ErrorCode": "0",
            "Message": "OK",
            "TerminalKey": "1652440412477DEMO",
            "Status": "CONFIRMED",
            "PaymentId": "1554475853",
            "OrderId": "50",
            "Params": [
                {
                    "Key": "Route",
                    "Value": "ACQ"
                }
            ],
            "Amount": 50000,
            "Payment_created": "2022-07-21 09:01:33.625963"
        }
        """

        # Есть ли PaymentId в сессии
        if request.session.get('PaymentId'):
            result = self.tinkoffAPI.status(request.session['PaymentId'])
        else:
            return JsonResponse({'Payment ID': 'Not found'}, status=404)

        # Если данные валидны, обрабатываем...
        try:
            if result.get('Status') \
                    and (result['Status'] == 'CONFIRMED' or result['Status'] == 'AUTHORIZED'):
                result['Payment_created'] = request.session['Payment_created']
                # Отправляем ответ json от Тинькофф
                return JsonResponse(result, status=200)

            # Если в ответе ошибка...
            elif result.get('Error'):
                return JsonResponse({'Error status': str(result)})

            # Если платеж не проведен...
            else:
                return JsonResponse({'Payment status': result['Status']})
        except ValueError as e:
            return JsonResponse({'Bad request': e}, status=400)
