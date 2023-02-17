from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from common.models import UserChoice
from common.serializers import UserColumnSerializer
from common.views import PpmViewSet
from storyboards.models import Storyboard, Chrono, Frame, Shot, ChronoFrame
from storyboards.serializers import (
    StoryboardDetailSerializer,
    ChronoSerializer,
    FrameSerializer,
    ShotSerializer,
    StoryboardListSerializer,
    ChronoframeSerializer, ChronoListSerializer)


def create_default_storyboard_frame_columns(sb, user):
    column_data = [
        {'column_name': 'Камера', 'column_type': 'select'},
        {'column_name': 'Описание', 'column_type': 'text'},
        {'column_name': 'Актёры', 'column_type': 'contact'},
        {'column_name': 'Примечание', 'column_type': 'text'}
    ]
    serializer = UserColumnSerializer(
        data=column_data, many=True, context={'user': user})
    serializer.is_valid(raise_exception=True)
    usercolumns = serializer.create(serializer.validated_data)
    for usercolumn in usercolumns:
        sb.frame_columns.add(usercolumn)
        if usercolumn.column_type == 'select':
            choices = [
                {'choice': 'Ручная камера', 'color': 'blue'},
                {'choice': 'Штатив', 'color': 'red'},
                {'choice': 'Easyrig', 'color': 'green'},
                {'choice': 'Кран', 'color': 'blue'},
                {'choice': 'Dolly', 'color': 'red'},
                {'choice': 'Steadicam', 'color': 'blue'},
                {'choice': 'Motion control', 'color': 'red'},
            ]
            for choice in choices:
                UserChoice.objects.create(
                    **choice, host_usercolumn=usercolumn, owner=user)


class StoryboardViewSet(PpmViewSet):
    queryset = Storyboard.objects.prefetch_related('frames', 'chronos')
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return StoryboardListSerializer
        return StoryboardDetailSerializer

    def create(self, request, *args, **kwargs):
        if Storyboard.objects \
            .filter(host_project=kwargs['project_pk']) \
            .filter(deleted_id__isnull=True) \
            .count() > 0:
            raise ValidationError(
                {'error': 'only one Storyboard per project'})
        res = super().create(request, *args, **kwargs)
        sb = Storyboard.objects.get(pk=res.data['id'])
        create_default_storyboard_frame_columns(sb, request.user)
        serializer = self.get_serializer(instance=sb)
        return Response(serializer.data)


class ChronoViewSet(PpmViewSet):
    queryset = Chrono.objects.prefetch_related('chronoframes')
    http_method_names = ['get', 'post', 'patch', 'put', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return ChronoListSerializer
        return ChronoSerializer


class FrameViewSet(PpmViewSet):
    queryset = Frame.objects.prefetch_related('shots', 'userfields')
    serializer_class = FrameSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']


class ShotViewSet(PpmViewSet):
    queryset = Shot.objects.all()
    serializer_class = ShotSerializer
    parser_classes = (MultiPartParser,)


class ChronoFrameViewSet(PpmViewSet):
    queryset = ChronoFrame.objects.all()
    serializer_class = ChronoframeSerializer
    http_method_names = ['get', 'patch', 'delete']
