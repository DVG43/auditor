from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import viewsets, views
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsOwner
from common.utils import get_model, get_object_or_404
from common.views import (
    PpmViewSet,
    unpack_nested_kwargs,
)
from contacts import serializers
from contacts.models import Position, Department, Contact
from contacts.serializers import (ContactSerializer,
                                  ContactSearchSerializer,
                                  ContactSearchSerializerRequest,
                                  ContactsDeleteListRequest)


class PositionViewSet(PpmViewSet):
    queryset = Position.objects.all()
    serializer_class = serializers.PositionSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']


class DepartmentViewSet(PpmViewSet):
    queryset = Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']


class ContactViewSet(PpmViewSet):
    queryset = Contact.objects.prefetch_related('department', 'position')
    permission_classes = [IsOwner]
    serializer_class = ContactSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'put']

    def get_queryset(self):
        print(32, 'ContactVS.get_queryset')
        # queryset = user.get_objects_with_perms(
        #     get_model(base_name), ['read', 'edit', 'own'])
        base_name = self.basename
        kw = unpack_nested_kwargs(self.kwargs, self.basename)
        user = self.request.user
        queryset = Contact.objects.filter(owner=user)

        if base_name == 'contact' and kw['host'] == 'project':
            host_obj = get_object_or_404(kw['host'], kw['host_pk'])
            queryset = host_obj.contacts.all()

        if kw['host'] == 'contact' and kw['host_pk'] == "0":
            return get_model(base_name).objects.filter(owner=user)
        return queryset

    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        print('ContactVS.destroy')
        kw = unpack_nested_kwargs(kwargs, self.basename)
        instance = get_object_or_404(self.basename, kw['base_pk'])
        # Отвязка контакта без глобального удаления:
        # Привязка контакта:
        # DELETE /project/3/contacts/2/ (удалить контакт 2 из проекта 3)
        if kw['host']:
            host_obj = get_object_or_404(kw['host'], kw['host_pk'])
            host_obj.contacts.remove(instance)
            return Response(
                {self.basename: instance.name,
                 "removed from": host_obj.name})
        else:
            instance.delete()
            return self.list(request)

    def update(self, request, *args, **kwargs):
        print(74, 'ContactVS.update')
        kw = unpack_nested_kwargs(kwargs, self.basename)
        instance = Contact.objects.get(pk=kw['base_pk'])
        if 'department' in request.data and request.data['department'] is None:
            request.data.pop('department')
            instance.department = None
        if 'position' in request.data and request.data['position'] is None:
            request.data.pop('position')
            instance.position = None
        instance.save()
        # Привязка контакта:
        # PUT /project/3/contacts/2/ (контакт 2 к проекту 3)
        if self.action == 'update' and kw['host']:
            host_obj = get_object_or_404(kw['host'], kw['host_pk'])
            host_obj.contacts.add(instance)
            return Response({"success": f"{instance} added to {host_obj}"})
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        contacts = super().list(request, *args, **kwargs)
        contacts_order = request.user.contacts_order
        return Response({'contacts': contacts.data,
                         'contacts_order': contacts_order})


class ContactSearchViewSet(viewsets.ViewSet):
    permission_classes = [IsOwner]
    serializer_class = ContactSearchSerializerRequest

    @action(detail=False, methods=['post'], url_path='')
    def search(self, request, *args, **kwargs):
        """
        Принимает на вход последовательность символов и
        возвращает список контактов пользователя с похожим
        email.
        """
        email = request.data["email"]
        user_id = request.user.pkid
        relevant_contacts = Contact.objects.filter(
            owner_id=user_id).filter(
            email__contains=email).all()
        serializer = []
        for res in relevant_contacts:
            data = {"email": res.email,
                    "name": res.name}
            res_serializer = ContactSearchSerializer(data=data)
            res_serializer.is_valid()
            serializer.append(res_serializer.data)
        return Response(serializer)


class ContactsDeleteListView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactsDeleteListRequest

    def post(self, request):
        """
        Удаляет контакты съёмочной группы. Принимает массив idx контактов.
        """
        user = self.request.user
        contacts_id = request.data['contacts']
        contacts = Contact.objects.filter(owner=user, id__in=contacts_id)
        if contacts:
            for contact in contacts:
                contact.delete()
            return Response({"contacts_deleted": contacts_id})
        else:
            raise ValidationError({'error': 'Contacts not found'})
