from django.urls import path, include
from rest_framework_nested import routers

from common.views import UserColumnViewSet
from contacts.views import ContactViewSet
from projects.views import LinkViewSet, TextViewSet
from projects.views import FileViewSet
from urls import router

## /projects/contacts/
pr_contacts_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
pr_contacts_router.register(r'contacts', ContactViewSet, basename='contact')
## /projects/links/
pr_links_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
pr_links_router.register(r'links', LinkViewSet, basename='link')
## /projects/files/
pr_files_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
pr_files_router.register(r'files', FileViewSet, basename='file')
## /projects/texts/
pr_texts_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
pr_texts_router.register(r'texts', TextViewSet, basename='text')
# /projects/contacts/usercolumns/
pr_cnt_userfields_router = routers.NestedSimpleRouter(pr_contacts_router, r'contacts', lookup='contact')
pr_cnt_userfields_router.register(r'usercolumns', UserColumnViewSet, basename='usercolumn')

urlpatterns = [
    path('', include(pr_contacts_router.urls)),
    path('', include(pr_cnt_userfields_router.urls)),
    path('', include(pr_links_router.urls)),
    path('', include(pr_files_router.urls)),
    path('', include(pr_texts_router.urls)),
]
