import datetime
import uuid
import graphene
from django.db.models import Q
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required
from graphene_django.types import ObjectType, DjangoObjectType
from graphene_file_upload.scalars import Upload

from accounts.models import User
from common.models import UserColumn, UserChoice
from common.utils import change_disk_space, recount_disk_space, duplicate_object
from document.models import Document
from . import serializers
from graphql_utils.utils_graphql import PermissionClassFolder, check_disk_space, download_logo
from folders.models import Folder
from table.models import DefaultTableModel, DefaultTableFrame, DefaultTableUsercell, UsercellFile
from .utils import create_default_table_frame_columns, add_userfields, organize_data_row_sort_arrays


class UserColumnType(DjangoObjectType):
    class Meta:
        model = UserColumn


class ColumnChoiceType(DjangoObjectType):
    class Meta:
        model = UserChoice


class UsercellFileType(DjangoObjectType):
    class Meta:
        model = UsercellFile


class UserCellType(DjangoObjectType):
    choices_id = ColumnChoiceType
    choice_id = ColumnChoiceType
    usercellfile = UsercellFileType

    class Meta:
        model = DefaultTableUsercell

    def resolve_choices_id(self, info):
        return self.choices_id

    def resolve_choice_id(self, info):
        return self.choice_id

    def resolve_usercellfile(self, info):
        return UsercellFile.objects.filter(host_usercell=self.id).first()


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
        if self.folder:
            project = self.folder
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
        PermissionClassFolder.has_permission(info)
        if host_folder:
             PermissionClassFolder.has_query_object_permission(info, host_folder)
        else:
             project_id = Document.objects.filter(pk=host_document).first().folder.id
             PermissionClassFolder.has_query_object_permission(info, project_id)

        return DefaultTableModel.objects.filter(
            folder=host_folder).all()

    @login_required
    def resolve_table_by_pk(self, info, table_pk=None):
        table = DefaultTableModel.objects.filter(pk=table_pk).first()
        PermissionClassFolder.has_permission(info)
        if table:
            if table.folder:
                PermissionClassFolder.has_query_object_permission(info, table.folder.id)
            else:
                host_project_id = Document.objects.filter(
                    pk=table.host_document.id).first().folder.id
                PermissionClassFolder.has_query_object_permission(info, host_project_id)
            instance = DefaultTableModel.objects.filter(pk=table_pk).first()
            organize_data_row_sort_arrays(instance)
            return instance

    @login_required
    def resolve_all_frames(self, info, host_default_table=None):
        table = DefaultTableModel.objects.filter(pk=host_default_table).first()
        PermissionClassFolder.has_permission(info)
        if table:
            if table.folder:
                PermissionClassFolder.has_query_object_permission(info, table.folder.id)
            else:
                host_project_id = Document.filter(
                    pk=table.table.host_document.id).first().folder.id
                PermissionClassFolder.has_query_object_permission(info, host_project_id)
            return DefaultTableFrame.objects.filter(host_default_table=host_default_table).all()

    @login_required
    def resolve_frame_by_pk(self, info, frame_pk=None):
        table = DefaultTableFrame.objects.filter(pk=frame_pk).first().host_default_table
        PermissionClassFolder.has_permission(info)
        if table:
            if table.folder:
                PermissionClassFolder.has_query_object_permission(info, table.folder.id)
            else:
                host_project_id = Document.filter(
                    pk=table.table.host_document.id).first().folder.id
                PermissionClassFolder.has_query_object_permission(info, host_project_id)
            instance = DefaultTableFrame.objects.filter(pk=frame_pk).first()
            organize_data_row_sort_arrays(instance)
            return instance


class CreateDefaultTable(SerializerMutation):
    class Meta:
        serializer_class = serializers.DefaultTableSerializer
        model_operations = ['create', 'update']
        model_class = DefaultTableModel

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        if "folder" in input:
            folder_id = input["folder"]
        else:
            folder_id = Document.objects.filter(pk=input["host_document"]).first().folder.id

        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_mutate_object_permission(info, folder_id)

        input.update({'owner': info.context.user.pkid,
                      'last_modified_user': info.context.user.email})

        response = super().mutate_and_get_payload(root, info, **input)

        table = DefaultTableModel.objects.get(pk=response.__dict__['id'])
        create_default_table_frame_columns(table, info.context)

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
            folder_id = table_instance.folder.id
        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_mutate_object_permission(info, folder_id)
        input.update({'last_modified_user': info.context.user.email})

        return super().mutate_and_get_payload(root, info, **input)


