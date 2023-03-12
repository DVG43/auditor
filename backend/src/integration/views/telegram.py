from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from integration.models.telegram import TelegramIntegration
from integration.serializers.telegram import TelegramIntegrationSerializer
from poll.models.poll import Poll


class TelegramIntegrationView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    queryset = TelegramIntegration.objects.all()
    serializer_class = TelegramIntegrationSerializer

    def get_serializer_context(self):
        context = super(TelegramIntegrationView, self).get_serializer_context()
        context['poll_id'] = self.kwargs.get('poll_id')
        context['user'] = self.request.user
        context['request'] = self.request
        return context

    def get_object(self):
        poll_id = self.kwargs.get('poll_id')
        poll = get_object_or_404(Poll.objects.all(), poll_id=poll_id)
        if all([self.request.user != poll.user, not self.request.user.is_staff]):
            raise PermissionDenied()
        obj, _ = TelegramIntegration.objects.get_or_create(poll=poll)
        return obj


class TelegramIntegrationSendMessage(APIView):
    def post(self, request, poll_id):
        obj = get_object_or_404(
            TelegramIntegration.objects.all(),
            poll_id=poll_id,
        )
        message = request.data.get('message', None)
        obj.send_message(message=message, request=request, survey_passing_id=2)
        return Response({"result": "message sent"})


class IntegrationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, poll_id):
        poll = get_object_or_404(
            Poll.objects.all(),
            poll_id=poll_id,
        )
        return Response({
            "telegram_integration": poll.telegram_integration_is_active()
        })
