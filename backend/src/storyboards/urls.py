from django.urls import path, include
from rest_framework_nested import routers

from common.views import UserColumnViewSet, UserCellViewSet, \
    UsercellImageViewSet, UserChoiceViewSet
from storyboards.views import (
    StoryboardViewSet,
    FrameViewSet,
    ChronoViewSet,
    ShotViewSet,
    ChronoFrameViewSet,
)
from urls import router

# projects/storyboards/
pr_storyboards_router = routers.NestedSimpleRouter(
    router, r'projects', lookup='project')
pr_storyboards_router.register(r'storyboards', StoryboardViewSet)

# projects/storyboards/frames/
pr_sbd_frames_router = routers.NestedSimpleRouter(
    pr_storyboards_router, r'storyboards', lookup='storyboard')
pr_sbd_frames_router.register(r'frames', FrameViewSet, basename='frame')

# projects/storyboards/frames/shots
pr_sbd_frm_shots_router = routers.NestedSimpleRouter(
    pr_sbd_frames_router, r'frames', lookup='frame')
pr_sbd_frm_shots_router.register(r'shots', ShotViewSet, basename='shot')

# projects/storyboards/frames/usercolumns/
pr_sbd_frm_usercolumn_router = routers.NestedSimpleRouter(
    pr_sbd_frames_router, r'frames', lookup='frame')
pr_sbd_frm_usercolumn_router.register(
    r'usercolumns', UserColumnViewSet, basename='usercolumn')

# projects/storyboards/frames/usercolumns/choices/
pr_sbd_frm_uc_choices_router = routers.NestedSimpleRouter(
    pr_sbd_frm_usercolumn_router, r'usercolumns', lookup='usercolumn')
pr_sbd_frm_uc_choices_router.register(
    r'choices', UserChoiceViewSet, basename='userchoice')

# projects/storyboards/frames/userfields/
pr_sbd_frm_userfields_router = routers.NestedSimpleRouter(
    pr_sbd_frames_router, r'frames', lookup='frame')
pr_sbd_frm_userfields_router.register(
    r'userfields', UserCellViewSet, basename='usercell')

# projects/storyboards/frames/userfields/images/
pr_sbd_frm_uf_images_router = routers.NestedSimpleRouter(
    pr_sbd_frm_userfields_router, r'userfields', lookup='usercell')
pr_sbd_frm_uf_images_router.register(
    r'images', UsercellImageViewSet, basename='usercellimage')

# projects/storyboards/chronos/
pr_sbd_chronos_router = routers.NestedSimpleRouter(
    pr_storyboards_router, r'storyboards', lookup='storyboard')
pr_sbd_chronos_router.register(r'chronos', ChronoViewSet)

# projects/storyboards/chronos/frames/
pr_sbd_chr_frames_router = routers.NestedSimpleRouter(
    pr_sbd_chronos_router, r'chronos', lookup='chrono')
pr_sbd_chr_frames_router.register(
    r'frames', ChronoFrameViewSet, basename='chronoframe')

urlpatterns = [
    path('', include(pr_storyboards_router.urls)),

    path('', include(pr_sbd_frames_router.urls)),
    path('', include(pr_sbd_frm_shots_router.urls)),

    path('', include(pr_sbd_frm_usercolumn_router.urls)),
    path('', include(pr_sbd_frm_uc_choices_router.urls)),

    path('', include(pr_sbd_frm_userfields_router.urls)),
    path('', include(pr_sbd_frm_uf_images_router.urls)),

    path('', include(pr_sbd_chronos_router.urls)),
    path('', include(pr_sbd_chr_frames_router.urls)),
]
