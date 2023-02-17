from accounts.permissions import IsActivated
from common.permissions import IsOwner, IsOwnerOrIsInvited
from django.shortcuts import get_object_or_404
from document.models import Document
from document.serializers import DocumentLogoSerializer, ProjectSerializer, DocumentSerializer
from rest_framework import generics, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from projects.models import Project
from settings import MEDIA_URL


class ChangeDocumentLogoView(generics.UpdateAPIView):
    serializer_class = DocumentLogoSerializer
    permission_classes = [IsAuthenticated, IsActivated, IsOwner]
    queryset = Document.objects.all()

    def patch(self, request, *args, **kwargs):
        document = get_object_or_404(Document, pk=kwargs['doc_pk'])
        if request.user != document.owner:
            raise PermissionDenied({'error': 'You don`t have access to this object'})
        document.document_logo = request.data['document_logo']
        document.save()
        resp = f"https://{request.META['HTTP_HOST']}" \
               f"{MEDIA_URL}" \
               f"{document.document_logo}"
        return Response(resp)


class DicumentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsActivated, IsOwnerOrIsInvited]

    def get_queryset(self):
        document = Document.objects.select_related('host_project').all()
        return document

    def get_serializer_class(self):
        return DocumentSerializer


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsActivated, IsOwnerOrIsInvited]

    def get_queryset(self):
        project = Project.objects.prefetch_related('documents').all()
        return project

    def get_serializer_class(self):
        return ProjectSerializer
