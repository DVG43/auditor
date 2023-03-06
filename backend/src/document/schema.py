import uuid

import channels_graphql_ws
import graphene
from accounts.models import User
from django.contrib.auth import get_user_model
from django.db.models import Q, F
from django.utils import timezone
from graphene import relay
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_utils.utils_graphql import \
    PermissionClassFolder, \
    download_logo
from projects.models import Project
import datetime

from .models import Document
from .permissions import PermissionClass
from .utils import organize_data_row_sort_arrays
from settings import MEDIA_URL
from folders.models import Folder


class DocumentsType(DjangoObjectType):
    class Meta:
        model = Document
        # fields = ("name",) #если нужны опрределенные поля

    perm = graphene.String()
    perms = graphene.List(graphene.String)
    last_modified_date = graphene.Int()

    @staticmethod
    def resolve_perm(self, info):
        user = info.context.user
        doc = self
        perms = user.get_object_perm_as_str_list(doc)
        return perms[0] if len(perms) == 1 else perms

    @staticmethod
    def resolve_perms(self, info):
        return self.perms

    @staticmethod
    def resolve_last_modified_user(self, info):
        user = User.objects.filter(email=self.last_modified_user).values('first_name', 'last_name').first()
        return f"{user.get('first_name')} {user.get('last_name')}"

    @staticmethod
    def resolve_last_modified_date(self, info):
        return int(datetime.datetime.timestamp(self.last_modified_date))

    @staticmethod
    def resolve_document_logo(self, info):
        if self.document_logo:
            return f"https://{info.context.META['HTTP_HOST']}" \
                   f"{MEDIA_URL}" \
                   f"{self.document_logo}"
        else:
            return None


class UserForDocumentType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)
        interfaces = (relay.Node,)


class ProjectForDocumentType(DjangoObjectType):
    class Meta:
        model = Project

class FolderForDocumentType(DjangoObjectType):
    class Meta:
        model = Folder


class Query(graphene.ObjectType):
    document_documents = graphene.List(DocumentsType, folder_id=graphene.Int())
    document_document = graphene.Field(DocumentsType, doc_id=graphene.Int())

    @login_required
    def resolve_document_document(self, info, **kwargs):
        """"возвращает документа по id документа"""
        doc_id = kwargs.get('doc_id')
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, doc_id)
        if id is not None:
            return Document.objects.get(pk=doc_id)
        return None

    @login_required
    def resolve_document_documents(self, info, **kwargs):
        """"возвращает документа по id папки"""
        folder_id = kwargs.get('folder_id')
        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_query_object_permission(info, folder_id)
        return Document.objects.filter(Q(folder__pk=folder_id) & Q(deleted_id__isnull=True))


# Create Input Objects Type
class DocumentInput(graphene.InputObjectType):
    name = graphene.String(required=False)
    project_id = graphene.ID(required=False)
    parent = graphene.ID(required=False)
    data_row_order = graphene.List(graphene.Int, required=False)
    document_logo_url = graphene.String(required=False)
    content = graphene.String(required=False)
    folder_id = graphene.ID(required=False)


