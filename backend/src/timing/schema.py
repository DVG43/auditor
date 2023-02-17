import datetime
import uuid

import channels_graphql_ws
import graphene
from django.db.models import Prefetch, Q
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required

from accounts.models import User
from common.utils import duplicate_object, change_disk_space, recount_disk_space
from projects.models import Project
from timing import models
from graphene_django.types import DjangoObjectType, ObjectType
from timing.serializers import (TimingSerializer,
                                EventSerializer,
                                GroupSerializer,
                                TimingUpdateSerializer)
from graphql_utils.utils_graphql import PermissionClass, download_logo, check_disk_space


class TimingType(DjangoObjectType):
    perm = graphene.String()
    perms = graphene.List(graphene.String)

    class Meta:
        model = models.Timing

    @staticmethod
    def resolve_perm(self, info):
        user = info.context.user
        project = self.host_project
        perms = user.get_object_perm_as_str_list(project)
        return perms[0] if len(perms) == 1 else perms

    @staticmethod
    def resolve_perms(self, info):
        return self.perms


class GroupType(DjangoObjectType):
    class Meta:
        model = models.TimingGroup


class EventType(DjangoObjectType):
    class Meta:
        model = models.Event


class Query(ObjectType):
    all_timing = graphene.List(TimingType, days=graphene.Int(), prj_id=graphene.Int())
    timing_by_pk = graphene.Field(TimingType, days=graphene.Int(), timing_pk=graphene.Int())
    group_by_pk = graphene.Field(GroupType, group_pk=graphene.Int())
    event_by_pk = graphene.Field(EventType, event_pk=graphene.Int())

    @login_required
    def resolve_all_timing(self, info, prj_id=None, days=None):
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, prj_id)

        if days:
            return models.Timing.objects.filter(
                host_project__pk=prj_id).prefetch_related(
                Prefetch('timing_group',
                         queryset=models.TimingGroup.objects.prefetch_related(
                             Prefetch('timing_event',
                                      queryset=models.Event.objects.filter(
                                          start_datetime__range=[
                                              datetime.datetime.now(),
                                              datetime.timedelta(days=days) + datetime.datetime.now()
                                          ]))))).all()

        return models.Timing.objects.filter(
            host_project__pk=prj_id).prefetch_related(
            Prefetch('timing_group',
                     queryset=models.TimingGroup.objects.prefetch_related(
                         'timing_event'))).all()

    @login_required
    def resolve_timing_by_pk(self, info, timing_pk=None, days=None):
        prj_id = models.Timing.objects.filter(pk=timing_pk).first().host_project.id
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, prj_id)
        if days:
            return models.Timing.objects.filter(
                host_project__pk=prj_id).filter(id=timing_pk).prefetch_related(
                Prefetch('timing_group',
                         queryset=models.TimingGroup.objects.prefetch_related(
                             Prefetch('timing_event',
                                      queryset=models.Event.objects.filter(
                                          start_datetime__range=[
                                              datetime.datetime.now(),
                                              datetime.timedelta(days=days) + datetime.datetime.now()
                                          ]))))).first()

        return models.Timing.objects.filter(
            host_project__pk=prj_id).filter(id=timing_pk).prefetch_related(
            Prefetch('timing_group',
                     queryset=models.TimingGroup.objects.prefetch_related(
                         Prefetch('timing_event')))).first()

    @login_required
    def resolve_group_by_pk(self, info, group_pk=None):
        prj_id = models.TimingGroup.objects.filter(pk=group_pk).first().host_timing.host_project.id
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, prj_id)
        return models.TimingGroup.objects.filter(pk=group_pk).prefetch_related(
            'timing_event').first()

    @login_required
    def resolve_event_by_pk(self, info, event_pk=None):
        prj_id = models.Event.objects.filter(
            id=event_pk).first().host_group.host_timing.host_project.id
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, prj_id)
        return models.Event.objects.filter(id=event_pk).first()


class CreateTiming(SerializerMutation):
    class Meta:
        serializer_class = TimingSerializer
        model_operations = ['create', 'update']
        model_class = models.Timing

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        prj_id = input["host_project"]
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, prj_id)

        host_project = Project.objects.filter(pk=prj_id).first()

        input.update({'owner': info.context.user.pkid,
                      'last_modified_user': info.context.user.email})

        url = None

        if "document_logo_url" in input:
            url = input['document_logo_url']
            del input['document_logo_url']

        if info.context.FILES:
            disk_space = check_disk_space(project=host_project,
                                          info=info)

        response = super().mutate_and_get_payload(root, info, **input)

        logo_input = {}
        if url:
            logo_input['document_logo'] = download_logo(url=url,
                                                        project=host_project)
            logo_input['id'] = response.__dict__['id']
            response = super().mutate_and_get_payload(root, info, **logo_input)

        # обновляем место на диске после сохранения нового файла
        if info.context.FILES:
            change_disk_space(host_project.owner, disk_space)

        return response


