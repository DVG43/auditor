import datetime
import uuid
import graphene
from django.db.models import Q
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required
from graphene_django.types import ObjectType, DjangoObjectType

from accounts.models import User
from common.models import UserColumn, UserChoice
from common.utils import change_disk_space, recount_disk_space, duplicate_object
from document.models import Document
from . import serializers
from graphql_utils.utils_graphql import PermissionClass, check_disk_space, download_logo
from folders.models import Folder
from table.models import DefaultTableModel, DefaultTableFrame, DefaultTableUsercell
from .utils import create_default_table_frame_columns


class UserColumnType(DjangoObjectType):
    class Meta:
        model = UserColumn


class ColumnChoiceType(DjangoObjectType):
    class Meta:
        model = UserChoice


class UserCellType(DjangoObjectType):
    choices_id = ColumnChoiceType
    choice_id = ColumnChoiceType

    class Meta:
        model = DefaultTableUsercell

    def resolve_choices_id(self, info):
        return self.choices_id

    def resolve_choice_id(self, info):
        return self.choice_id


class FramesType(DjangoObjectType):
    userfields = UserCellType

    class Meta:
        model = DefaultTableFrame

    def resolve_userfields(self, info):
        return self.userfields


class DefaultTableType(DjangoObjectType):
    perm = graphene.String()
    perms = graphene.List(graphene.String)
    frame_columns = UserColumnType
    frames = DefaultTableFrame

    class Meta:
        model = DefaultTableModel

    def resolve_frame_columns(self, info):
        return self.frame_columns

    def resolve_frames(self, info):
        return DefaultTableFrame.objects.filter(host_default_table=self.id).all()

    @staticmethod
    def resolve_perm(self, info):
        user = info.context.user
        if self.host_folder:
            project = self.host_folder
        else:
            project = self.host_document.folder
        perms = user.get_object_perm_as_str_list(project)
        return perms[0] if len(perms) == 1 else perms

    @staticmethod
    def resolve_perms(self, info):
        return self.perms


class Query(ObjectType):
    all_tables = graphene.List(DefaultTableType, host_document=graphene.ID(), host_folder=graphene.ID())
    table_by_pk = graphene.Field(DefaultTableType, table_pk=graphene.ID())
    all_frames = graphene.List(FramesType, host_default_table=graphene.ID())
    frame_by_pk = graphene.Field(FramesType, frame_pk=graphene.ID())

    @login_required
    def resolve_all_tables(self, info, host_folder=None, host_document=None):
        PermissionClass.has_permission(info)
        if host_folder:
             PermissionClass.has_query_object_permission(info, host_folder)
        else:
             project_id = Document.objects.filter(pk=host_document).first().folder.id
             PermissionClass.has_query_object_permission(info, project_id)

        return DefaultTableModel.objects.filter(
            host_folder=host_folder).all()

    @login_required
    def resolve_table_by_pk(self, info, table_pk=None):
        table = DefaultTableModel.objects.filter(pk=table_pk).first()
        PermissionClass.has_permission(info)
        if table.host_folder:
            PermissionClass.has_query_object_permission(info, table.host_folder.id)
        else:
            host_project_id = Document.objects.filter(
                pk=table.host_document).first().folder.id
            PermissionClass.has_query_object_permission(info, host_project_id)

        return DefaultTableModel.objects.filter(pk=table_pk).first()

    @login_required
    def resolve_all_frames(self, info, host_default_table=None):
        table = DefaultTableModel.objects.filter(pk=host_default_table).first()
        PermissionClass.has_permission(info)
        if table.host_folder:
            PermissionClass.has_query_object_permission(info, table.host_folder.id)
        else:
            host_project_id = Document.filter(
                pk=table.table.host_document).first().folder.id
            PermissionClass.has_query_object_permission(info, host_project_id)
        return DefaultTableFrame.objects.filter(host_default_table=host_default_table).all()

    @login_required
    def resolve_frame_by_pk(self, info, frame_pk=None):
        table = DefaultTableFrame.objects.filter(pk=frame_pk).first().host_default_table
        PermissionClass.has_permission(info)
        if table.host_folder:
            PermissionClass.has_query_object_permission(info, table.host_folder.id)
        else:
            host_project_id = Document.filter(
                pk=table.table.host_document).first().folder.id
            PermissionClass.has_query_object_permission(info, host_project_id)
        return DefaultTableFrame.objects.filter(pk=frame_pk).first()


