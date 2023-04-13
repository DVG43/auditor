from django.shortcuts import render

# Create your views here.
from .models import Template, CategoryForTemplate
from rest_framework.viewsets import ModelViewSet
from .serializers import CategoryForTemplateSerializer, TemplateSerializer #, CreateTemplateSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class CategoryForTemplateViewSet(ModelViewSet):
    queryset = CategoryForTemplate.objects.prefetch_related(
        'templates')
    http_method_names = ['get']
    pagination_class = StandardResultsSetPagination
    serializer_class = CategoryForTemplateSerializer
    permission_classes = [IsAuthenticated]
    #serializer_class = CreateTemplateSerializer

    def get_queryset(self):
        instance = CategoryForTemplate.objects.filter(templates__pk=self.kwargs.get('catalog_template_pk'))
        return instance


class TemplateViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    queryset = Template.objects.prefetch_related(
        'categories')
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        if request.data.get("favourite") == 'false':
            request.data['favourite'] = ''
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        self.queryset = Template.objects.filter(Q(owner=user) | Q(is_common=True))\
            .prefetch_related('categories').select_related('owner')

        return self.queryset

    def perform_create(self, serializer):
        save_kw = {}
        # получаем связанные категории
        if self.request.data.get("categories_input"):
            categories = CategoryForTemplate.objects.filter(pk__in=self.request.data.get("categories_input"))
            save_kw.update({"categories": categories})
        else:
            pass

        # добавляем в избранные
        if self.request.data.get("favourite") == True or self.request.data.get("favourite") == 'true':
            favourite = [self.request.user]
            save_kw.update({"favourite": favourite})
        else:
            pass
        save_kw.update({"last_modified_user": self.request.user.email, "owner": self.request.user})
        serializer.save(**save_kw)

    def perform_update(self, serializer):
        save_kw = {}
        # получаем связанные категории
        if self.request.data.get("categories_input"):
            categories = CategoryForTemplate.objects.filter(pk__in=self.request.data.get("categories_input"))
            save_kw.update({"categories": categories})
        else:
            pass

        # проевряем есть ли в избранных и добавляем в словарь
        if self.request.data.get("favourite") == True or self.request.data.get("favourite") == 'true':
            favourite = [self.request.user]
            save_kw.update({"favourite": favourite})
        elif self.request.data.get("favourite") == False or self.request.data.get("favourite") == 'false':
            save_kw.update({"favourite": []})
        else:
            pass
        save_kw.update({"last_modified_user": self.request.user.email})
        serializer.save(**save_kw)

    def get_serializer_class(self):
        return TemplateSerializer

