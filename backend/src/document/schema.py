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
    PermissionClass as PermissionClassProject, \
    download_logo
from projects.models import Project
import datetime

from .models import Document, Element, TagForDocument
from .permissions import PermissionClass
from .utils import organize_data_row_sort_arrays
from settings import MEDIA_URL


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


class ElementForDocumentType(DjangoObjectType):
    class Meta:
        model = Element


class TagForDocumentType(DjangoObjectType):
    class Meta:
        model = TagForDocument


class UserForDocumentType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)
        interfaces = (relay.Node,)


class ProjectForDocumentType(DjangoObjectType):
    class Meta:
        model = Project


class Query(graphene.ObjectType):
    document_elements = graphene.List(ElementForDocumentType, doc_id=graphene.Int())
    document_element = graphene.Field(ElementForDocumentType, id=graphene.Int())
    document_documents = graphene.List(DocumentsType, project_id=graphene.Int())
    document_document = graphene.Field(DocumentsType, doc_id=graphene.Int())
    document_tags = graphene.List(TagForDocumentType, doc_id=graphene.Int())
    document_tag = graphene.Field(TagForDocumentType, id=graphene.Int())

    @login_required
    def resolve_document_element(self, info, **kwargs):
        """"разрешен для владельца и у кого есть uuid документа если доступ открыт"""
        id = kwargs.get('id')
        if id is not None:
            element_instance = Element.objects.get(pk=id)
            doc_id = element_instance.document_id.id
            PermissionClass.has_permission(info)
            PermissionClass.has_query_object_permission(info, doc_id)
            return element_instance
        return None

    @login_required
    def resolve_document_document(self, info, **kwargs):
        """"разрешен для владельца и у кого есть uuid документа если доступ открыт"""
        doc_id = kwargs.get('doc_id')
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, doc_id)
        if id is not None:
            return Document.objects.get(pk=doc_id)
        return None

    @login_required
    def resolve_document_tag(self, info, **kwargs):
        """"разрешен всем если доступ открыт а владельцу в любом случае"""
        id = kwargs.get('id')
        if id is not None:
            tag_instance = TagForDocument.objects.get(pk=id)
            doc_id = tag_instance.document_id.id
            PermissionClass.has_permission(info)
            PermissionClass.has_query_object_permission(info, doc_id)
            return tag_instance
        return None

    # @graphene.resolve_only_args
    @login_required
    def resolve_document_elements(self, info, **kwargs):
        """"разрешен для владельца и у кого есть uuid документа если доступ открыт"""
        doc_id = kwargs.get('doc_id')
        if doc_id is not None:
            PermissionClass.has_permission(info)
            PermissionClass.has_query_object_permission(info, doc_id)
            return Element.objects.filter(document_id__pk=doc_id)
        return None

    # @graphene.resolve_only_args
    # @login_required
    def resolve_document_documents(self, info, **kwargs):
        """"возвращает только свои докумнты"""
        project_id = kwargs.get('project_id')
        PermissionClassProject.has_permission(info)
        PermissionClassProject.has_query_object_permission(info, project_id)
        return Document.objects.filter(Q(host_project__pk=project_id) & Q(deleted_id__isnull=True))

    @login_required
    def resolve_document_tags(self, info, **kwargs):
        """"разрешен для владельца и у кого есть uuid документа если доступ открыт"""
        doc_id = kwargs.get('doc_id')
        if doc_id is not None:
            PermissionClass.has_permission(info)
            PermissionClass.has_query_object_permission(info, doc_id)
            return TagForDocument.objects.filter(document_id__pk=doc_id)
        return None


# Create Input Objects Type
class ElementForDocumentInput(graphene.InputObjectType):
    content = graphene.String(required=False)
    position = graphene.Int(required=False)


class TagForDocumentInput(graphene.InputObjectType):
    document_id = graphene.ID(required=False)
    word = graphene.String(required=False)


class DocumentInput(graphene.InputObjectType):
    name = graphene.String(required=False)
    project_id = graphene.ID(required=False)
    parent = graphene.ID(required=False)
    data_row_order = graphene.List(graphene.Int, required=False)
    document_logo_url = graphene.String(required=False)
    content = graphene.String(required=False)


