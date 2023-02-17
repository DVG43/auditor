from django.urls import path, include
from rest_framework_nested import routers

from callsheets.views import (
    CallsheetViewSet,
    LocationViewSet,
    CallsheetLogoViewSet,
    LocationMapViewSet,
    CallsheetmemberViewSet
)
from common.views import UserColumnViewSet
from contacts.views import ContactViewSet
from urls import router

# /projects/callsheets/
pr_callsheets_router = routers.NestedSimpleRouter(router, r'projects',
                                                  lookup='project')
pr_callsheets_router.register(r'callsheets', CallsheetViewSet,
                              basename='callsheet')
# /projects/callsheets/members/
pr_cs_callsheetmembers_router = routers.NestedSimpleRouter(
    pr_callsheets_router, r'callsheets', lookup='callsheet')
pr_cs_callsheetmembers_router.register(
    r'members', CallsheetmemberViewSet, basename='callsheetmember')
# /projects/callsheets/members/usercolumns/
pr_cs_mbr_userfields_router = routers.NestedSimpleRouter(
    pr_cs_callsheetmembers_router, r'members', lookup='callsheetmember')
pr_cs_mbr_userfields_router.register(
    r'usercolumns', UserColumnViewSet, basename='usercolumn')

# /projects/callsheets/locations/
pr_cs_locations_router = routers.NestedSimpleRouter(pr_callsheets_router,
                                                    r'callsheets',
                                                    lookup='callsheet')
pr_cs_locations_router.register(r'locations', LocationViewSet,
                                basename='location')

# /projects/callsheets/locations/maps
pr_cs_loc_maps_router = routers.NestedSimpleRouter(pr_cs_locations_router,
                                                    r'locations',
                                                    lookup='location')
pr_cs_loc_maps_router.register(r'maps', LocationMapViewSet,
                               basename='locationmap')

# /projects/callsheets/locations/usercolumns/
pr_cs_loc_userfields_router = routers.NestedSimpleRouter(pr_cs_locations_router,
                                                         r'locations',
                                                         lookup='location')
pr_cs_loc_userfields_router.register(r'usercolumns', UserColumnViewSet,
                                     basename='usercolumn')

# /projects/callsheets/usercolumns/
pr_cs_userfields_router = routers.NestedSimpleRouter(pr_callsheets_router,
                                                     r'callsheets',
                                                     lookup='callsheet')
pr_cs_userfields_router.register(r'usercolumns', UserColumnViewSet,
                                 basename='usercolumn')

# /projects/callsheets/logos/
pr_cs_logos_router = routers.NestedSimpleRouter(pr_callsheets_router, r'callsheets', lookup='callsheet')
pr_cs_logos_router.register(r'logos', CallsheetLogoViewSet,
                            basename='callsheetlogo')

urlpatterns = [
    path('', include(pr_callsheets_router.urls)),
    path('', include(pr_cs_callsheetmembers_router.urls)),
    path('', include(pr_cs_mbr_userfields_router.urls)),
    path('', include(pr_cs_locations_router.urls)),
    path('', include(pr_cs_loc_maps_router.urls)),
    path('', include(pr_cs_userfields_router.urls)),
    path('', include(pr_cs_loc_userfields_router.urls)),
    path('', include(pr_cs_logos_router.urls)),

    # path('', include(.urls)),

]
