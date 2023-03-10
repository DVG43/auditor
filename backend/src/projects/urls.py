from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import SimpleRouter

from common.views import UserColumnViewSet
from contacts.views import ContactViewSet
from projects.views import (
    LinkViewSet,
    TextViewSet,
    FileViewSet
)
from urls import router

## /projects/contacts/
pr_contacts_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
pr_contacts_router.register(r'contacts', ContactViewSet, basename='contact')
## links/
link_router = SimpleRouter()
link_router.register(r'link', LinkViewSet)
## links/
file_router = SimpleRouter()
file_router.register(r'file', FileViewSet)
## links/
text_router = SimpleRouter()
text_router.register(r'text', TextViewSet)
# /projects/contacts/usercolumns/
pr_cnt_userfields_router = routers.NestedSimpleRouter(pr_contacts_router, r'contacts', lookup='contact')
pr_cnt_userfields_router.register(r'usercolumns', UserColumnViewSet, basename='usercolumn')


urlpatterns = [
    path('', include(pr_contacts_router.urls)),
    path('', include(pr_cnt_userfields_router.urls)),
    path('', include(link_router.urls)),
    path('', include(file_router.urls)),
    path('', include(text_router.urls)),
]
