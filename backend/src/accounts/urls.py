from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView

from accounts import views
# from accounts.views import SocialSignUp
from subscription.views import SubscriptionView, SubscriptionCancelView

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.UserViewSet.as_view({'post': 'create'}),
         name='signup_user'),
    path('login/', views.LoginView.as_view(),
         name='token_obtain_pair'),
    # path('login-with-social/', SocialSignUp.as_view()),
    path('login/refresh/', views.RefreshTokenView.as_view(),
         name='token_refresh'),
    path('login/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', views.LogoutView.as_view(),
         name='logout'),
    path('email/verify/', views.EmailVerifyView.as_view(), name="email_verify"),
    path('email/verify/resend/', views.ResendActivationCode.as_view(),
         name="email_verify_resend"),
    path('email/change/', views.ChangeEmail.as_view(), name="email_change"),
    path('email/change/confirm/', views.ChangeEmailConfirm.as_view(),
         name="email_change_confirm"),
    path('password/change/', views.ChangePasswordAPIView.as_view(),
         name="change_password"),
    path('password/reset/', views.ResetPasswordAPIView.as_view(),
         name="recover_password"),
    path('add_email/', views.AddEmailAfterOauthAPIView.as_view(),
             name="add_email"),
    path('add_email/confirm/', views.AddEmailAfterOauthConfirm.as_view(),
                 name="add_email_confirm"),

    path('profile/', include([
        path('', views.UserViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy'
        }), kwargs={'pk': 'me'}, name='user_me'),
        path('subs/', SubscriptionView.as_view()),
        path('subs/cancel/', SubscriptionCancelView.as_view()),
        path('likes/', views.LikeViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
        }), name='vote_for'),
        path('likes/document/', views.LikeViewSet.as_view({
                    'get': 'get_total_likes',
                    'patch': 'update_doc_like',
                }), name='vote_for_document'),
        path('likes/document/my/', views.LikeViewSet.as_view({
            'get': 'get_doc_like'
        }), name='my_vote_for_document')
    ])),

]
