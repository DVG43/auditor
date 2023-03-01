import datetime
import uuid
import graphene
from django.db.models import Prefetch
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required
from graphene_django.types import ObjectType, DjangoObjectType

from common.models import UserColumn, UserCell, UserChoice
from common.serializers import UserColumnSerializer, UserChoiceSerializer, UserCellSerializer
from common.utils import change_disk_space, recount_disk_space, get_model
from . import serializers
from graphql_utils.utils_graphql import PermissionClass, check_disk_space, download_logo
from projects.models import Project
from table.models import DefaultTableModel, DefaultTableFrame


class DefaultTableType(DjangoObjectType):
    perm = graphene.String()
    perms = graphene.List(graphene.String)

    class Meta:
        model = DefaultTableModel

    @staticmethod
    def resolve_perm(self, info):
        user = info.context.user
        project = self.host_document
        perms = user.get_object_perm_as_str_list(project)
        return perms[0] if len(perms) == 1 else perms

    @staticmethod
    def resolve_perms(self, info):
        return self.perms


class Query(ObjectType):
    all_tables = graphene.List(DefaultTableType, host_document_id=graphene.Int(), host_document_model=graphene.String())
    table_by_pk = graphene.Field(DefaultTableType, table_pk=graphene.Int())

    @login_required
    def resolve_all_tables(self, info, host_document_id=None, host_document_model=None):
        PermissionClass.has_permission(info)
        if host_document_model == "project":
            PermissionClass.has_query_object_permission(info, host_document_id)
        else:
            project_id = get_model(host_document_model).filter(pk=host_document_id).first().host_project.id
            PermissionClass.has_query_object_permission(info, project_id)

        return DefaultTableModel.objects.filter(
            host_document_id=host_document_id).prefetch_related(
            Prefetch('table_frames',
                     queryset=DefaultTableFrame.objects.prefetch_related(
                         'userfields'))).all()

    @login_required
    def resolve_table_by_pk(self, info, table_pk=None):
        table = DefaultTableModel.objects.filter(pk=table_pk).first()
        PermissionClass.has_permission(info)
        if table.host_document_model == "project":
            PermissionClass.has_query_object_permission(info, table.host_document_id)
        else:
            host_project_id = get_model(table.host_document_model).filter(
                pk=table.host_document_id).first().host_project.id
            PermissionClass.has_query_object_permission(info, host_project_id)

        return DefaultTableModel.objects.filter(
            pk=table_pk).prefetch_related(
            Prefetch('table_frames',
                     queryset=DefaultTableFrame.objects.prefetch_related(
                         'userfields'))).all()


class CreateDefaultTable(SerializerMutation):
    class Meta:
        serializer_class = serializers.DefaultTableSerializer
        model_operations = ['create', 'update']
        model_class = DefaultTableModel

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        prj_id = input["host_project"]
        del input["host_project"]
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


class UpdateDefaultTable(SerializerMutation):

    class Meta:
        serializer_class = serializers.DefaultTableSerializer
        model_operations = ['update']
        model_class = DefaultTableModel
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


class DeleteDefaultTable(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        table_instance = DefaultTableModel.objects.filter(pk=id).first()
        if table_instance:
            ok = True
            # PermissionClass.has_mutate_object_permission(info, table_instance.host_project.id)
            table_instance.deleted_id = uuid.uuid4()
            table_instance.deleted_since = datetime.datetime.now()
            table_instance.last_modified_user = info.context.user.email
            table_instance.save()
        return DeleteDefaultTable(ok=ok)


class CreateTableColumn(SerializerMutation):
    class Meta:
        serializer_class = UserColumnSerializer
        model_operations = ['create']
        model_class = UserColumn
        lookup_field = 'id'

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        prj_id = input["host_project"]
        del input["host_project"]
        PermissionClass.has_permission(info)
        PermissionClass.has_mutate_object_permission(info, prj_id)

        host_project = Project.objects.filter(pk=prj_id).first()

        input.update({'owner': info.context.user.pkid,
                      'last_modified_user': info.context.user.email})
        print(input)

        url = None

        if "document_logo_url" in input:
            url = input['document_logo_url']
            del input['document_logo_url']

        if info.context.FILES:
            disk_space = check_disk_space(project=host_project,
                                          info=info)
        host = input["host_document_id"]
        del input["host_document_id"]
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

        obj = DefaultTableModel.filter(pk=host).first()
        obj.frame_columns.add(response.id)
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
                    if cls_name == 'Frame':
                        usercell = UserCell.objects.create(
                            host_usercolumn=response.id, owner=info.context.user)
                        frame_obj.userfields.add(usercell)


        return response


class UpdateTableColumn(SerializerMutation):
    class Meta:
        serializer_class = UserColumnSerializer
        model_operations = ['update']
        model_class = UserColumn
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


class DeleteTableColumn(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, id, input=None):
        ok = False
        PermissionClass.has_permission(info)
        # del input["host_project"]
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


class DeleteFrame(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

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
        serializer_class = UserChoiceSerializer
        model_operations = ['create', 'update']
        model_class = UserChoice
        lookup_field = 'id'


class DeleteColumnChoice(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

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


# class CreateUpdateUserCell(SerializerMutation):
#     class Meta:
#         serializer_class = UserCellSerializer
#         model_operations = ['create', 'update']
#         model_class = UserCell
#         lookup_field = 'cell_id'


# class DeleteUserCell(graphene.Mutation):
#     class Arguments:
#         id = graphene.Int(required=True)
#
#     ok = graphene.Boolean()
#
#     @staticmethod
#     @login_required
#     def mutate(root, info, id, input=None):
#         ok = False
#         PermissionClass.has_permission(info)
#         cell_instance = UserCell.objects.filter(cell_id=id).first()
#         if cell_instance:
#             ok = True
#             if cell_instance.host_usercolumn.column_type == "image":
#                 cell_instance.delete()
#                 recount_disk_space(info.context.user)
#             else:
#                 cell_instance.delete()
#         return DeleteUserCell(ok=ok)


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
    # create_or_update_usercell = CreateUpdateUserCell.Field()
    # delete_user_cell = DeleteUserCell.Field()


# schema = graphene.Schema(query=Query, mutation=Mutation)
