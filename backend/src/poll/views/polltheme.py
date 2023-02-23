from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from poll.models.poll import Poll
from poll.models.polltheme import PollTheme
from poll.serializers.polltheme import PollThemeSerializer, PollThemeListSerializer
from poll.service import get_serialized_questions


class PollThemeViewSet(ModelViewSet):
    queryset = PollTheme.objects.all()
    serializer_class = PollThemeSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        super(PollThemeViewSet, self).destroy(request, *args, **kwargs)
        return Response({'result': 'ok'})


class PollThemeListView(ListAPIView):
    serializer_class = PollThemeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return PollTheme.objects.filter(Q(user=self.request.user) | Q(is_standard=True))

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        data = {
            'design': serializer.data,
        }
        return Response(data)


class PollThemeActiveRetrieveView(RetrieveAPIView):
    queryset = PollTheme.objects.all()
    serializer_class = PollThemeSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        poll_id = self.request.parser_context['kwargs'].get('pk', 0)
        instance = get_object_or_404(self.queryset, poll_id=int(poll_id))
        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = {
            'design': serializer.data,
        }
        return Response(data)


class PollThemeActiveListView(ListAPIView):
    queryset = PollTheme.objects.all()
    serializer_class = PollThemeListSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        poll_id = self.request.parser_context['kwargs'].get('pk')
        return {
            'request': self.request,
            'poll_id': poll_id
        }

    def get_queryset(self):
        poll_id = self.request.query_params.get('pk')
        return PollTheme.objects.distinct().filter(Q(user=self.request.user) | Q(poll=poll_id) | Q(is_standard=True))

    def list(self, request, *args, **kwargs):
        poll_id = self.request.parser_context['kwargs'].get('pk')
        poll = get_object_or_404(Poll, poll_id=poll_id)

        queryset = self.get_queryset()

        design_serializer = self.get_serializer(queryset.filter(poll=poll.poll_id, user=self.request.user, is_active=True).first())
        themes_serializer = self.get_serializer(queryset.filter(poll=poll.poll_id, user=self.request.user, is_active=False), many=True)

        data = {
            'design': design_serializer.data,
            'themes': themes_serializer.data,
            'questions': get_serialized_questions(poll.get_questions())
        }
        return Response(data)