class UpdateTiming(SerializerMutation):
    class Meta:
        serializer_class = TimingUpdateSerializer
        model_operations = ['update']
        model_class = models.Timing
        lookup_field = 'id'

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        prj_id = input["host_project"]
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, prj_id)
        input.update({'last_modified_user': info.context.user.email})

        host_project = Project.objects.filter(pk=prj_id).first()

        if 'document_logo_url' in input:
            input['document_logo'] = download_logo(url=input['document_logo_url'],
                                                   project=host_project)

        if info.context.FILES:
            check_disk_space(project=host_project,
                             info=info)

        response = super().mutate_and_get_payload(root, info, **input)

        # обновляем место на диске после обновления файла
        if info.context.FILES or 'document_logo_url' in input:
            recount_disk_space(host_project.owner)

        return response


class CreateEvent(SerializerMutation):
    class Meta:
        serializer_class = EventSerializer
        model_operations = ['create']
        model_class = models.Event

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        group_instance = models.TimingGroup.objects.filter(
            id=input["host_group"]).first()
        user = group_instance.owner
        PermissionClass.has_permission(info)
        if user and group_instance:
            PermissionClass.has_mutate_object_permission(info,
                                                         group_instance.host_timing.host_project.id)
            input.update({'owner': user.pkid})
            group_instance.host_timing.last_modified_user = info.context.user.email
            group_instance.host_timing.save()
            return super().mutate_and_get_payload(root, info, **input)


class UpdateEvent(SerializerMutation):
    class Meta:
        serializer_class = EventSerializer
        model_operations = ['update']
        model_class = models.Event
        lookup_field = 'id'

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        event_instance = models.Event.objects.filter(
            id=input["id"]).first()
        PermissionClass.has_permission(info)
        if event_instance:
            PermissionClass.has_mutate_object_permission(info,
                                                         event_instance.host_group.host_timing.host_project.id)
            event_instance.host_group.host_timing.last_modified_user = info.context.user.email
            event_instance.host_group.host_timing.save()
            return super().mutate_and_get_payload(root, info, **input)


class CreateGroup(SerializerMutation):
    class Meta:
        serializer_class = GroupSerializer
        model_operations = ['create']
        model_class = models.TimingGroup

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        timing = models.Timing.objects.filter(pk=input["host_timing"]).first()
        PermissionClass.has_permission(info)
        user = timing.owner
        if user and timing:
            PermissionClass.has_mutate_object_permission(info, timing.host_project.id)
            input.update({'owner': user.pkid})
            timing.last_modified_user = info.context.user.email
            timing.save()
            return super().mutate_and_get_payload(root, info, **input)


class UpdateGroup(SerializerMutation):
    class Meta:
        serializer_class = GroupSerializer
        model_operations = ['update']
        model_class = models.TimingGroup
        lookup_field = 'id'

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        group_instance = models.TimingGroup.objects.filter(
            id=input["id"]).first()
        PermissionClass.has_permission(info)
        if group_instance:
            PermissionClass.has_mutate_object_permission(info,
                                                         group_instance.host_timing.host_project.id)
            group_instance.host_timing.last_modified_user = info.context.user.email
            group_instance.host_timing.save()
            return super().mutate_and_get_payload(root, info, **input)


