from rest_framework import viewsets
from rest_framework import permissions

from poll.models.analitics import PollAnalitics
from poll.serializers.analitics import PollAnaliticsSerializer


class PollAnaliticsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be created, viewed, edited or deleted.
    """
    serializer_class = PollAnaliticsSerializer

    def get_queryset(self):

        queryset = PollAnalitics.objects.all().order_by('-id')

        return queryset

    def get_permissions(self):

        permission_classes = [permissions.IsAuthenticated, ]

        return super(PollAnaliticsViewSet, self).get_permissions()

    def get_serializer_context(self):
        context = super(PollAnaliticsViewSet, self).get_serializer_context()
        context['poll_id'] = self.kwargs.get('poll_id')
        context['survey_id'] = self.kwargs.get('survey_id')
        context['user'] = self.request.user
        context['request'] = self.request
        return context