class CreateDefaultTable(SerializerMutation):
    class Meta:
        serializer_class = serializers.DefaultTableSerializer
        model_operations = ['create', 'update']
        model_class = DefaultTableModel

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        if "host_folder" in input:
            folder_id = input["host_folder"]
        else:
            folder_id = Document.objects.filter(host_project=input["host_document"]).first().folder.id

        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, folder_id)

        host_folder = Folder.objects.filter(pk=folder_id).first()

        input.update({'owner': info.context.user.pkid,
                      'last_modified_user': info.context.user.email})

        url = None

        if "document_logo_url" in input:
            url = input['document_logo_url']
            del input['document_logo_url']

        if info.context.FILES:
            disk_space = check_disk_space(project=host_folder,
                                          info=info)

        response = super().mutate_and_get_payload(root, info, **input)

        logo_input = {}
        if url:
            logo_input['document_logo'] = download_logo(url=url,
                                                        project=host_folder)
            logo_input['id'] = response.__dict__['id']
            response = super().mutate_and_get_payload(root, info, **logo_input)

        # обновляем место на диске после сохранения нового файла
        if info.context.FILES:
            change_disk_space(host_folder.owner, disk_space)

        table = DefaultTableModel.objects.get(pk=response.__dict__['id'])
        create_default_table_frame_columns(table, info.context.user)

        return response


class UpdateDefaultTable(SerializerMutation):

    class Meta:
        serializer_class = serializers.DefaultTableSerializer
        model_operations = ['update']
        model_class = DefaultTableModel
        lookup_field = 'id'

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        table_instance = DefaultTableModel.objects.filter(id=input["id"]).first()
        if table_instance.host_document:
            folder_id = table_instance.host_document.folder.id
        else:
            folder_id = table_instance.host_folder.id
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, folder_id)
        input.update({'last_modified_user': info.context.user.email})

        host_folder = Folder.objects.filter(pk=folder_id).first()

        if 'document_logo_url' in input:
            input['document_logo'] = download_logo(url=input['document_logo_url'],
                                                   project=host_folder)

        if info.context.FILES:
            check_disk_space(project=host_folder,
                             info=info)

        response = super().mutate_and_get_payload(root, info, **input)

        # обновляем место на диске после обновления файла
        if info.context.FILES or 'document_logo_url' in input:
            recount_disk_space(host_folder.owner)

        return response


class DeleteDefaultTable(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        table_instance = DefaultTableModel.objects.filter(pk=id).first()
        if table_instance:
            ok = True
            if table_instance.host_document:
                folder_id = table_instance.host_document.folder.id
            else:
                folder_id = table_instance.host_folder.id
            PermissionClass.has_mutate_object_permission(info, folder_id)
            table_instance.deleted_id = uuid.uuid4()
            table_instance.deleted_since = datetime.datetime.now()
            table_instance.last_modified_user = info.context.user.email
            table_instance.save()
        return DeleteDefaultTable(ok=ok)


class CreateTableColumn(SerializerMutation):
    class Meta:
        serializer_class = serializers.UserColumnSerializer
        model_operations = ['create']
        model_class = UserColumn
        lookup_field = 'id'

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        table_instance = DefaultTableModel.objects.filter(id=input["host_table"]).first()
        if table_instance.host_document:
            folder_id = table_instance.host_document.folder.id
        else:
            folder_id = table_instance.host_folder.id

        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, folder_id)

        host_folder = Folder.objects.filter(pk=folder_id).first()

        input.update({'owner': info.context.user.pkid,
                      'last_modified_user': info.context.user.email})

        url = None

        if "document_logo_url" in input:
            url = input['document_logo_url']
            del input['document_logo_url']

        if info.context.FILES:
            disk_space = check_disk_space(project=host_folder,
                                          info=info)
        host = input["host_table"]
        del input["host_table"]
        response = super().mutate_and_get_payload(root, info, **input)

        logo_input = {}
        if url:
            logo_input['document_logo'] = download_logo(url=url,
                                                        project=host_folder)
            logo_input['id'] = response.__dict__['id']
            response = super().mutate_and_get_payload(root, info, **logo_input)

        # обновляем место на диске после сохранения нового файла
        if info.context.FILES:
            change_disk_space(host_folder.owner, disk_space)

        obj = DefaultTableModel.objects.filter(pk=int(host)).first()
        obj.frame_columns.add(response.column_id)
        obj.save()

        frames_attr = None
        for attr in obj.__dir__():
            if attr.endswith('frames'):
                frames_attr = getattr(obj, attr)
                break
        if frames_attr:
            frame_count = frames_attr.count()
            if frame_count > 0:
                for frame_obj in frames_attr.all():
                    cls_name = frame_obj.__class__.__name__
                    if cls_name == 'DefaultTableFrame':
                        usercell = DefaultTableUsercell.objects.create(
                            host_usercolumn=UserColumn.objects.filter(pk=response.column_id).first(),
                            owner=info.context.user)
                        frame_obj.userfields.add(usercell)

        return response