class DeleteTiming(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        timing_instance = models.Timing.objects.filter(pk=id).first()
        if timing_instance:
            ok = True
            PermissionClass.has_mutate_object_permission(info, timing_instance.host_project.id)
            timing_instance.deleted_id = uuid.uuid4()
            timing_instance.deleted_since = datetime.datetime.now()
            timing_instance.last_modified_user = info.context.user.email
            timing_instance.save()
        return DeleteTiming(ok=ok)


class DeleteEvent(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        event_instance = models.Event.objects.filter(pk=id).first()
        if event_instance:
            ok = True
            prj_id = event_instance.host_group.host_timing.host_project.id
            PermissionClass.has_mutate_object_permission(info, prj_id)
            event_instance.delete()
            event_instance.host_group.host_timing.last_modified_user = info.context.user.email
            event_instance.host_group.host_timing.save()
        return DeleteEvent(ok=ok)


class DeleteGroup(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        group_instance = models.TimingGroup.objects.filter(pk=id).first()
        if group_instance:
            ok = True
            prj_id = group_instance.host_timing.host_project.id
            PermissionClass.has_mutate_object_permission(info, prj_id)
            group_instance.delete()
            group_instance.host_timing.last_modified_user = info.context.user.email
            group_instance.host_timing.save()
        return DeleteGroup(ok=ok)


class CopyTiming(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        PermissionClass.has_permission(info)
        ok = False
        timing_instance = models.Timing.objects.filter(pk=id).first()
        if timing_instance:
            ok = True
            PermissionClass.has_mutate_object_permission(info, timing_instance.host_project.id)
            duplicate_object(timing_instance, project_id=timing_instance.host_project.id)
        return CopyTiming(ok=ok)


class TimingOpenAccess(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    doc_uuid = graphene.UUID()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        PermissionClass.has_permission(info)
        ok = False
        timing_instance = models.Timing.objects.get(
            Q(pk=id) & Q(owner=info.context.user.pk))
        if timing_instance:
            timing_instance.doc_uuid = str(uuid.uuid4())
            timing_instance.save()
            ok = True
            return TimingOpenAccess(ok=ok, doc_uuid=timing_instance.doc_uuid)
        return TimingOpenAccess(ok=ok)


class TimingCloseAccess(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        PermissionClass.has_permission(info)
        ok = False
        timing_instance = models.Timing.objects.get(
            Q(pk=id) & Q(owner=info.context.user.pk))
        if timing_instance:
            ok = True
            doc_uuid = timing_instance.doc_uuid
            timing_instance.doc_uuid = None
            timing_instance.save()
            user = User.objects.filter(document=doc_uuid).first()
            if user:
                user.delete()
        return TimingCloseAccess(ok=ok)


class MoveTiming(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        project_id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, project_id, input=None):
        PermissionClass.has_permission(info)
        ok = False
        timing_instance = models.Timing.objects.filter(id=id).first()
        new_host_prj = Project.objects.filter(id=project_id).first()
        if timing_instance:
            ok = True
            PermissionClass.has_mutate_object_permission(info, timing_instance.host_project.id)
            PermissionClass.has_mutate_object_permission(info, project_id)
            timing_instance.host_project = new_host_prj
            timing_instance.save()
        return MoveTiming(ok=ok)


class Mutation(graphene.ObjectType):
    create_timing = CreateTiming.Field()
    update_timing = UpdateTiming.Field()
    delete_timing = DeleteTiming.Field()
    create_group = CreateGroup.Field()
    update_group = UpdateGroup.Field()
    delete_group = DeleteGroup.Field()
    create_event = CreateEvent.Field()
    update_event = UpdateEvent.Field()
    delete_event = DeleteEvent.Field()
    timing_open_access_timing = TimingOpenAccess.Field()
    timing_close_access_timing = TimingCloseAccess.Field()
    timing_copy_timing = CopyTiming.Field()
    timing_move_timing = MoveTiming.Field()


class TimingOnNewChatMessage(channels_graphql_ws.Subscription):
    """Subscription triggers on a new chat message."""

    chatroom = graphene.String()
    timing = graphene.Field(TimingType)

    class Arguments:
        """Subscription arguments."""

        chatroom = graphene.String()

    def subscribe(self, info, chatroom=None):
        """Client subscription handler."""
        del info
        # Specify the subscription group client subscribes to.
        print(f"subscribed to chatroom {chatroom}")
        return [chatroom] if chatroom is not None else None

    def publish(self, info, chatroom=None):
        """Called to prepare the subscription notification message."""

        # The `self` contains payload delivered from the `broadcast()`.
        new_msg_chatroom = self["chatroom"]

        # Method is called only for events on which client explicitly
        # subscribed, by returning proper subscription groups from the
        # `subscribe` method. So he either subscribed for all events or
        # to particular chatroom.
        assert chatroom is None or chatroom == new_msg_chatroom

        # Avoid self-notifications.
        if (
            info.context.user.is_authenticated
            and self["timing"].last_modified_user == info.context.user.email
        ):
            return TimingOnNewChatMessage.SKIP
        return TimingOnNewChatMessage(
            chatroom=chatroom, timing=self["timing"]
        )

    @classmethod
    def message_about_changing(cls, chatroom, instance):
        """Auxiliary function to send subscription notifications.
        It is generally a good idea to encapsulate broadcast invocation
        inside auxiliary class methods inside the subscription class.
        That allows to consider a structure of the `payload` as an
        implementation details.
        """
        cls.broadcast(
            group=chatroom,
            payload={"chatroom": chatroom, 'timing': instance},
        )
        print({"chatroom": chatroom, 'timing': instance})


class Subscription(graphene.ObjectType):
    """GraphQL subscriptions."""
    timing_subscribe_for_notifications = TimingOnNewChatMessage.Field()


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