# Mutations
class CreateElementForDocument(graphene.Mutation):
    """"разрешен для владельца и у кого есть uuid документа если доступ открыт"""

    class Arguments:
        doc_id = graphene.ID(required=True)
        input = ElementForDocumentInput(required=True)

    ok = graphene.Boolean()
    element = graphene.Field(ElementForDocumentType)
    data_row_order = graphene.List(graphene.Int)

    @staticmethod
    def mutate(root, info, doc_id, input=None):
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, doc_id)
        ok = False
        if input.position or input.position == 0:
            element_instance = Element(content=input.content,
                                       document_id=Document.objects.get(pk=doc_id))  # document=input.document)
            element_instance.save()
            document_instance = Document.objects.get(pk=doc_id)
            document_instance.last_modified_user = info.context.user.email
            document_instance.data_row_order.insert(input.position, element_instance.id)
            doc_new_ins = organize_data_row_sort_arrays(document_instance).data_row_order
            ok = True
            return CreateElementForDocument(ok=ok, data_row_order=doc_new_ins, element=element_instance)
        return CreateElementForDocument(ok=ok, data_row_order=None, element=None)


class UpdateElementForDocument(graphene.Mutation):
    """"разрешен для владельца и у кого есть uuid документа если доступ открыт"""

    class Arguments:
        id = graphene.Int(required=True)
        input = ElementForDocumentInput(required=True)

    ok = graphene.Boolean()
    element = graphene.Field(ElementForDocumentType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        element_instance = Element.objects.get(pk=id)

        if element_instance:
            doc_id = element_instance.document_id.id
            PermissionClass.has_permission(info)
            PermissionClass.has_query_object_permission(info, doc_id)

            doc_id = element_instance.document_id.id
            if input.content or (input.content == ""):
                element_instance.content = input.content
            ok = True
            element_instance.save()

            document_instance = Document.objects.get(pk=doc_id)
            document_instance.last_modified_user = info.context.user.email
            document_instance.save()

            return UpdateElementForDocument(ok=ok, element=element_instance)
        return UpdateElementForDocument(ok=ok, element=element_instance)


class DeleteElementForDocument(graphene.Mutation):
    """"разрешен для владельца и у кого есть uuid документа если доступ открыт"""

    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    id = graphene.Int()
    data_row_order = graphene.List(graphene.Int)

    # staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        element_instance = Element.objects.get(pk=id)

        if element_instance:
            doc_id = element_instance.document_id.id
            PermissionClass.has_permission(info)
            PermissionClass.has_query_object_permission(info, doc_id)
            element_instance.delete()

            document_instance = Document.objects.get(pk=doc_id)
            document_instance.last_modified_user = info.context.user.email
            document_instance.data_row_order.remove(id)
            organize_data_row_sort_arrays(document_instance)

            document_instance.save()
            ok = True

            return DeleteElementForDocument(ok=ok, data_row_order=document_instance.data_row_order, id=id)


class CreateTagForDocument(graphene.Mutation):
    """разрешено всем"""

    class Arguments:
        input = TagForDocumentInput(required=True)

    ok = graphene.Boolean()
    tag = graphene.Field(TagForDocumentType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, input.document_id)

        tag_instance = TagForDocument(word=input.word, document_id=Document.objects.get(
            pk=input.document_id))  # document=input.document)
        tag_instance.save()
        return CreateTagForDocument(ok=ok, tag=tag_instance)


class DeleteTagForDocument(graphene.Mutation):
    """разрешено только владельцу"""

    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        tag_instance = TagForDocument.objects.get(Q(pk=id) & Q(document_id__owner=info.context.user.pk))
        if tag_instance:
            doc_id = tag_instance.document_id.id
            PermissionClass.has_permission(info)
            PermissionClass.has_query_object_permission(info, doc_id)
            ok = True
            tag_instance.delete()
            return DeleteTagForDocument(ok=ok)


class CreateDocumen(graphene.Mutation):
    """создается в документах у пользователя который создает"""

    class Arguments:
        input = DocumentInput(required=True)

    ok = graphene.Boolean()
    document = graphene.Field(DocumentsType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        PermissionClassProject.has_permission(info)
        PermissionClassProject.has_query_object_permission(
            info,
            input.project_id
        )
        host_project = Project.objects.get(pk=input.project_id)

        document_instance = Document(
            name=input.name, doc_uuid=None,
            owner=get_user_model().objects.get(pk=info.context.user.pk),
            last_modified_user=info.context.user.email,
            host_project=host_project,
            content=input.content if input.content else '{"root":{"children":[{"children":[],"direction":null,"format":"","indent":0,"type":"paragraph","version":1}],"direction":null,"format":"","indent":0,"type":"root","version":1}}'
        )
        if input.parent:
            document_instance.parent = Document.objects.get(pk=input.parent)
        document_instance.save()
        if input.document_logo_url:
            document_instance.document_logo = download_logo(
                url=input.document_logo_url,
                project=host_project
            )
            document_instance.save()
        element_instance = Element(content="<p></p>\n", document_id=document_instance)
        element_instance.save()
        document_instance.data_row_order = [element_instance.pk]
        document_instance.save()
        if hasattr(document_instance, "perms"):
            document_instance.owner.grant_object_perm(document_instance, 'own')
        ok = True
        return CreateDocumen(ok=ok, document=document_instance)


class UpdateDocumen(graphene.Mutation):
    """"разрешен для владельца и у кого есть uuid документа если доступ открыт"""

    class Arguments:
        id = graphene.ID(required=True)
        input = DocumentInput(required=True)

    ok = graphene.Boolean()
    document = graphene.Field(DocumentsType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, id)
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
            if input.parent and (int(input.parent) != document_instance.id):
                document_instance.parent = Document.objects.get(pk=input.parent)
            if input.document_logo_url:
                document_instance.document_logo = download_logo(
                    url=input.document_logo_url,
                    project=document_instance.host_project
                )
            # document_instance.save()
            organize_data_row_sort_arrays(document_instance)
            ok = True
            return UpdateDocumen(ok=ok, document=document_instance)


class DocumentOpenAccess(graphene.Mutation):
    """"разрешен только для владельца"""

    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    document = graphene.Field(DocumentsType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, id)

        document_instance = Document.objects.get(pk=id)
        if document_instance:
            document_instance.doc_uuid = str(uuid.uuid4())
            document_instance.save()
            ok = True
            return DocumentOpenAccess(ok=ok, document=document_instance)


class DocumentCloseAccess(graphene.Mutation):
    """"разрешен только для владельца"""

    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    document = graphene.Field(DocumentsType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, id)
        document_instance = Document.objects.get(pk=id)
        if document_instance:
            document_instance.doc_uuid = None
            document_instance.save()
            ok = True
            return DocumentCloseAccess(ok=ok, document=document_instance)


class CopyDocumen(graphene.Mutation):
    """"разрешен для владельца и у кого есть uuid документа если доступ открыт"""

    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    document = graphene.Field(DocumentsType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, id)

        document_instance = Document.objects.get(pk=id)
        tuple_data_row_order = tuple(document_instance.data_row_order)
        if document_instance:
            document_instance.pk = None
            document_instance.order_id = None
            document_instance.data_row_order = []
            document_instance.doc_uuid = None
            document_instance.name = document_instance.name + " копия"
            document_instance.save()
            element_instances = Element.objects.filter(document_id__pk=id)  # .order_by("document_id__data_row_order")
            # element_instances = Element.objects.filter(pk__in=new_data_row_order)
            new_order_elem = list(tuple_data_row_order)
            if element_instances:
                for element in element_instances:
                    old_pk = element.pk
                    element.pk = None
                    element.document_id = document_instance
                    element.save()
                    new_order_elem[tuple_data_row_order.index(old_pk)] = element.pk
            tag_instances = TagForDocument.objects.filter(document_id__pk=id)
            if tag_instances:
                for tag in tag_instances:
                    tag.pk = None
                    tag.document_id = document_instance
                    tag.save()
            document_instance.data_row_order = new_order_elem
            # document_instance.save()
            organize_data_row_sort_arrays(document_instance)
            if hasattr(document_instance, "perms"):
                document_instance.owner.grant_object_perm(document_instance, 'own')
            ok = True
            return CopyDocumen(ok=ok, document=document_instance)


class DeleteDocument(graphene.Mutation):
    """"разрешен только владельце"""

    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    id = graphene.Int()

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        PermissionClass.has_query_object_permission(info, id)

        document_instance = Document.objects.get(pk=id)
        if document_instance:
            ok = True
            document_instance.deleted_id = uuid.uuid4()
            document_instance.deleted_since = timezone.now()
            document_instance.save()
            return DeleteDocument(ok=ok, id=id)


class Mutation(graphene.ObjectType):
    document_create_element = CreateElementForDocument.Field()
    document_update_element = UpdateElementForDocument.Field()
    document_delete_element = DeleteElementForDocument.Field()
    document_create_tag = CreateTagForDocument.Field()
    document_delete_tag = DeleteTagForDocument.Field()
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
