from django.urls import path, include
from rest_framework_nested import routers
from common.views import UserColumnViewSet
from contacts.views import (
    PositionViewSet,
    DepartmentViewSet,
    ContactsDeleteListView,
    ContactViewSet
)
from urls import router

# # /contacts/usercolumns/
# cnt_userfields_router = routers.NestedSimpleRouter(router, r'contacts', lookup='contact')
# cnt_userfields_router.register(r'usercolumns', UserColumnViewSet, basename='usercolumn')

# /contacts/positions/
cnt_positions_router = routers.NestedSimpleRouter(
    router, r'contacts', lookup='contact')
cnt_positions_router.register(
    r'positions', PositionViewSet, basename='position')

# /contacts/deparments/
cnt_departments_router = routers.NestedSimpleRouter(
    router, r'contacts', lookup='contact')
cnt_departments_router.register(
    r'departments', DepartmentViewSet, basename='department')


urlpatterns = [
    # path('', include(cnt_userfields_router.urls)),
    path('contact/delete_list/', ContactsDeleteListView.as_view()),
    path('', include(cnt_positions_router.urls)),
    path('', include(cnt_departments_router.urls)),
]

router.register(r'positions', PositionViewSet)
router.register(r'departments', DepartmentViewSet)
