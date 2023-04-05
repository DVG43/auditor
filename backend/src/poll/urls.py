from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

# from integration.views.telegram import TelegramIntegrationView, \
#     IntegrationView
from poll.views.answers import UserAnswerCollectionSet, \
    UserAnswerBySurveyCollectionSet
from poll.views.items_question import ItemQuestionCollection, \
    MediaItemQuestionCollection, YesNoItemCollection, FreeAnswerItemCollection
from poll.views.poll import PollCollection, DuplicatePoll, \
    PollTagsCollection, PollSettingUpdateView, PollList, PollCreate, PollMinimumFieldList, PollRetrieveEditPage
from poll.views.questions import QuestionCollection, YesNoAnswersView, \
    ManyFromListQuestionCaptionView, YesNoAnswersCreateAPIView, TagFreeAnswer, ItemTagFreeAnswer
from poll.views.surveypassing import SurveyPassingCollectionSet, \
    SurveyIdPassingCollectionSet, SurveyPassingMultipleDelete
from poll.views.user_access import UserAccessView, TransferAccess
from poll.views.polltheme import PollThemeViewSet, PollThemeListView, PollThemeActiveRetrieveView, \
    PollThemeActiveListView
from poll.views.analitics import PollAnaliticsViewSet
from poll.views_v2.sub_question_view import ItemViewSet, ItemCreateViewSet, AttachedTypeCreateViewSet, AttachedTypeViewSet
from poll.views_v2.poll import PollViewSet
from poll.views_v2.questions import QuestionViewSet, QuestionCreateView

from poll.views.poll_templates import my_view


router = DefaultRouter()
router.register('poll-theme', PollThemeViewSet)
analitics_router = DefaultRouter()
analitics_router.register('pollanalitics',PollAnaliticsViewSet,'pollanalitics')

poll_endpoints = [
    # path('api-auth/', include('rest_framework.urls')),
    # Poll
    path('', PollCreate.as_view()),
    path('my/', PollList.as_view()),
    path('my/list/', PollMinimumFieldList.as_view()),
    path('poll/<int:pk>/', PollCollection.as_view()),
    path('poll/<int:pk>/edit/', PollRetrieveEditPage.as_view()),
    path('poll/clone/<int:pk>/', DuplicatePoll.as_view()),
    path('poll/<int:pk>/tags/', PollTagsCollection.as_view()),
    path('poll/tags/', PollTagsCollection.as_view()),
    path('poll/<int:pk>/setting/', PollSettingUpdateView.as_view()),
    path('poll/<int:pk>/user-access/', UserAccessView.as_view()),
    path('poll/<int:pk>/transfer-access/', TransferAccess.as_view()),

    # # Integration
    # path('<int:poll_id>/integration/', IntegrationView.as_view()),
    # path('<int:poll_id>/integration/telegram/', TelegramIntegrationView.as_view()),

    # Answers
    path('answers/', UserAnswerCollectionSet.as_view()),
    path('<int:pk>/answers/', UserAnswerCollectionSet.as_view()),
    path('sp/<int:pk>/answers/', UserAnswerBySurveyCollectionSet.as_view()),

    # Questions
    path('<int:pk>/questions/', QuestionCollection.as_view()),
    path('questions/<int:pk>/<str:question_type>/', QuestionCollection.as_view()),
    path('<int:pk>/questions/captions/', ManyFromListQuestionCaptionView.as_view()),

    # Items
    path('questions/items/<int:pk>/', ItemQuestionCollection.as_view()),
    path('questions/free_answer_items/<int:pk>/', FreeAnswerItemCollection.as_view()),
    path('questions/free_answer_tags/<int:pk>/', TagFreeAnswer.as_view()),
    path('questions/free_answer_item_tags/<int:pk>/', ItemTagFreeAnswer.as_view()),
    path('questions/yesnoitems/<int:pk>/', YesNoItemCollection.as_view()),
    path('questions/mediaitems/<int:pk>/', MediaItemQuestionCollection.as_view()),

    path('sp/', SurveyPassingCollectionSet.as_view()),
    path('sp/<int:pk>/', SurveyPassingCollectionSet.as_view()),
    path('sp/survey/<int:pk>/', SurveyIdPassingCollectionSet.as_view()),
    path('sp/multiple-delete/', SurveyPassingMultipleDelete.as_view()),

    # YesNoAnswersView
    path('questions/YesNoAnswers/', YesNoAnswersCreateAPIView.as_view()),
    path('questions/YesNoAnswers/<int:pk>/', YesNoAnswersView.as_view()),

    # poll theme
    path('poll/', include(router.urls)),
    path('poll/poll-theme-list/', PollThemeListView.as_view()),
    path('poll/<int:pk>/poll-theme-active/', PollThemeActiveRetrieveView.as_view()),
    path('poll/<int:pk>/poll-theme-active/list/', PollThemeActiveListView.as_view()),

    # for Staff

    path('user/<int:pk>/list/', PollMinimumFieldList.as_view()),
    path('user/<int:pk>/poll_create/', PollCreate.as_view()),

    # templates
    path('poll_templates/<uuid:templ_uuid>/', my_view, name='templates'),

]


endpoints_v2 = [
    path('poll/',  PollViewSet.as_view()),
    path('poll/<int:pk>/',  PollViewSet.as_view()),

    path('poll/<int:pk>/question/', QuestionCreateView.as_view()),
    path('question/<int:pk>/<str:question_type>/', QuestionViewSet.as_view()),

    path('question/<int:pk>/<str:question_type>/items/', ItemCreateViewSet.as_view()),
    path('item/<int:pk>/<str:question_type>/', ItemViewSet.as_view()),

    path('question/<int:pk>/<str:question_type>/attached_type/', AttachedTypeCreateViewSet.as_view()),
    path('attached_type/<int:pk>/<str:question_type>/', AttachedTypeViewSet.as_view()),
]

urlpatterns = [
    path('poll/graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
