import graphene
from graphene_file_upload.scalars import Upload

from common.utils import change_disk_space, get_model
from graphql_utils.utils_graphql import (
    check_disk_space,
    download_logo,
    PermissionClassFolder
)


# def get_model(model_name):
#     print(ContentType.objects.__dict__)
#     model_app_name = ContentType.objects.get(model=model_name).app_label
#     print(model_name, model_app_name)
#     return apps.get_model(model_app_name, model_name)


class UploadLogo(graphene.Mutation):
    class Arguments:
        file = Upload(required=False)
        url = graphene.String(required=False)
        model = graphene.String(required=True)
        document_id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, model,
               document_id,
               file=None,
               url=None,
               response=None, **kwargs):
        PermissionClassFolder.has_permission(info)
        instance = get_model(model).objects.filter(pk=document_id).first()
        host_folder = instance.folder

        PermissionClassFolder.has_mutate_object_permission(info, host_folder.id)

        if file:
            instance.document_logo = file
            instance.save()
        if url:
            logo = download_logo(url=url, project=host_folder)
            instance.document_logo = logo
            instance.save()

        return UploadLogo(success=True)


class Mutation(graphene.ObjectType):
    add_logo = UploadLogo.Field()


schema = graphene.Schema(mutation=Mutation)
