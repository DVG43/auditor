from django.urls import path, include
from rest_framework_nested import routers

from common.views import UserColumnViewSet, UserCellViewSet, UserChoiceViewSet, \
    UsercellImageViewSet
from urls import router
from shootingplans.views import (
    ShootingplanViewSet,
    UnitViewSet,
    UnitframeViewSet
)

## projects/shootingplans/
pr_shootingplans_router = routers.NestedSimpleRouter(
    router, r'projects', lookup='project')
pr_shootingplans_router.register(r'shootingplans', ShootingplanViewSet)

# projects/shootingplans/units/
pr_shp_units_router = routers.NestedSimpleRouter(
    pr_shootingplans_router, r'shootingplans', lookup='shootingplan')
pr_shp_units_router.register(r'units', UnitViewSet, basename='unit')

# projects/shootingplans/units/frames/
pr_shp_un_frames_router = routers.NestedSimpleRouter(
    pr_shp_units_router, r'units', lookup='unit')
pr_shp_un_frames_router.register(
    r'frames', UnitframeViewSet, basename='unitframe')

# projects/shootingplans/units/frames/usercolumns/
pr_shp_un_frm_usercolumns_router = routers.NestedSimpleRouter(
    pr_shp_un_frames_router, r'frames', lookup='unitframe')
pr_shp_un_frm_usercolumns_router.register(
    r'usercolumns', UserColumnViewSet, basename='usercolumn')

# projects/shootingplans/units/frames/usercolumns/choices/
pr_shp_un_frm_uc_choices_router = routers.NestedSimpleRouter(
    pr_shp_un_frm_usercolumns_router, r'usercolumns', lookup='usercolumn')
pr_shp_un_frm_uc_choices_router.register(
    r'choices', UserChoiceViewSet, basename='userchoice')

# projects/shootingplans/units/frames/userfields/
pr_shp_un_frm_userfields_router = routers.NestedSimpleRouter(
    pr_shp_un_frames_router, r'frames', lookup='unitframe')
pr_shp_un_frm_userfields_router.register(
    r'userfields', UserCellViewSet, basename='usercell')

# projects/shootingplans/units/frames/userfields/images/
pr_shp_un_frm_uf_images_router = routers.NestedSimpleRouter(
    pr_shp_un_frm_userfields_router, r'userfields', lookup='usercell')
pr_shp_un_frm_uf_images_router.register(
    r'images', UsercellImageViewSet, basename='usercellimage')

urlpatterns = [
    path('', include(pr_shootingplans_router.urls)),

    path('', include(pr_shp_units_router.urls)),

    path('', include(pr_shp_un_frames_router.urls)),
    path('', include(pr_shp_un_frm_usercolumns_router.urls)),
    path('', include(pr_shp_un_frm_uc_choices_router.urls)),

    path('', include(pr_shp_un_frm_userfields_router.urls)),
    path('', include(pr_shp_un_frm_uf_images_router.urls)),
]
