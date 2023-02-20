from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import SimpleRouter
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

from drf_spectacular.views import SpectacularJSONAPIView, SpectacularAPIView, \
    SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from accounts.views import SocialComplete, SocialDisconnect, ShareDocView, GetSharedDoc
from common.views import CalendarView, GetOpenGraphTagsView, StandardIconViewSet
from contacts.views import ContactViewSet, ContactSearchViewSet
from projects.views import ProjectViewSet
from trash.views import TrashViewSet
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

router = SimpleRouter()
router.register(r'contacts', ContactViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'trash', TrashViewSet)
router.register(r'icons', StandardIconViewSet)

urlpatterns = [
    path('api/v1/', include([
        path('schema/', SpectacularAPIView.as_view(api_version='v1'), name='schema'),
        path('schema_json/', SpectacularJSONAPIView.as_view(api_version='v1'), name='schema_json'),
        path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
        path('admin/', admin.site.urls),
        path('auth/', include('accounts.urls', namespace='accounts')),
        path('oauth/social-auth/', SocialComplete.as_view()),
        path('oauth/social-disconnect/', SocialDisconnect.as_view()),
        path('oauth/', include('social_django.urls', namespace='social')),
        path('calendar/<str:from>/<str:to>/', CalendarView.as_view()),
        path('url_opengraph/', GetOpenGraphTagsView.as_view()),
        path('', include(router.urls)),
        path('', include('projects.urls')),
        path('', include('contacts.urls')),
        path('', include('storyboards.urls')),
        # path('pay/', include('tinkoff_pay.urls')),
        path('', include('subscription.urls')),
        path('', include('document.urls')),
        path('', include('folders.urls')),
        path('document/share/', include([
            path('', ShareDocView.as_view({
                'post': 'create'}),
                 name='share_document'),
            path('<uuid:doc_uuid>/', ShareDocView.as_view({
                'delete': 'delete'}),
                 name='delete_share_document'),
            path('token/<uuid:doc_uuid>/',
                 GetSharedDoc.as_view({'get': 'retrieve'}),
                 name='get_shared_doc_token')])),
        path('contact/search/',
             ContactSearchViewSet.as_view({'post': 'search'}),
             name='search_for_contact'),
        path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    ])),
    path('api/v2/', include([
        path('schema/', SpectacularAPIView.as_view(api_version='v2'), name='schema', ),
        path('schema_json/', SpectacularJSONAPIView.as_view(), name='schema_json'),
        path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
]
# static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Kinomanager API",
#         default_version='v1',
#         # description="Test description",
#         # terms_of_service="https://www.google.com/policies/terms/",
#         contact=openapi.Contact(email="dmz55@ya.ru"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=[permissions.AllowAny],
# )

# urlpatterns += [
#     re_path(r'^api/v1/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
#             name='schema-json'),
#     re_path(r'^api/v1/swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
#             name='schema-swagger-ui'),
#     re_path(r'^api/v1/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
# ]