class UpdateTableColumn(SerializerMutation):
    class Meta:
        serializer_class = serializers.UserColumnSerializer
        model_operations = ['update']
        model_class = UserColumn
        lookup_field = 'id'

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        table_instance = DefaultTableModel.objects.filter(id=input["host_table"]).first()
        if table_instance.host_document:
            folder_id = table_instance.host_document.folder.id
        else:
            folder_id = table_instance.host_folder.id

        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, folder_id)
        input.update({'last_modified_user': info.context.user.email})

        host_folder = Folder.objects.filter(pk=folder_id).first()

        if 'document_logo_url' in input:
            input['document_logo'] = download_logo(url=input['document_logo_url'],
                                                   project=host_folder)

        if info.context.FILES:
            check_disk_space(project=host_folder,
                             info=info)

        input["id"] = input["column_id"]

        response = super().mutate_and_get_payload(root, info, **input)

        # обновляем место на диске после обновления файла
        if info.context.FILES or 'document_logo_url' in input:
            recount_disk_space(host_folder.owner)

        return response


class DeleteTableColumn(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        column_instance = UserColumn.objects.filter(pk=id).first()
        if column_instance:
            ok = True
            if column_instance.column_type == "image":
                column_instance.delete()
                recount_disk_space(info.context.user)
            else:
                column_instance.delete()
        return DeleteTableColumn(ok=ok)


class CreateUpdateFrame(SerializerMutation):
    class Meta:
        serializer_class = serializers.DefaultTableFrameSerializer
        model_operations = ['create', 'update']
        model_class = DefaultTableFrame
        lookup_field = 'id'

    def mutate_and_get_payload(cls, root, info, **input):
        table_instance = DefaultTableModel.objects.filter(id=input["host_default_table"]).first()
        if table_instance.host_document:
            folder_id = table_instance.host_document.folder.id
        else:
            folder_id = table_instance.host_folder.id

        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, folder_id)
        input.update({'owner': info.context.user.pkid,
                      'last_modified_user': info.context.user.email})
        return super().mutate_and_get_payload(root, info, **input)


class DeleteFrame(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        frame_instance = DefaultTableFrame.objects.filter(pk=id).first()
        if frame_instance:
            ok = True
            frame_instance.delete()
        return DeleteFrame(ok=ok)


class CreateUpdateColumnChoice(SerializerMutation):
    class Meta:
        serializer_class = serializers.UserChoiceSerializer
        model_operations = ['create', 'update']
        model_class = UserChoice
        lookup_field = 'id'

    def mutate_and_get_payload(cls, root, info, **input):
        table_instance = UserColumn.objects.filter(id=input["host_usercolumn"]).first().host_table
        if table_instance.host_document:
            folder_id = table_instance.host_document.folder.id
        else:
            folder_id = table_instance.host_folder.id

        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, folder_id)
        input.update({'owner': info.context.user.pkid,
                      'last_modified_user': info.context.user.email})
        return super().mutate_and_get_payload(root, info, **input)


