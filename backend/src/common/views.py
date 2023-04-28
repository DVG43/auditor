import datetime
from uuid import uuid4

import requests
from bs4 import BeautifulSoup
from django.core import files
from django.core.files.base import ContentFile
import settings

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, views, viewsets
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import User
from document.models import Document
from common.models import UserColumn, UserCell, UserChoice, UsercellImage, StandardIcon
from common.permissions import IsOwnerOrIsProjectAccess, IsOwner
from common.serializers import (
    CalendarSerializer,
    UserColumnSerializer,
    UserCellSerializer,
    UserChoiceSerializer,
    UsercellImageSerializer,
    StandardIconSerializer,
)
from common.utils import (
    get_model,
    unpack_nested_kwargs,
    get_object_or_404,
    organize_data_row_sort_arrays, add_userfields,
    insert_frames, check_file_size,
    change_disk_space,
    recount_disk_space,
    update_host_modified_date,
    find_host_project,
    check_folder_exist
)
from folders.utils import get_child_folders
from projects.models import Project, Link, File, Text
from storyboards.models import Storyboard, Shot
from folders.models import Folder
from storyboards.serializers import FrameSerializer  # DO NOT REMOVE!


class FilterQuerySetMixin(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        print('40 vvv FilterQuerySetMixin.get_queryset vvv')
        user = self.request.user
        kw = unpack_nested_kwargs(self.kwargs, self.basename)
        self.kw = kw
        base = self.basename
        if base == 'project':
            queryset = user.get_objects_with_perms(get_model(base), ['read', 'edit', 'own'])
        else:
            queryset = get_model(base).objects.all()
        # queryset = get_model(base).objects.filter(owner=user)
        if self.request.user.is_invited:
            queryset = get_model(base).objects.filter(pk=self.request.user.document)
        if base in ['project', 'storyboard',
                    'file', 'link', 'text', 'document', 'folder']:
            queryset = queryset.filter(deleted_id__isnull=True).filter(owner__is_active=True)

        # Если в запросе есть /storyboards/0/ - выдать сториборд проекта
        if ('storyboard_pk' in self.kwargs
            and self.kwargs['storyboard_pk'] == '0') \
            or base == 'storyboard':
            project_storyboard = Storyboard.objects \
                .filter(host_project=self.kwargs['project_pk']) \
                .filter(deleted_id__isnull=True)
            if project_storyboard:
                project_storyboard_id = str(project_storyboard.first().pk)
                # Если запрос к самому сториборду - подменить pk
                if base == 'storyboard':
                    self.kwargs.update({'pk': project_storyboard_id})
                    self.check_object_permissions(self.request, project_storyboard.first())
                # Если запрос к дочерним объектам - подменить host_pk
                elif kw['host'] == 'storyboard':
                    if kw['host_pk'] == '0':
                        kw['host_pk'] = project_storyboard_id
                # Если запрос ниже дочерних - подменить parent_pk
                if kw['parent'] == 'storyboard':
                    kw['parent_pk'] = project_storyboard_id
            else:
                raise ValidationError({'error': 'no storyboard in project'})

        filter_kw = {}
        # # Фильтр по родительскому документу
        # if base not in ['project', 'contact', 'trash', 'usercell',
        #                 'usercolumn', 'folder']:
        #     filter_kw = {f"host_{kw['host']}": kw['host_pk']}

        # Фильтр userfields для всех frames
        if base == 'usercell' and kw['parent'] in ['storyboard']:
            filter_kw = {
                f"of_{kw['host']}__host_{kw['parent']}": kw['parent_pk']
            }
            if kw['host_pk'] != '0':
                filter_kw.update({f"of_{kw['host']}": kw['host_pk']})

        if base in ['department', 'position']:
            filter_kw = {'owner': user}

        # Фильтр usercolumns для всех frames
        if base == 'usercolumn' and kw['parent'] in ['storyboard']:
            filter_kw = {f"of_{kw['parent']}": kw['parent_pk']}


        print('^^^', filter_kw, '^^^')
        self.queryset = queryset.filter(**filter_kw)

        return self.queryset


class PpmViewSet(ModelViewSet, FilterQuerySetMixin):
    permission_classes = [IsOwnerOrIsProjectAccess]

    def retrieve(self, request, *args, **kwargs):
        # if self.basename in ['storyboard', 'chrono']:
        #     instance = self.get_object()
        #     # чистка и сортировка массивов сортировки
        #     organize_data_row_sort_arrays(instance)
        #     serializer = self.get_serializer(instance)
        #     return Response(serializer.data)
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        print(120, 'MVS.create')
        user = request.user
        base = self.basename or kwargs['basename']
        kw = unpack_nested_kwargs(self.kwargs, base)
        host_obj = None

        check_folder_exist(request)

        # скачиваем логотип для документа по ссылке
        if 'document_logo_url' in request.data:
            url = request.data['document_logo_url']
            try:
                response = requests.get(url, allow_redirects=True)
            except (requests.HTTPError, requests.ConnectionError) as error:
                return Response({'document_logo_url': 'not valid url'},
                                status=status.HTTP_400_BAD_REQUEST)
            filename = url.split('/')[-1]
            file = files.File(ContentFile(response.content), filename)

            # проверяем хватает ли места для логотипа на диске
            host_prj = find_host_project(kw)
            user = User.objects.filter(pkid=host_prj.owner.pkid).first()
            disk_space = user.disk_space if user.disk_space else 0
            if file.size + disk_space > settings.DISK_SIZE:
                return Response({'file': 'Not enough space on disk for file'},
                                status=status.HTTP_400_BAD_REQUEST)

            kwargs['document_logo'] = files.File(ContentFile(response.content), filename)

        if request.FILES:
            disk_space = check_file_size(request, request.user)
            # проверяем, что для загружаемого файла достаточно места на диске
            if not disk_space:
                return Response({'file': 'Not enough space on disk for file'},
                                status=status.HTTP_400_BAD_REQUEST)
        # # проверка прав на род.документ
        # if kw['host'] and kw['host_pk'] != "0":
        #     print(128)
        #     host_obj = get_object_or_404(kw['host'], kw['host_pk'])
        # elif kw['host'] == 'storyboard' and kw['host_pk'] == '0':
        #     print(131)
        #     host_obj = Storyboard.objects \
        #         .filter(deleted_id__isnull=True) \
        #         .filter(host_project=kw['parent_pk']).first()
        # привязка к род. документу
        # if host_obj:
        #     print(137, type(request.data))
        #     request.data.update({f"host_{kw['host']}": host_obj.id})
        # if base not in ["project"]:
        #     host_prj = find_host_project(kw)
        #     if host_prj:
        #         request.data.update({"owner": host_prj.owner})
        print(139, 'host_obj =', host_obj)
        serializer = self.get_serializer(data=request.data)
        print(141, serializer.__class__.__name__)
        serializer.is_valid(raise_exception=True)
        new_obj = self.perform_create(serializer)
        print(144, new_obj, 'created')

        # # Получение существующих юзер.колонок для документа и их добавление
        # # для всех объектов
        # if base in ['frame']:
        #     print(149)
        #     add_userfields(user, host_obj, new_obj)

        # Добавление участника в проект, при создании из проекта
        if base == 'contact' and kw['host'] == 'project':
            print(154)
            host_obj.contacts.add(new_obj)

        new_obj.save()
        new_obj.refresh_from_db()

        # обновляем место на диске после сохранения нового файла
        if request.FILES:
            change_disk_space(request.user, disk_space)

        # обновляем время и юзера последнего изменения сториборда, вызывного или шутингплана,
        # при изменении дочерних объектов
        if base in ["chrono", "shot", "frame", "chronoframe",
                    "usercell", "userchoice", "usercellimage", "usercolumn", "userfield"]:
            update_host_modified_date(kw, request.user.email)

        serializer = self.get_serializer(instance=new_obj)
        print(172, serializer.__class__.__name__)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        print(179, 'MVS.update')
        partial = kwargs.pop('partial', False)
        base = self.basename or kwargs['basename']
        kw = unpack_nested_kwargs(kwargs, base)
        self.kw = kw

        check_folder_exist(request)
        # скачиваем логотип для документа по ссылке
        if 'document_logo_url' in request.data:
            url = request.data['document_logo_url']
            try:
                response = requests.get(url, allow_redirects=True)
            except (requests.HTTPError, requests.ConnectionError) as error:
                return Response({'document_logo_url': 'not valid url'},
                                status=status.HTTP_400_BAD_REQUEST)
            filename = url.split('/')[-1]
            file = files.File(ContentFile(response.content), filename)

            # проверяем достаточно ли места для скачиваемого файла на диске
            obj = get_model(base).objects.filter(id=kw['base_pk']).first()
            user = User.objects.filter(pkid=obj.owner.pkid).first()
            disk_space = user.disk_space if user.disk_space else 0
            if file.size + disk_space > settings.DISK_SIZE:
                return Response({'file': 'Not enough space on disk for file'},
                                status=status.HTTP_400_BAD_REQUEST)

            logo_field = 'logo' if isinstance(obj, Project) else 'document_logo'
            request.data[logo_field] = files.File(ContentFile(response.content), filename)
            # request.data['document_logo'] = files.File(ContentFile(response.content), filename)

        if request.FILES:
            obj = get_model(base).objects.filter(id=kw['base_pk']).first()
            disk_space = check_file_size(request, obj.owner)
            # проверяем, что для загружаемого файла достаточно места на диске
            if not disk_space:
                return Response({'file': 'Not enough space on disk for file'},
                                status=status.HTTP_400_BAD_REQUEST)

        if self.basename in ['contact'] \
            and kw['parent'] in ['project'] \
            and not request.data:
            print(186, 'PVS.update Add contact to document')
            contact = get_object_or_404('contact', kw['base_pk'])
            host_obj = get_object_or_404(kw['host'], kw['host_pk'])
            # Добавление участников в проект из съёмочной группы
            host_obj.contacts.add(contact)
            return self.list(request)

        if base == 'storyboard' and kw['base_pk'] == '0':
            instance = Storyboard.objects \
                .filter(deleted_id__isnull=True) \
                .filter(host_project=kw['host_pk']).first()
        else:
            instance = get_object_or_404(base, kw['base_pk'])
        print(206, 'Instance =', instance)
        self.check_object_permissions(self.request, instance)

        # Изменение польз.ячеек
        if 'userfields' in request.data:
            print(214, 'MVS update userfields')
            userfields = request.data.pop('userfields')
            if userfields:
                # Проверка формата: список словарей
                if isinstance(userfields, list) \
                    and isinstance(userfields[0], dict):
                    for usercell_data in userfields:
                        if 'cell_id' in usercell_data:
                            uc_id = usercell_data.pop('cell_id')
                            uc = get_object_or_404('usercell', uc_id)
                            # Удаление ключа
                            if 'images' in usercell_data:
                                usercell_data.pop('images')

                            # Очистка варианта выбора в поле выбора
                            if 'choice_id' in usercell_data \
                                and usercell_data['choice_id'] == 0:
                                usercell_data.pop('choice_id')
                                usercell_data['cell_content'] = ''
                            serializer = UserCellSerializer(
                                instance=uc, data=usercell_data, partial=True)
                            serializer.is_valid(raise_exception=True)
                            serializer.update(
                                uc, serializer.validated_data)
                else:
                    raise ParseError(
                        {'error': 'userfields must be a list of objects'})

        if 'frames' in request.data and base in ['chrono']:
            # при добавлении фреймов из СБ создаём chronoframe/unitframe и
            # добавляем в них фреймы СБ по id указанным в списке frames: [ ]
            instance = get_object_or_404(base, kw['base_pk'])  #
            # host_chrono/unit
            print(247, instance)
            insert_frames(request.user, base, instance, request.data['frames'])
            organize_data_row_sort_arrays(instance)
            instance = self.get_object()
            serializer = self.get_serializer(instance=instance)
            return Response(serializer.data)

        if 'images' in request.data:
            if isinstance(request.data['images'], InMemoryUploadedFile):
                print(256, instance)
                images = request.data.pop('images')
                for image in images:
                    data = {
                        'file': image,
                        'host_usercell': instance.id
                    }
                    serializer = UsercellImageSerializer(
                        data=data, context={'user': request.user})
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
            else:
                # Удаление ссылок на изображения
                for image in request.data['images']:
                    image.pop('file')

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # обновляем место на диске после обновления файла
        if request.FILES or 'document_logo_url' in request.data:
            recount_disk_space(obj.owner)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        if base in ['storyboard', 'chrono']:
            organize_data_row_sort_arrays(instance)
            serializer = self.get_serializer(instance=instance)

        # обновляем время и юзера последнего изменения сториборда, вызывного или шутингплана,
        # при изменении дочерних объектов
        if base in ["chrono", "shot", "frame", "chronoframe",
                    "usercell", "userchoice", "usercellimage", "usercolumn", "userfield"]:
            update_host_modified_date(kw, request.user.email)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save(last_modified_user=self.request.user.email)

    def destroy(self, request, *args, **kwargs):
        print(290, 'MVS.destroy')
        base = self.basename or kwargs['basename']
        self.kw = unpack_nested_kwargs(kwargs, base)
        obj = self.get_object()

        if isinstance(obj, Project):
            obj.deleted_id = uuid4()
            obj.deleted_since = timezone.now()
            obj.save()
            rel_docs = settings.REL_DOCS
            for doc_type in rel_docs:
                for doc in getattr(obj, doc_type).filter(deleted_id__isnull=True):
                    if doc:
                        doc.deleted_id = uuid4()
                        doc.deleted_since = timezone.now()
                        doc.save()
        elif isinstance(obj, Folder):
            folders = [obj]
            child_folders = obj.folders.all()
            if child_folders:
                folders.extend(get_child_folders(child_folders))
            rel_docs = settings.REL_DOCS
            for folder in folders:
                folder.deleted_id = uuid4()
                folder.deleted_since = timezone.now()
                folder.save()
                for doc_type in rel_docs:
                    if doc_type != 'folders':
                        for doc in getattr(folder, doc_type).filter(
                            deleted_id__isnull=True
                        ):
                            if doc:
                                doc.deleted_id = uuid4()
                                doc.deleted_since = timezone.now()
                                doc.save()
        elif isinstance(obj, (Link, File, Text, Document)):
            obj.deleted_id = uuid4()
            obj.deleted_since = timezone.now()
            obj.save()
        elif isinstance(obj, Storyboard):
            inst_sb_deleted = Storyboard.objects.filter(deleted_id__isnull=False).first()
            if inst_sb_deleted:
                inst_sb_deleted.deleted_id = None
                inst_sb_deleted.deleted_since = None
                inst_sb_deleted.save()
            obj.deleted_id = uuid4()
            obj.deleted_since = timezone.now()
            obj.save()
        elif isinstance(obj, Shot):
            # обновляем время и юзера последнего изменения сториборда, вызывного или шутингплана,
            # при изменении дочерних объектов
            update_host_modified_date(self.kw, request.user.email)
            # обновляем место на диске
            owner = obj.owner
            obj.delete()
            recount_disk_space(owner)
        else:
            # обновляем время и юзера последнего изменения сториборда, вызывного или шутингплана,
            # при изменении дочерних объектов
            if base in ["chrono", "frame", "chronoframe",
                        "usercell", "userchoice", "usercellimage", "userfield"]:
                update_host_modified_date(self.kw, request.user.email)
            obj.delete()
        return Response({'success': 'object deleted'}, status=204)


class UserColumnViewSet(PpmViewSet):
    queryset = UserColumn.objects.all()
    serializer_class = UserColumnSerializer
    permission_classes = [IsOwnerOrIsProjectAccess]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        print(331, 'common.UserColumnViewSet.create')
        kw = unpack_nested_kwargs(kwargs, self.basename)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usercolumn = self.perform_create(serializer)
        print(347, usercolumn, 'created')

        obj = None


        if kw['host'].endswith('frame'):
            print(357)
            if kw['parent'] == 'storyboard' and kw['parent_pk'] == '0':
                print(359)
                obj = Storyboard.objects \
                    .filter(host_project=kw['super_pk']) \
                    .filter(deleted_id__isnull=True).first()
            else:
                print(366)
                obj = get_object_or_404(kw['parent'], kw['parent_pk'])
            if not obj:
                raise ValidationError({'error': 'no storyboards found'})
            print(368, obj)
            obj.frame_columns.add(usercolumn.id)  # привязка к host_sb/unit
            print(370)
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
                                host_usercolumn=usercolumn, owner=request.user)
                            frame_obj.userfields.add(usercell)

                serializer = self.get_serializer(instance=usercolumn)


        # обновляем время и юзера последнего изменения сториборда, вызывного или шутингплана,
        # при изменении дочерних объектов
        update_host_modified_date(kw, request.user.email)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        print(404, 'UserColumnVS.update')
        if request.data:
            pass

        return super().update(request, *args, **kwargs)

    # def perform_create(self, serializer):
    #     return serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Удаление пользовательской колонки DELETE /usercolumns/<field_id>/
        Удаляет колонку и всё связанное с ним содержимое (все cell_id)!
        """
        print(421, 'UserColumn delete', kwargs)
        if kwargs['pk'] == '0':
            UserColumn.objects.all().delete()
        else:
            uf = get_object_or_404('usercolumn', kwargs['pk'])
            # обновляем время и юзера последнего изменения сториборда, вызывного или шутингплана,
            # при изменении дочерних объектов
            kw = unpack_nested_kwargs(kwargs, 'usercolumn')
            update_host_modified_date(kw, request.user.email)
            uf.delete()
        # return Response({"success": "userfield (column) deleted"})
        return super().list(request)


class CalendarView(views.APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    @staticmethod
    def get(request, *args, **kwargs):
        print(436, 'common.CalendarView')
        from_date = kwargs['from']
        to_date = kwargs['to']
        from_date_dt = datetime.date.fromisoformat(from_date)
        to_date_dt = datetime.date.fromisoformat(to_date)

        q_user_trash = Q(owner=request.user) & Q(deleted_id__isnull=True)
        q = q_user_trash

        projects = Project.objects.filter(q).distinct()
        response = []
        for idx, project in enumerate(projects):
            response.append({
                'project_id': project.id,
                'project_name': project.name,
                'documents': []})
            # TODO Refactor
        serializer = CalendarSerializer(response, many=True)
        return Response(serializer.data)


class UserCellViewSet(PpmViewSet):
    queryset = UserCell.objects.all()
    serializer_class = UserCellSerializer
    permission_classes = [IsOwnerOrIsProjectAccess]
    http_method_names = ['get', 'patch', 'delete']


class UserChoiceViewSet(PpmViewSet):
    queryset = UserChoice.objects.all()
    serializer_class = UserChoiceSerializer
    permission_classes = [IsOwnerOrIsProjectAccess]
    http_method_names = ['get', 'patch', 'delete']


class UsercellImageViewSet(PpmViewSet):
    queryset = UsercellImage.objects.all()
    serializer_class = UsercellImageSerializer
    permission_classes = [IsOwnerOrIsProjectAccess]
    http_method_names = ['get', 'patch', 'delete']


class GetOpenGraphTagsView(views.APIView):
    """
    View to get OpenGraph metatags, such as title, description and image
    from the specified url.
    """
    # Какие права нужны?
    # permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser,)
    empty_tags = {'title': None, 'description': None, 'image': None}

    def get_metatag_data(self, html_data, tag_property_value):
        """Return the Open Graph data of required tag.
            Args:
                html_data: HTML source of scraped page.
                tag_property_value: meta property of Open Graph tags
                                    for example as 'og:title'.
            Returns:
                parsed value or None if OpenGraph tag value is missing.
            """
        try:
            if html_data.find('meta', property=f'og:{tag_property_value}'):
                return html_data.find('meta', property=f'og:{tag_property_value}')['content']
            return
        except AttributeError as error:
            # нужно логирование
            return

    def get_page_html(self, url: str):
        """Scrapes a URL and returns the HTML source.
        Args:
            url (string): URL of a page.
        Returns:
            result (dict): dict of values OpenGraph of tags
                           'title', 'description' and 'image'
                           if response status_code == 200 or
                           dict with None values
        """
        try:
            response = requests.get(url, timeout=5,)
            if response.status_code == 200:
                html_data = BeautifulSoup(response.text, 'html.parser',)
                result = {key: self.get_metatag_data(html_data, key) for key in
                          ['title', 'description', 'image']}
                return result
            return self.empty_tags
        except requests.exceptions.RequestException:
            # нужно логирование
            # logger.info('Error raised while url processing, site isn't reachable')
            return self.empty_tags

    def post(self, request, *args, **kwargs):
        """
        Expects for the 'url' passed in the request to get its OpenGraph meta tags.
        Returns:
            JSON with OpenGraph meta tags values. If the 'url' is not received or its
            tags are not filled in, returns JSON where None instead of OpenGraph tag values.
        """
        if 'url' in request.data:
            return Response(self.get_page_html(request.data['url']))
        return Response(self.empty_tags)

class StandardIconViewSet(ModelViewSet):
    """
    ViewSet to work with StandardIcon.
    """
    permission_classes = [IsAuthenticated]
    queryset = StandardIcon.objects.filter(is_active=True)
    serializer_class = StandardIconSerializer
