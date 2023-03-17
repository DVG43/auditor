from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from common.utils import duplicate_object
from common.utils import get_model, unpack_nested_kwargs
from projects.models import Project


class CopyAndMoveDocMixin(ViewSet):
    allowed_move_models = ['file', 'text', 'link', 'document', 'poll']

    allowed_copy_models = ['file', 'text', 'link', 'document', 'poll']

    @action(methods=["PATCH"], detail=True, url_path='copy')
    def copy_document(self, request, **kwargs):
        """
        Копирует документ между проектами.
        """
        base = self.basename or kwargs['basename']
        kw = unpack_nested_kwargs(self.kwargs, base)
        current_host_project = kw['host_pk']
        if 'project_id' not in request.data:
            return Response({"project_id": "required field"},
                            status=status.HTTP_400_BAD_REQUEST)
        project_id = request.data['project_id']

        if 'object_id' not in request.data:
            return Response({"object_id": "required field"},
                            status=status.HTTP_400_BAD_REQUEST)
        obj_id = request.data['object_id']

        if 'model' not in request.data:
            return Response({"model": "required field"},
                            status=status.HTTP_400_BAD_REQUEST)
        model_name = request.data['model']
        if model_name not in self.allowed_copy_models:
            return Response({"model": "only texts, files, links"
                                      " are allowed to copy and move"},
                            status=status.HTTP_400_BAD_REQUEST)

        object = get_model(model_name).objects.filter(
            id=obj_id).filter(host_project_id=current_host_project).first()
        dup_obj = duplicate_object(object, project_id=project_id)
        serialized_object = self.get_serializer(dup_obj)
        return Response(
            data=serialized_object.data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=["PATCH"], detail=True, url_path='move')
    def move_document(self, request, **kwargs):
        """
        Перемещает документ между проектами.
        """
        base = self.basename or kwargs['basename']
        kw = unpack_nested_kwargs(self.kwargs, base)
        current_host_project = kw['host_pk']
        if 'project_id' not in request.data:
            return Response({"project_id": "required field"},
                            status=status.HTTP_400_BAD_REQUEST)
        project_id = request.data['project_id']

        if 'object_id' not in request.data:
            return Response({"object_id": "required field"},
                            status=status.HTTP_400_BAD_REQUEST)
        obj_id = request.data['object_id']

        if 'model' not in request.data:
            return Response({"model": "required field"},
                            status=status.HTTP_400_BAD_REQUEST)
        model_name = request.data['model']

        if model_name not in self.allowed_move_models:
            return Response({"model": "only texts, files, links"
                                      " are allowed to copy and move"},
                            status=status.HTTP_400_BAD_REQUEST)

        object = get_model(model_name).objects.filter(
            id=obj_id).filter(host_project_id=current_host_project).first()
        object.host_project = Project.objects.filter(id=project_id).first()
        object.save()
        serialized_object = self.get_serializer(object)
        return Response(
            data=serialized_object.data,
            status=status.HTTP_201_CREATED
        )