# Mutations
class CreateDocumen(graphene.Mutation):
    """создается в документах"""

    class Arguments:
        input = DocumentInput(required=True)

    ok = graphene.Boolean()
    document = graphene.Field(DocumentsType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        default_content = '{"root":{"children":[{"children":[],"direction":null,"format":"","indent":0,"type":"paragraph","version":1}],"direction":null,"format":"","indent":0,"type":"root","version":1}}'
        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_mutate_object_permission(
            info,
            input.folder_id
        )
        # if input.project_id:
        #     host_project = Project.objects.get(pk=input.project_id)
        folder = Folder.objects.filter(id=input.folder_id).first()
        document_instance = Document(
            name=input.name, doc_uuid=None,
            owner=get_user_model().objects.get(pk=info.context.user.pk),
            last_modified_user=info.context.user.email,
            host_project=Project.objects.get(pk=input.project_id) if input.project_id else None,
            content=input.content if input.content else default_content,
            folder=folder
        )
        document_instance.save()
        document_instance.refresh_from_db()

        # присвоение родителя или создание поддокумента по умолчанию для корневого документа
        if input.parent:
            document_instance.parent = Document.objects.get(pk=input.parent)
            document_instance.save()
        else:
            children_document_instance = Document.objects.create(
                name="Без названия",
                parent=document_instance,
                content=default_content,
                folder=folder,
                last_modified_user=info.context.user.email,
                owner=get_user_model().objects.get(pk=info.context.user.pk)
            )
            if hasattr(children_document_instance, "perms"):
                children_document_instance.owner.grant_object_perm(children_document_instance, 'own')

        # добавление логотипа
        if input.document_logo_url:
            document_instance.document_logo = download_logo(
                url=input.document_logo_url,
                project=folder
            )
            document_instance.save()
        if hasattr(document_instance, "perms"):
            document_instance.owner.grant_object_perm(document_instance, 'own')
        ok = True
        return CreateDocumen(ok=ok, document=document_instance)


class UpdateDocumen(graphene.Mutation):
    """"обновление документа"""

    class Arguments:
        id = graphene.ID(required=True)
        input = DocumentInput(required=True)

    ok = graphene.Boolean()
    document = graphene.Field(DocumentsType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, id)
        document_instance = Document.objects.get(pk=id)
        if document_instance:
            if input.name:
                document_instance.name = input.name
            if input.project_id:
                document_instance.host_project = Project.objects.get(pk=input.project_id)
            document_instance.last_modified_user = info.context.user.email
            if input.data_row_order:
                document_instance.data_row_order = input.data_row_order
            if input.content:
                document_instance.content = input.content
            if input.folder_id:
                folder = Folder.objects.filter(id=input.folder_id).first()
                document_instance.folder = folder
            if input.parent and (int(input.parent) != document_instance.id):
                document_instance.parent = Document.objects.get(pk=input.parent)
            if input.document_logo_url:
                document_instance.document_logo = download_logo(
                    url=input.document_logo_url,
                    project=document_instance.folder
                )
            # document_instance.save()
            organize_data_row_sort_arrays(document_instance)
            ok = True
            return UpdateDocumen(ok=ok, document=document_instance)


class DocumentOpenAccess(graphene.Mutation):
    """"открывает доступ к документу"""

    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    document = graphene.Field(DocumentsType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, id)

        document_instance = Document.objects.get(pk=id)
        if document_instance:
            document_instance.doc_uuid = str(uuid.uuid4())
            document_instance.save()
            ok = True
            return DocumentOpenAccess(ok=ok, document=document_instance)


class DocumentCloseAccess(graphene.Mutation):
    """"закрывает дотуп к документу"""

    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    document = graphene.Field(DocumentsType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, id)
        document_instance = Document.objects.get(pk=id)
        if document_instance:
            document_instance.doc_uuid = None
            document_instance.save()
            ok = True
            return DocumentCloseAccess(ok=ok, document=document_instance)


class CopyDocumen(graphene.Mutation):
    """"копирование документа"""

    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    document = graphene.Field(DocumentsType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, id)

        document_instance = Document.objects.get(pk=id)
        if document_instance:
            document_instance.pk = None
            document_instance.order_id = None
            document_instance.data_row_order = []
            document_instance.doc_uuid = None
            document_instance.name = document_instance.name + " копия"
            document_instance.save()
            if hasattr(document_instance, "perms"):
                document_instance.owner.grant_object_perm(document_instance, 'own')
            ok = True
            return CopyDocumen(ok=ok, document=document_instance)


class DeleteDocument(graphene.Mutation):
    """"удаление документа"""

    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    id = graphene.Int()

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, id)

        document_instance = Document.objects.get(pk=id)
        if document_instance:
            ok = True
            document_instance.deleted_id = uuid.uuid4()
            document_instance.deleted_since = timezone.now()
            document_instance.save()
            return DeleteDocument(ok=ok, id=id)


class Mutation(graphene.ObjectType):
    document_create_document = CreateDocumen.Field()
    document_update_document = UpdateDocumen.Field()
    document_delete_document = DeleteDocument.Field()
    document_open_access_document = DocumentOpenAccess.Field()
    document_close_access_document = DocumentCloseAccess.Field()
    document_copy_document = CopyDocumen.Field()


class OnNewChatMessage(channels_graphql_ws.Subscription):
    """Subscription triggers on a new chat message."""

    chatroom = graphene.String()
    document = graphene.Field(DocumentsType)

    class Arguments:
        """Subscription arguments."""

        chatroom = graphene.String()

    def subscribe(self, info, chatroom=None):
        """Client subscription handler."""
        del info
        # Specify the subscription group client subscribes to.
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
            and self["document"].last_modified_user == info.context.user.email
        ):
            return OnNewChatMessage.SKIP
        return OnNewChatMessage(
            chatroom=chatroom, document=self["document"]
        )

    # @classmethod
    # def new_chat_message(cls, chatroom, text, sender):
    #     cls.broadcast(
    #         group=chatroom,
    #         payload={"chatroom": chatroom, "text": text, "sender": sender},
    #     )

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
            payload={"chatroom": chatroom, 'document': instance},
        )


class Subscription(graphene.ObjectType):
    """GraphQL subscriptions."""
    subscribe_for_notifications = OnNewChatMessage.Field()


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
