from http import HTTPStatus

from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from poll.models.poll import Poll
from integration.models.telegram import TelegramIntegration
from integration.models.googlesheet import GoogleSheetIntegration


class AllintegrationsIsActiveView(APIView):

    def get(self, request, pk, format=None):

        try:
            poll = Poll.objects.get(poll_id=pk)
            if all([request.user != poll.user, not request.user.is_staff]):
                raise PermissionDenied()
            info = []
            try:
                info.append({'type': 'telegram_integration',
                             'is_active': TelegramIntegration.objects.get(
                                 poll=pk).is_active})
            except TelegramIntegration.DoesNotExist:
                info.append({'type': 'telegram_integration',
                             'is_active': None
                             })
            try:
                gsi = GoogleSheetIntegration.objects.get(id=pk)
                info.append({'type': 'googleSheet',
                             'is_active': gsi.is_active,
                             'spreadsheet_url': gsi.spreadsheet_url
                             })
            except GoogleSheetIntegration.DoesNotExist:
                info.append({'type': 'googleSheet',
                             'is_active': None
                             })
        except Poll.DoesNotExist:
            return Response({'result': 'Not found'}, status=HTTPStatus.NOT_FOUND)
        return Response({'poll_id': poll.pk, 'info': info}, status=HTTPStatus.OK)
