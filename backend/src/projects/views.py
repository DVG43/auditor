from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.mixins import CopyAndMoveDocMixin
from common.utils import get_model, count_space_per_object, recount_disk_space
from common.views import PpmViewSet
from projects.models import Project, Link, File, Text
from projects.serializers import (ProjectDetailSerializer,
                                  ProjectListSerializer,
                                  LinkSerializer,
                                  FileSerializer, TextSerializer)
from shared_access.mixins import ShareMixin
from shared_access.serializers import ShareProjectSerializer, ShareDeleteSerializer
from storyboards.models import Storyboard
from storyboards.serializers import StoryboardDetailSerializer
from storyboards.views import create_default_storyboard_frame_columns


class ProjectViewSet(PpmViewSet, ShareMixin):
    queryset = Project.objects.prefetch_related(
        'contacts', 'storyboards', 'documents',
        'links', 'files', 'texts', 'timings')
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action == "add":
            return ShareProjectSerializer
        elif self.action == "trash":
            return ShareDeleteSerializer
        return ProjectDetailSerializer

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)

        if res.status_code == status.HTTP_400_BAD_REQUEST:
            return res

        prj_id = res.data['id']
        prj_name = request.data['name']
        data = {
            'name': f'{prj_name}_Сториборд',
            'host_project': prj_id
        }
        context = {'user': request.user}
        serializer = StoryboardDetailSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        sb = serializer.create(serializer.validated_data)
        create_default_storyboard_frame_columns(sb, request.user)

        prj = Project.objects.get(pk=prj_id)
        serializer = self.get_serializer(instance=prj)
        return Response(serializer.data)

    @action(methods=["GET"], detail=False, url_path='space')
    def get_projects_space(self, request):
        """
        По данным пользователя собирает все проекты и считает статистику
        используемой памяти по проекту, сториборду, вызывному и файлам.
        """
        projects = Project.objects.filter(owner=request.user).all()
        response = []
        for prj in projects:

            # собирает документы, в которых хранятся файлы
            storyboard = Storyboard.objects.filter(host_project=prj).first()
            files = File.objects.filter(host_project=prj.id).all()

            prj_size = 0
            documents = []


            # получает статистику по сториборду (картинки шотов)
            if storyboard:
                storyboard_size = count_space_per_object(request.user, storyboard, "storyboard")
                prj_size += storyboard_size
                documents.append({
                    "id": storyboard.id,
                    "model": "storyboard",
                    "name": storyboard.name,
                    "size": storyboard_size
                })

            # получает статистику по файлам
            for file in files:
                prj_size += file.file.size
                documents.append({
                            "id": file.id,
                            "name": file.name,
                            "size": file.file.size,
                            "model": "file"
                        })

            # получаем вес логотипа
            logo_size = 0 if not prj.logo else prj.logo.size

            prj_data = {
                "id": prj.id,
                "name": prj.name,
                "model": "project",
                "space": prj_size + logo_size,
                "documents": documents
            }

            response.append(prj_data)

        return Response(data={"projects": response})

    @action(methods=["POST"], detail=False, url_path="space/clean")
    def clean_space(self, request, *args, **kwargs):
        """
        Принимает на вход данные вида:
        {"model": "storyboard"|"documents"|"timings",
        "id": int}
        И безвозвратно удаляет выбранный проект или документ.
        """
        models = [
            "project",
            "storyboard",
            "file",
            "text",
            "link",
            "document",
            "folder"
        ]
        if "model" not in request.data or "id" not in request.data:
            return Response({"required_field": "model and id are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.data["model"] not in models:
            return Response({"wrong_model": f"you can delete only {models}"},
                            status=status.HTTP_400_BAD_REQUEST)
        get_model(request.data["model"]).objects.filter(id=request.data["id"]).delete()
        recount_disk_space(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LinkViewSet(PpmViewSet, CopyAndMoveDocMixin):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer


class FileViewSet(PpmViewSet, CopyAndMoveDocMixin):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    @action(methods=['GET'], url_path='content', detail=True)
    def get_file_content(self, request, pk=None, project_pk=None):

        obj = File.objects.filter(id=pk).filter(
            host_project=project_pk).first()

        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)

        file = obj.file
        title = obj.slugged_name + '.' + file.name.split('.')[-1]
        response = FileResponse(file.open(),
                                as_attachment=True,
                                filename=title)
        return response


class TextViewSet(PpmViewSet, CopyAndMoveDocMixin):
    queryset = Text.objects.all()
    serializer_class = TextSerializer
