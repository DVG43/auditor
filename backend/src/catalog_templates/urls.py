from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import SimpleRouter
from urls import router

from .views import (
    CategoryForTemplateViewSet,
    TemplateViewSet
)

## catalog_template/
catalog_templates_router = SimpleRouter()
catalog_templates_router.register(r'catalog_template', TemplateViewSet)
## catalog_template/tag
categories_router = routers.NestedSimpleRouter(catalog_templates_router, r'catalog_template', lookup='catalog_template')
categories_router.register(r'category', CategoryForTemplateViewSet, basename='category')



urlpatterns = [
    path('', include(catalog_templates_router.urls)),
    path('', include(categories_router.urls)),
]
