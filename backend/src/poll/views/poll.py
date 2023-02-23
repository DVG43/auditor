from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db.models import Q, Prefetch
from django.contrib.postgres.search import TrigramSimilarity
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
# from integration.models.telegram import TelegramIntegration, TelegramChats
from ..models.poll import Poll, PollSettings, PollTags
from ..models.questions import DivisionQuestion, ManyFromListQuestion, YesNoQuestion, TextQuestion, RatingQuestion, \
    MediaQuestion, ItemQuestion, FinalQuestion, HeadingQuestion, FreeAnswer, MediaAttachedType, MediaItemQuestion, \
    ItemsFreeAnswer
from ..paginations import PollPagination
from ..permissions import IsPollRedactor, IsPollOwner, IsPollOwnerDiskSpaceFree
from ..serializers.poll import PollSerializer, PollTagsSerializer, PollSettingsSerializer, PollListSerializer
from ..serializers.questions import ManyFromListQuestionSerializer, MediaQuestionSerializer

User = get_user_model()


class PollList(generics.ListAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Poll.objects.select_related('setting').prefetch_related('user_access'). \
            filter(Q(user_access__user=user) | Q(owner=user)).distinct().all()

    def list(self, request, *args, **kwargs):
        response = super(PollList, self).list(request, *args, **kwargs)
        return Response({'result': response.data})

    def get_serializer_context(self):
        return {'request': self.request}


class PollMinimumFieldList(generics.ListAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollListSerializer
    permission_classes = [IsPollOwner | IsAdminUser]
    pagination_class = PollPagination

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        user_pk = self.kwargs.get('pk')
        if user_pk:
            user = get_object_or_404(User, id=user_pk)
        else:
            user = self.request.user
        query = Q(user_access__user=user) | Q(owner=user)

        title = self.request.query_params.get('title', None)
        is_active = self.request.query_params.get('isFormActive', 'all')
        tags = self.request.query_params.get('tags', None)

        if is_active != 'all' and is_active in ['active', 'notActive']:
            is_active = 'active' == is_active or not 'notActive' == is_active
            query = query.add(Q(setting__isFormActive=is_active), Q.AND)
        if tags:
            tags = tags.split(',')
            query = query.add(Q(tags_list__name__in=tags), Q.AND)

        query = Poll.objects.distinct().select_related('setting').prefetch_related(
            'tags_list', 'user_access'
        ).filter(query)
        if title:
            query = query.annotate(similarity=TrigramSimilarity('title', title)) \
                .filter(similarity__gt=0.4).order_by('-similarity')
        return query


class PollCreate(generics.CreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]

    def get_serializer_context(self):
        return {'request': self.request}

    def post(self, request, *args, **kwargs):
        user_pk = self.kwargs.get('pk')
        if user_pk:
            user = get_object_or_404(User, pk=user_pk)
            request.data['user'] = user_pk
            request.user = user
        else:
            request.data['user'] = request.user.pk

        response = super(PollCreate, self).post(request, *args, **kwargs)
        poll_id = response.data['poll_id']
        return Response({'result': 'The poll has been created', 'poll_id': str(poll_id)},
                        status=HTTPStatus.OK)


# для страницы редактирования опросника,
# что бы пользователь не мог открыть страницу редактирования другого пользователя
class PollRetrieveEditPage(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [IsPollOwner | IsPollRedactor | IsAdminUser]

    def check_object_permissions(self, request, obj):
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                raise NotFound()

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({'result': [response.data]})


class PollCollection(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PollSerializer
    permission_classes = [IsPollOwner | IsPollRedactor | IsAdminUser]

    def get_queryset(self):
        queryset = Poll.objects.all().select_related(
            "owner",
            # "googlesheetintegration",
            # "telegramintegration",
        ).prefetch_related(
            Prefetch("manyfromlistquestion_set",
                     queryset=ManyFromListQuestion.objects.prefetch_related("items")),
            Prefetch("mediaquestion_set",
                     queryset=MediaQuestion.objects.prefetch_related("items", "attached_type")),
            Prefetch("freeanswer_set",
                     queryset=FreeAnswer.objects.prefetch_related(
                         "attached_type", "tags",
                         Prefetch("items",
                                  queryset=ItemsFreeAnswer.objects.prefetch_related("tags")))),
            Prefetch("yesnoquestion_set",
                     queryset=YesNoQuestion.objects.prefetch_related("attached_type", "items",
                                                                     "yes_no_answers")),
            Prefetch("finalquestion_set", queryset=FinalQuestion.objects.prefetch_related("items")),
        )
        return queryset

    def get_object(self):
        obj = super(PollCollection, self).get_object()
        if self.request.user == obj.owner:
            obj.last_open = timezone.now()
            obj.save()
        self.request.data['user'] = obj.owner.pk
        return obj

    def get_serializer_context(self):
        return {'request': self.request}

    def update(self, request, *args, **kwargs):
        response = super(PollCollection, self).update(request, *args, **kwargs)
        return Response({'result': response.data})

    def retrieve(self, request, *args, **kwargs):
        response = super(PollCollection, self).retrieve(request, *args, **kwargs)
        return Response({'result': [response.data]})

    def delete(self, request, *args, **kwargs):
        super(PollCollection, self).delete(request, *args, **kwargs)
        return Response({'result': 'The poll has been deleted'})


class DuplicatePoll(APIView):
    permission_classes = [IsPollOwner | IsPollRedactor | IsAdminUser, IsPollOwnerDiskSpaceFree]

    def get(self, request, pk, format=None):
        """
        Get poll
        """
        try:
            poll = Poll.objects.get(poll_id=pk)
            try:
                poll_setting = PollSettings.objects.get(poll=poll)
            except PollSettings.DoesNotExist:
                poll_setting = None

            # poll_tg_integration = TelegramIntegration.objects.filter(poll=poll).first()

            oldpk = pk
            poll.pk = None
            if not request.user.is_staff:
                poll.owner = request.user
            poll.title += ' (Копия)'
            poll.count_answers = 0
            poll.save()

            if poll_setting:
                poll_setting.pk = None
                poll_setting.poll_id = poll.pk
                poll_setting.save()

            # if poll_tg_integration:
            #     tg_chat = TelegramChats.objects.filter(bot=poll_tg_integration).first()
            #     tg_chat.pk = None
            #     poll_tg_integration.pk = None
            #     poll_tg_integration.poll_id = poll.pk
            #     poll_tg_integration.save()
            #     tg_chat.bot_id = poll_tg_integration.pk
            #     tg_chat.save()

            division = DivisionQuestion.objects.filter(poll_id=oldpk).all()
            for question in division:
                question.pk = None
                question.poll_id = poll.pk
                question.save()

            manyfromlist = ManyFromListQuestion.objects.filter(poll_id=oldpk).all()
            for question in manyfromlist:
                serialized_question = ManyFromListQuestionSerializer(question)
                question_items = serialized_question.data['items']
                question.pk = None
                question.poll_id = poll.pk
                question.save()

                for question_item in question_items:
                    del question_item['item_question_id']
                    question.items.add(ItemQuestion.objects.create(**question_item))

            yes_no_question = YesNoQuestion.objects.filter(poll_id=oldpk).all()
            for question in yes_no_question:
                yes_no_answers = question.yes_no_answers.all()
                question_items = question.items.all()
                question.pk = None
                question.poll_id = poll.pk
                question.save()

                for question_item in question_items:
                    question_item.pk = None
                    question_item.save()
                    question.items.add(question_item)

                for yes_no_answer in yes_no_answers:
                    yes_no_answer.pk = None
                    yes_no_answer.save()
                    question.yes_no_answers.add(yes_no_answer)

            text = TextQuestion.objects.filter(poll_id=oldpk).all()
            for question in text:
                question.pk = None
                question.poll_id = poll.pk
                question.save()

            rating = RatingQuestion.objects.filter(poll_id=oldpk).all()
            for question in rating:
                question.pk = None
                question.poll_id = poll.pk
                question.save()

            media = MediaQuestion.objects.filter(poll_id=oldpk).all()
            for question in media:
                serialized_question = MediaQuestionSerializer(question)
                question_items = serialized_question.data['items']
                question_attached_types = serialized_question.data['attached_type']
                question.pk = None
                question.poll_id = poll.pk
                question.save()

                for question_item in question_items:
                    del question_item['item_question_id']
                    question.items.add(MediaItemQuestion.objects.create(**question_item))

                for question_attached_type in question_attached_types:
                    del question_attached_type['media_attached_id']
                    question.attached_type.add(MediaAttachedType.objects.create(**question_attached_type))

            final = FinalQuestion.objects.filter(poll_id=oldpk).all()
            for question in final:
                question.pk = None
                question.poll_id = poll.pk
                question.save()

            heading = HeadingQuestion.objects.filter(poll_id=oldpk).all()
            for question in heading:
                question.pk = None
                question.poll_id = poll.pk
                question.save()

            free_answer = FreeAnswer.objects.filter(poll_id=oldpk).all()
            for question in free_answer:
                question_items = question.items.all()
                question.pk = None
                question.poll_id = poll.pk
                question.save()

                for question_item in question_items:
                    question_item.pk = None
                    question_item.save()
                    question.items.add(question_item)

        except Poll.DoesNotExist:
            return Response({'result': 'Not found'}, status=HTTPStatus.NOT_FOUND)
        return Response({'result': poll.pk}, status=HTTPStatus.OK)


class PollTagsCollection(APIView):
    permission_classes = [AllowAny | IsAdminUser]

    def get(self, request, pk, format=None):
        try:
            poll_tags = PollTags.objects.filter(poll=pk)
            serialized_tags = PollTagsSerializer(poll_tags, many=True)
        except Poll.DoesNotExist:
            return Response({'result': 'Not found'}, status=HTTPStatus.NOT_FOUND)

        return Response({'result': serialized_tags.data}, status=HTTPStatus.OK)

    def post(self, request, pk):
        try:
            for poll in request.data['polls']:
                get_poll = Poll.objects.get(poll_id=poll)
                for tag in request.data['tags']:
                    serialized_tag = PollTagsSerializer(tag)

                    if not serialized_tag.data['name'] in str(get_poll.tags_list.values_list('name')):
                        get_poll.tags_list.get_or_create(name=tag['name'])
        except Exception as ex:
            return Response({'error': f'{ex}'}, status=HTTPStatus.BAD_REQUEST)
        return Response({'result': 'Ok'}, status=HTTPStatus.OK)

    def delete(self, request):
        try:
            for poll in request.data['polls']:
                get_poll = Poll.objects.get(poll_id=poll)
                for tag in request.data['tags']:
                    serialized_tag = PollTagsSerializer(tag)
                    if serialized_tag.data['name'] in str(get_poll.tags_list.values_list('name')):
                        tag_for_delete = PollTags.objects.get(poll=poll, name=tag['name'])
                        get_poll.tags_list.remove(tag_for_delete)

        except Exception as ex:
            return Response({'error': f'{ex}'}, status=HTTPStatus.BAD_REQUEST)
        return Response({'result': 'Ok'}, status=HTTPStatus.OK)


class PollSettingUpdateView(generics.RetrieveUpdateAPIView):
    queryset = PollSettings.objects.all()
    serializer_class = PollSettingsSerializer
    permission_classes = [AllowAny | IsAdminUser]

    def get_object(self):
        poll_id = self.kwargs.get('pk')
        instance = get_object_or_404(self.queryset, poll_id=poll_id)
        if all([self.request.user != instance.poll.owner, not self.request.user.is_staff]):
            raise PermissionDenied()
        return instance