class DeleteDefaultTable(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClassFolder.has_permission(info)
        table_instance = DefaultTableModel.objects.filter(pk=id).first()
        if table_instance:
            ok = True
            if table_instance.host_document:
                folder_id = table_instance.host_document.folder.id
            else:
                folder_id = table_instance.folder.id
            PermissionClassFolder.has_mutate_object_permission(info, folder_id)
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
            folder_id = table_instance.folder.id

        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_mutate_object_permission(info, folder_id)

        host_folder = Folder.objects.filter(pk=folder_id).first()

        input.update({'owner': info.context.user.pkid,
                      'last_modified_user': info.context.user.email})

        url = None

        if "document_logo_url" in input:
            url = input['document_logo_url']
            del input['document_logo_url']

        if info.context.FILES:
            disk_space = check_disk_space(project=folder,
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
        obj.col_order.append(response.column_id)
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
            folder_id = table_instance.folder.id

        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_mutate_object_permission(info, folder_id)
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
        host_table = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, host_table, input=None):
        ok = False
        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_mutate_object_permission(info, host_table)
        column_instance = UserColumn.objects.filter(pk=id).first()
        if column_instance:
            ok = True
            pk = column_instance.id
            if column_instance.column_type == "image":
                column_instance.delete()
                recount_disk_space(info.context.user)
            else:
                column_instance.delete()
            table = DefaultTableModel.objects.filter(pk=host_table).first()
            table.col_order.remove(pk)
            table.save()
        return DeleteTableColumn(ok=ok)


class CreateFrame(SerializerMutation):
    class Meta:
        serializer_class = serializers.DefaultTableFrameSerializer
        model_operations = ['create']
        model_class = DefaultTableFrame
        lookup_field = 'id'

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        table_instance = DefaultTableModel.objects.filter(id=input["host_default_table"]).first()
        if table_instance.host_document:
            folder_id = table_instance.host_document.folder.id
        else:
            folder_id = table_instance.folder.id

        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_mutate_object_permission(info, folder_id)
        input.update({'owner': info.context.user.pkid,
                      'last_modified_user': info.context.user.email})
        response = super().mutate_and_get_payload(root, info, **input)

        new_obj = DefaultTableFrame.objects.filter(id=response.__dict__["id"]).first()
        add_userfields(info.context.user, table_instance, new_obj)
        return response


class UpdateFrame(SerializerMutation):
    class Meta:
        serializer_class = serializers.DefaultTableFrameSerializer
        model_operations = ['update']
        model_class = DefaultTableFrame
        lookup_field = 'id'

    @staticmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        table_instance = DefaultTableFrame.objects.filter(id=input["id"]).first().host_table
        if table_instance.host_document:
            folder_id = table_instance.host_document.folder.id
        else:
            folder_id = table_instance.folder.id

        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_mutate_object_permission(info, folder_id)
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
        PermissionClassFolder.has_permission(info)
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
            folder_id = table_instance.folder.id

        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_mutate_object_permission(info, folder_id)
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
        PermissionClassFolder.has_permission(info)
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
            folder_id = table_instance.folder.id

        PermissionClassFolder.has_permission(info)
        PermissionClassFolder.has_mutate_object_permission(info, folder_id)
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
        PermissionClassFolder.has_permission(info)
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
        PermissionClassFolder.has_permission(info)
        ok = False
        table_instance = DefaultTableModel.objects.filter(pk=id).first()
        if table_instance:
            ok = True
            PermissionClassFolder.has_mutate_object_permission(info, table_instance.folder.id)
            duplicate_object(table_instance, project_id=table_instance.folder.id)
        return CopyTable(ok=ok)


class TableOpenAccess(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    doc_uuid = graphene.UUID()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        PermissionClassFolder.has_permission(info)
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
        PermissionClassFolder.has_permission(info)
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
        PermissionClassFolder.has_permission(info)
        ok = False
        table_instance = DefaultTableModel.objects.filter(id=id).first()
        new_host_folder = Folder.objects.filter(id=folder_id).first()
        if table_instance:
            ok = True
            PermissionClassFolder.has_mutate_object_permission(info, folder_id)
            table_instance.folder = new_host_folder
            table_instance.save()
        return MoveTable(ok=ok)


class AddUsercellFile(graphene.Mutation):
    class Arguments:
        file = Upload(required=False)
        url = graphene.String(required=False)
        id = graphene.ID(required=True)
        host_table = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info,
               id,
               host_table,
               file=None,
               url=None,
               response=None, **kwargs):

        instance = DefaultTableUsercell.objects.filter(pk=id).first()
        host_instance = DefaultTableModel.objects.filter(pk=host_table).first()

        if host_instance.folder:
            host_folder = host_instance.folder
        else:
            host_folder = host_instance.host_document.folder

        if file:
            new_instance = UsercellFile(file=file, host_usercell=instance, owner=info.context.user)
            new_instance.save()
        if url:
            file = download_logo(url=url, project=host_folder)
            new_instance = UsercellFile(file=file, host_usercell=instance, owner=info.context.user)
            new_instance.save()

        return AddUsercellFile(success=True)


class Mutation(graphene.ObjectType):
    create_default_table = CreateDefaultTable.Field()
    update_default_table = UpdateDefaultTable.Field()
    delete_default_table = DeleteDefaultTable.Field()
    create_table_column = CreateTableColumn.Field()
    update_table_column = UpdateTableColumn.Field()
    delete_table_column = DeleteTableColumn.Field()
    create_or_update_column_choice = CreateUpdateColumnChoice.Field()
    delete_column_choice = DeleteColumnChoice.Field()
    create_frame = CreateFrame.Field()
    update_frame = UpdateFrame.Field()
    delete_frame = DeleteFrame.Field()
    create_or_update_usercell = UpdateUserCell.Field()
    delete_user_cell = DeleteUserCell.Field()
    move_table = MoveTable.Field()
    open_table_access = TableOpenAccess.Field()
    close_table_access = TableCloseAccess.Field()
    copy_table = CopyTable.Field()
    add_usercell_file = AddUsercellFile.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
