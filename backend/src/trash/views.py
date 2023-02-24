import datetime as dt
import os
from uuid import uuid4

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

import settings
from accounts.models import User
from common.permissions import IsOwner
from common.utils import count_space_per_object
from projects.models import Project, Link, File, Text
from storyboards.models import Storyboard
from document.models import Document
from timing.models import Timing
from folders.models import Folder
from poll.models.poll import Poll
from folders.utils import get_child_folders
from .serializers import TrashProjectListSerializer


class TrashViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    http_method_names = ['get', 'delete']
    queryset = Project.objects.filter(deleted_id__isnull=False)

    def get_queryset(self):
        print(24, 'TrashVS.get_queryset')
        q = (
            Q(deleted_id__isnull=False) |
            Q(storyboards__deleted_id__isnull=False) |
            Q(links__deleted_id__isnull=False) |
            Q(files__deleted_id__isnull=False) |
            Q(texts__deleted_id__isnull=False) |
            Q(timings__deleted_id__isnull=False) |
            Q(documents__deleted_id__isnull=False) |
            Q(folders__deleted_id__isnull=False)|
            Q(polls__deleted_id__isnull=False)
        )
        queryset = Project.objects \
            .filter(owner=self.request.user) \
            .filter(q)
        return queryset

    def list(self, request, *args, **kwargs):
        self.clean_old_docs()
        self.change_disk_space(request.user)
        serializer = TrashProjectListSerializer(
            self.get_queryset().distinct(), many=True, context={'request': request})
        return Response(serializer.data)

    def clean_old_docs(self, expire_days=7):
        print(34, 'Checking expired documents...')
        from django.utils import timezone
        now = timezone.now()
        queryset = self.get_queryset()
        rel_docs = settings.REL_DOCS
        queryset = list(set(queryset))

        if queryset:
            for obj in queryset:
                obj.refresh_from_db()
                if obj.deleted_since:
                    expire_date = obj.deleted_since + dt.timedelta(
                        days=expire_days
                    )
                    if expire_date <= now:
                        obj.delete()
                else:
                    for doc_type in rel_docs:
                        for doc in getattr(obj, doc_type).filter(
                            deleted_id__isnull=False
                        ):
                            if doc:
                                expire_date = doc.deleted_since + dt.timedelta(
                                    days=expire_days
                                )
                                if expire_date <= now:
                                    doc.delete()
        return None

    def change_disk_space(self, user):
        """
        Функция, пересчитывающая и сохраняющая размер загруженных пользователем файлов после очистки
        корзины.
        """
        folder = os.path.join(os.getcwd(), settings.MEDIA_ROOT, str(user.pkid))
        size = 0
        for path, dirs, files in os.walk(folder):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)
        user = User.objects.filter(pkid=user.pkid).first()
        user.disk_space = size
        user.save()

    def destroy(self, request, *args, **kwargs):
        print(59, 'Restore from trash')
        qs = self.get_queryset().filter(deleted_id=kwargs['pk'])
        if not qs:
            qs = Storyboard.objects.filter(deleted_id=kwargs['pk']) or \
                 Link.objects.filter(deleted_id=kwargs['pk']) or \
                 File.objects.filter(deleted_id=kwargs['pk']) or \
                 Text.objects.filter(deleted_id=kwargs['pk']) or \
                 Timing.objects.filter(deleted_id=kwargs['pk']) or \
                 Document.objects.filter(deleted_id=kwargs['pk']) or \
                 Folder.objects.filter(deleted_id=kwargs['pk']) or \
                 Poll.objects.filter(deleted_id=kwargs['pk'])
        if qs:
            instance = qs.first()
            if isinstance(instance, Project):
                inst_sb_deleted = instance.storyboards.filter(deleted_id__isnull=False).first()
                inst_sb_new = instance.storyboards.filter(deleted_id__isnull=True).first()
                if inst_sb_deleted and inst_sb_new:
                    inst_sb_new.deleted_id = uuid4()
                    inst_sb_new.deleted_since = timezone.now()
                    inst_sb_new.save()
                if inst_sb_deleted:
                    inst_sb_deleted.deleted_id = None
                    inst_sb_deleted.deleted_since = None
                    inst_sb_deleted.save()
                if instance.documents.count() > 0:
                    for doc in instance.documents.filter(deleted_id__isnull=False):
                        doc.deleted_id = None
                        doc.deleted_since = None
                        doc.save()
                if instance.files.count() > 0:
                    for file in instance.files.filter(deleted_id__isnull=False):
                        file.deleted_id = None
                        file.deleted_since = None
                        file.save()
                if instance.folders.count() > 0:
                    for folder in instance.files.filter(deleted_id__isnull=False):
                        folder.deleted_id = None
                        folder.deleted_since = None
                        folder.save()
                if instance.links.count() > 0:
                    for link in instance.files.filter(deleted_id__isnull=False):
                        link.deleted_id = None
                        link.deleted_since = None
                        link.save()
            elif isinstance(instance, Folder):
                folders = [instance]
                child_folders = instance.folders.all()
                if child_folders:
                    folders.extend(get_child_folders(child_folders))
                rel_docs = settings.REL_DOCS
                for folder in folders:
                    folder.deleted_id = None
                    folder.deleted_since = None
                    folder.save()
                    for doc_type in rel_docs:
                        if doc_type != 'folders':
                            for doc in getattr(folder, doc_type).filter(
                                deleted_id__isnull=False
                            ):
                                if doc:
                                    doc.deleted_id = None
                                    doc.deleted_since = None
                                    doc.save()
            elif isinstance(instance, (Storyboard, Document)):
                prj = instance.host_project
                if prj.deleted_id:
                    prj.deleted_id = None
                    prj.deleted_since = None
                    prj.save()
                if isinstance(instance, Storyboard):
                    inst_sb_new = prj.storyboards.filter(deleted_id__isnull=True).first()
                    if inst_sb_new:
                        inst_sb_new.deleted_id = uuid4()
                        inst_sb_new.deleted_since = timezone.now()
                        inst_sb_new.save()
            instance.deleted_id = None
            instance.deleted_since = None
            instance.save()
            return Response({"success": f"{instance} restored"})
        return Response(status=404)

    @action(methods=['DELETE'], url_path='clean', detail=False)
    def clean(self, request, *args, **kwargs):
        """
        Удаляет все файлы из корзины.
        """
        Project.objects.filter(deleted_id__isnull=False).filter(owner=request.user).delete()
        Storyboard.objects.filter(deleted_id__isnull=False).filter(owner=request.user).delete()
        Link.objects.filter(deleted_id__isnull=False).filter(owner=request.user).delete()
        File.objects.filter(deleted_id__isnull=False).filter(owner=request.user).delete()
        Text.objects.filter(deleted_id__isnull=False).filter(owner=request.user).delete()
        Timing.objects.filter(deleted_id__isnull=False).filter(owner=request.user).delete()
        Document.objects.filter(deleted_id__isnull=False).filter(owner=request.user).delete()
        Folder.objects.filter(deleted_id__isnull=False).filter(owner=request.user).delete()
        Poll.objects.filter(deleted_id__isnull=False).filter(owner=request.user).delete()
        self.change_disk_space(request.user)
        return Response({"success": "all data deleted from trash"}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], url_path='space', detail=False)
    def get_trash_space(self, request, *args, **kwargs):
        """
        Считает и отдает вес файлов в корзине.
        """
        storyboards = Storyboard.objects.filter(deleted_id__isnull=False).filter(owner=request.user).all()
        projects = Project.objects.filter(
            deleted_id__isnull=False).filter(
            owner=request.user).filter(
            logo__isnull=False).all()
        files = File.objects.filter(deleted_id__isnull=False).filter(owner=request.user).all()
        timings = Timing.objects.filter(deleted_id__isnull=False).filter(owner=request.user).all()
        documents = Document.objects.filter(deleted_id__isnull=False).filter(owner=request.user).all()

        trash_size = 0

        for file in files:
            trash_size += file.file.size

        for storyboard in storyboards:
            storyboard_size = count_space_per_object(request.user, storyboard, "storyboard")
            trash_size += storyboard_size

        for prj in projects:
            if prj.logo:
                trash_size += prj.logo.size

        for timing in timings:
            if timing.document_logo:
                trash_size += timing.document_logo.size

        for document in documents:
            if document.document_logo:
                trash_size += document.document_logo.size

        return Response({"trash_size": trash_size})
