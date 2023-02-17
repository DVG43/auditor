from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import CreateMovieAPIView, GetCreatedVideoAPIView, \
    SaveAudioForBordomatic, BordomaticPrivateViewSet, \
    DeleteAudioFromFileAPIView, UpdateImageForBordomatic, UpdateAudioForBordomatic
# SaveImageForBordomatic, BordomaticViewSet, GetBordomaticAPIView    #

router = SimpleRouter()
# router.register('bordomatic', BordomaticViewSet)
router.register('bordomatic', BordomaticPrivateViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('create_movie/', CreateMovieAPIView.as_view(), name='create_movie'),
    path('save_audio/', SaveAudioForBordomatic.as_view(), name='save_audio'),
    path('update_audio/<int:id>/', UpdateAudioForBordomatic.as_view(), name='update_image'),
    path('update_image/<int:id>/', UpdateImageForBordomatic.as_view(), name='update_image'),

    path('get_movie/', GetCreatedVideoAPIView.as_view(), name='get_movie'),
    # path('get_bordomatic/<int:storyboard_id>/', GetBordomaticAPIView.as_view(), name='get_bordomatic'),

    path('delete_audio/', DeleteAudioFromFileAPIView.as_view(), name='delete_audio'),

]