class DeleteColumnChoice(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        choice_instance = UserChoice.objects.filter(pk=id).first()
        if choice_instance:
            ok = True
            if choice_instance.host_usercolumn.column_type == "image":
                choice_instance.delete()
                recount_disk_space(info.context.user)
            else:
                choice_instance.delete()
        return DeleteTableColumn(ok=ok)


class UpdateUserCell(SerializerMutation):
    class Meta:
        serializer_class = serializers.UserCellSerializer
        model_operations = ['update']
        model_class = DefaultTableUsercell
        lookup_field = 'cell_id'

    def mutate_and_get_payload(cls, root, info, **input):
        table_instance = UserColumn.objects.filter(id=input["host_usercolumn"]).first().host_table
        if table_instance.host_document:
            folder_id = table_instance.host_document.folder.id
        else:
            folder_id = table_instance.host_folder.id

        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, folder_id)
        input.update({'owner': info.context.user.pkid,
                      'last_modified_user': info.context.user.email})
        return super().mutate_and_get_payload(root, info, **input)


class DeleteUserCell(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        cell_instance = DefaultTableUsercell.objects.filter(cell_id=id).first()
        if cell_instance:
            ok = True
            if cell_instance.host_usercolumn.column_type == "image":
                cell_instance.delete()
                recount_disk_space(info.context.user)
            else:
                cell_instance.delete()
        return DeleteUserCell(ok=ok)


class CopyTable(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        PermissionClass.has_permission(info)
        ok = False
        table_instance = DefaultTableModel.objects.filter(pk=id).first()
        if table_instance:
            ok = True
            PermissionClass.has_mutate_object_permission(info, table_instance.host_folder.id)
            duplicate_object(table_instance, project_id=table_instance.host_folder.id)
        return CopyTable(ok=ok)


class TableOpenAccess(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    doc_uuid = graphene.UUID()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        PermissionClass.has_permission(info)
        ok = False
        timing_instance = DefaultTableModel.objects.get(
            Q(pk=id) & Q(owner=info.context.user.pk))
        if timing_instance:
            timing_instance.doc_uuid = str(uuid.uuid4())
            timing_instance.save()
            ok = True
            return TableOpenAccess(ok=ok, doc_uuid=timing_instance.doc_uuid)
        return TableOpenAccess(ok=ok)


class TableCloseAccess(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        PermissionClass.has_permission(info)
        ok = False
        timing_instance = DefaultTableModel.objects.get(
            Q(pk=id) & Q(owner=info.context.user.pk))
        if timing_instance:
            ok = True
            doc_uuid = timing_instance.doc_uuid
            timing_instance.doc_uuid = None
            timing_instance.save()
            user = User.objects.filter(document=doc_uuid).first()
            if user:
                user.delete()
        return TableCloseAccess(ok=ok)


class MoveTable(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        folder_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, folder_id, input=None):
        PermissionClass.has_permission(info)
        ok = False
        table_instance = DefaultTableModel.objects.filter(id=id).first()
        new_host_folder = Folder.objects.filter(id=folder_id).first()
        if table_instance:
            ok = True
            PermissionClass.has_mutate_object_permission(info, table_instance.host_folder.id)
            PermissionClass.has_mutate_object_permission(info, folder_id)
            table_instance.host_folder = new_host_folder
            table_instance.save()
        return MoveTable(ok=ok)


class Mutation(graphene.ObjectType):
    create_default_table = CreateDefaultTable.Field()
    update_default_table = UpdateDefaultTable.Field()
    delete_default_table = DeleteDefaultTable.Field()
    create_table_column = CreateTableColumn.Field()
    update_table_column = UpdateTableColumn.Field()
    delete_table_column = DeleteTableColumn.Field()
    create_or_update_column_choice = CreateUpdateColumnChoice.Field()
    delete_column_choice = DeleteColumnChoice.Field()
    create_or_update_frame = CreateUpdateFrame.Field()
    delete_frame = DeleteFrame.Field()
    create_or_update_usercell = UpdateUserCell.Field()
    delete_user_cell = DeleteUserCell.Field()
    move_table = MoveTable.Field()
    open_table_access = TableOpenAccess.Field()
    close_table_access = TableCloseAccess.Field()
    copy_table = CopyTable.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
