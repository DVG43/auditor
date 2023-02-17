from common.mixins import CopyAndMoveDocMixin
from common.views import PpmViewSet
from shootingplans.models import Shootingplan, Unit, Unitframe
from shootingplans.serializers import (
    ShootingplanSerializer,
    UnitSerializer,
    UnitListSerializer,
    UnitframeSerializer,
    ShootingplanListSerializer
)


class ShootingplanViewSet(PpmViewSet, CopyAndMoveDocMixin):
    queryset = Shootingplan.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return ShootingplanListSerializer
        else:
            return ShootingplanSerializer


class UnitViewSet(PpmViewSet):
    queryset = Unit.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return UnitListSerializer
        return UnitSerializer


class UnitframeViewSet(PpmViewSet):
    queryset = Unitframe.objects.all()
    serializer_class = UnitframeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
