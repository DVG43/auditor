from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from callsheets.models import (
    Callsheet,
    Location,
    CallsheetLogo,
    LocationMap,
    Callsheetmember,
)
from callsheets.serializers import (
    CallsheetSerializer,
    LocationSerializer,
    CallsheetLogoSerializer,
    LocationMapSerializer,
    CallsheetListSerializer,
    CallsheetmemberSerializer,
)
from callsheets.utils import get_client_ip, get_location, get_weather
from common.mixins import CopyAndMoveDocMixin
from common.permissions import IsOwnerOrIsProjectAccess
from common.utils import contact_to_callsheetmember, add_userfields, \
    get_object_or_404, recount_disk_space, update_host_modified_date, unpack_nested_kwargs
from common.views import PpmViewSet


class CallsheetmemberViewSet(PpmViewSet):
    queryset = Callsheetmember.objects.prefetch_related('userfields')
    serializer_class = CallsheetmemberSerializer


class CallsheetViewSet(PpmViewSet, CopyAndMoveDocMixin):
    permission_classes = [IsOwnerOrIsProjectAccess]
    queryset = Callsheet.objects.prefetch_related(
        'locations', 'members', 'userfields'
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return CallsheetListSerializer
        else:
            return CallsheetSerializer

    def create(self, request, *args, **kwargs):
        print(31, 'CallsheetVS.create')
        ip = get_client_ip(request)
        locaition = get_location(ip)
        cs = super().create(request, *args, **kwargs)
        cs_id = cs.data['id']
        cs_date = cs.data['date']
        weather = get_weather(locaition, cs_date)
        Callsheet.objects.filter(id=cs_id).update(**weather, **locaition)
        print(33, 'CallsheetVS add default location')
        data = {'host_callsheet': cs_id}
        serializer = LocationSerializer(
            data=data, context={'user': request.data['owner']})
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        cs = Callsheet.objects.get(pk=cs_id)
        serializer = self.get_serializer(cs)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        print(59, 'CallsheetViewSet.update')
        if 'members' in request.data:
            members = request.data.pop('members')
            if members and isinstance(members, list) \
                    and not isinstance(members[0], int):
                raise ParseError(
                    {'error': {'members': 'must be a list of Int ids'}})

            cs = self.get_object()
            for cnt_id in members:
                cnt = get_object_or_404('contact', cnt_id)
                csm = contact_to_callsheetmember(cnt, cs)
                add_userfields(request.user, cs, csm)
        cs_id = kwargs['pk']
        if "city" in request.data:
            city = request.data['city']
            cs = Callsheet.objects.get(pk=cs_id)
            if city != cs.city and 'manual' not in request.data:
                cs_date = cs.date
                location = {'lat': request.data['lat'], 'lng': request.data['lng']}
                weather = get_weather(location, cs_date)
                request.data.update(weather)
        if "date" in request.data:
            date = request.data['date']
            cs = Callsheet.objects.get(pk=cs_id)
            if date != cs.date:
                location = {'lat': cs.lat, 'lng': cs.lng}
                weather = get_weather(location, date)
                request.data.update(weather)
        return super().update(request, *args, **kwargs)


class LocationViewSet(PpmViewSet):
    queryset = Location.objects.prefetch_related('userfields')
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrIsProjectAccess]
    http_method_names = ['get', 'post', 'patch', 'delete']


class CallsheetLogoViewSet(PpmViewSet):
    queryset = CallsheetLogo.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrIsProjectAccess]
    serializer_class = CallsheetLogoSerializer
    parser_classes = (MultiPartParser, )

    def destroy(self, request, *args, **kwargs):
        print(59, 'CallsheetLogoViewSet.destroy')
        instance = self.get_object()
        owner = instance.owner
        # обновляем время и юзера последнего изменения вызывного
        # при изменении дочерних объектов
        kw = unpack_nested_kwargs(kwargs, "callsheetlogo")
        update_host_modified_date(kw, request.user.email)
        self.perform_destroy(instance)
        recount_disk_space(owner)
        return super().list(request)


class LocationMapViewSet(PpmViewSet):
    queryset = LocationMap.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrIsProjectAccess]
    serializer_class = LocationMapSerializer
    parser_classes = (MultiPartParser, )

    class Meta:
        model = LocationMap

    def destroy(self, request, *args, **kwargs):
        print(75, 'LocationMapViewSet.destroy')
        instance = self.get_object()
        owner = instance.owner
        # обновляем время и юзера последнего изменения вызывного
        # при изменении дочерних объектов
        kw = unpack_nested_kwargs(kwargs, "locationmap")
        update_host_modified_date(kw, request.user.email)
        self.perform_destroy(instance)
        recount_disk_space(owner)
        return super().list(request)
