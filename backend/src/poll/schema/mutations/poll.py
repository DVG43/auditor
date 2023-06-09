import uuid

import graphene
from django.utils import timezone
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required

from graphql_utils.permissions import PermissionClass
from folders.models import Folder
from poll.models import (
    poll as poll_models,
    questions as qstn_models,
)
from poll.schema import types
from poll.serializers import (
    poll as poll_serializers,
)
from poll.utils import QUESTION_MODELS


class CreatePoll(SerializerMutation):
    """
    Create Poll (Check list)
    """

    class Meta:
        serializer_class = poll_serializers.PollSerializer
        model_operations = ['create']
        lookup_field = 'id'
        model_class = poll_models.Poll

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)

        if "folder" in input:
            folder = Folder.objects.filter(pk=input["folder"]).first()
            PermissionClass.has_mutate_object_permission(info, folder)
        else:
            folder = None

        input.update({'owner': info.context.user,
                      'last_modified_user': info.context.user.email,
                      'folder': folder})

        poll = poll_serializers.PollSerializer.create(
            poll_serializers.PollSerializer(),
            validated_data=input
        )

        cls.generate_base_structure(poll)

        return poll

    @staticmethod
    def generate_base_structure(poll):
        """
        Creates base page and section with possible questions
        """

        base_page = qstn_models.PageQuestion.objects.create(poll=poll, order_id=1, caption="Заглавная страница")

        data = {
            "poll": poll,
            "parent_id": base_page.page_id
        }

        item_sets = []

        item_texts_set = (("Да", "Нет", "Н/Д"), ("Хороший", "Плохой", "Н/Д"), ("Удача", "Неудача", "Н/Д"),
                          ("Соответствует", "Не соответствует", "Н/Д"))
        default_colors = ("#46875E", "#C50056", "#6A6A6A")

        for item_texts in item_texts_set:
            set_obj = qstn_models.ItemSet.objects.create(poll=poll)
            item_sets.append(set_obj)
            for i, text in enumerate(item_texts):
                qstn_models.ItemQuestion.objects.create(item_set=set_obj, text=text, order_id=i + 1,
                                                        hex_color=default_colors[i])

        qstn_models.DateQuestion.objects.create(caption="Дата и время", order_id=1, **data)
        qstn_models.TextQuestion.objects.create(caption="Введите вопрос", order_id=2, **data)
        qstn_models.NumberQuestion.objects.create(caption="Число", order_id=3, **data)
        qstn_models.CheckQuestion.objects.create(caption="Чек бокс", order_id=4, **data)
        qstn_models.ManyFromListQuestion.objects.create(caption="Выбор ответов", order_id=5,
                                                        item_set=item_sets[0],
                                                        **data)


class UpdatePollInput(graphene.InputObjectType):
    name = graphene.String(required=False)
    use_points = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    folder = graphene.ID(required=False)
    image = graphene.String(required=False)
    tag_color = graphene.String(required=False)
    test_mode_global = graphene.Boolean(required=False)
    count_answers = graphene.Int(required=False)


class UpdatePoll(graphene.Mutation):
    """
    Update Poll (Check list) by poll_id
    """

    class Arguments:
        # The input arguments for this mutation
        poll_id = graphene.ID(required=True)
        poll_input = UpdatePollInput()

    ok = graphene.Boolean()
    poll = graphene.Field(types.PollType)

    @staticmethod
    @login_required
    def mutate(cls, info, poll_id, **input):
        PermissionClass.has_permission(info)

        poll = poll_models.Poll.objects.filter(id=poll_id)
        if poll:

            PermissionClass.has_mutate_object_permission(info, poll.first())
            poll.update(**input['poll_input'])

            return UpdatePoll(ok=True, poll=poll.first())
        else:
            return UpdatePoll(ok=False)


class UpdatePollSettingInput(graphene.InputObjectType):
    isFormActive = graphene.Boolean(required=False)
    mixQuestions = graphene.Boolean(required=False)
    allowRefillingForm = graphene.Boolean(required=False)
    groupsForRefilling = graphene.JSONString(required=False)
    groupsForOnlyOneFilling = graphene.JSONString(required=False)
    usePassword = graphene.Boolean(required=False)
    formPassword = graphene.String(required=False)
    useAnswersCountRestriction = graphene.Boolean(required=False)
    maxAnswers = graphene.String(required=False)
    useAnswersTimeRestriction = graphene.String(required=False)
    maxTimeRange = graphene.JSONString(required=False)
    isRedirectActive = graphene.Boolean(required=False)
    redirectMethod = graphene.String(required=False)
    redirectPath = graphene.String(required=False)
    askLocation = graphene.Boolean(required=False)
    activeCaptcha = graphene.Boolean(required=False)
    useSignature = graphene.Boolean(required=False)
    reopenForm = graphene.Boolean(required=False)
    reopenDelay = graphene.String(required=False)
    formInactiveMessage = graphene.String(required=False)
    language = graphene.String(required=False)
    externalapi = graphene.String(required=False)
    externalapiparams = graphene.String(required=False)


class UpdatePollSetting(graphene.Mutation):
    """
    Update Poll (Check list) settings by poll_id
    """

    class Arguments:
        # The input arguments for this mutation
        poll_id = graphene.ID(required=True)
        poll_set_input = UpdatePollSettingInput()

    ok = graphene.Boolean()
    poll_setting = graphene.Field(types.PollSettingsType)

    @staticmethod
    @login_required
    def mutate(cls, info, poll_id, **input):
        PermissionClass.has_permission(info)

        poll_setting = poll_models.PollSettings.objects.filter(poll_id=poll_id)
        if poll_setting:

            PermissionClass.has_mutate_object_permission(info, poll_setting.poll)
            poll_setting.update(**input['poll_set_input'])

            return UpdatePollSetting(ok=True, poll_setting=poll_setting.first())
        else:
            return UpdatePollSetting(ok=False)


class DeletePoll(graphene.Mutation):
    """
    Delete Poll (Check list) settings by poll_id
    """

    class Arguments:
        # The input arguments for this mutation
        poll_id = graphene.ID()

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, info, poll_id):
        poll = poll_models.Poll.objects.filter(id=poll_id).first()

        PermissionClass.has_permission(info)
        if poll:
            PermissionClass.has_mutate_object_permission(info, poll)

            poll.deleted_id = uuid.uuid4()
            poll.deleted_since = timezone.now()
            poll.save()

            return DeletePoll(ok=True)
        else:
            return DeletePoll(ok=False)


class CreatePollTagInput(graphene.InputObjectType):
    name = graphene.String(required=False)


class CreatePollTag(graphene.Mutation):
    """
    MultiCreate Poll (Check list) Tag settings by poll_id
    """

    class Arguments:
        # The input arguments for this mutation
        polls = graphene.List(graphene.Int)
        tags = graphene.List(CreatePollTagInput)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, info, polls, tags):
        PermissionClass.has_permission(info)

        try:
            for poll in polls:
                get_poll = poll_models.Poll.objects.get(id=poll)
                PermissionClass.has_mutate_object_permission(info, get_poll)
                for tag in tags:
                    serialized_tag = poll_serializers.PollTagsSerializer(tag)

                    if not serialized_tag.data['name'] in str(get_poll.tags_list.values_list('name')):
                        get_poll.tags_list.get_or_create(name=tag['name'])
        except Exception as ex:
            return {'error': f'{ex}'}
        return CreatePollTag(ok=True)


class OpenAccessPollTemplate(graphene.Mutation):
    """
    open access Poll template by poll_id
    """

    class Arguments:
        poll_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    url = graphene.String()

    @staticmethod
    @login_required
    def mutate(cls, info, poll_id):
        poll = poll_models.Poll.objects.filter(id=poll_id).first()

        PermissionClass.has_permission(info)
        if poll:
            PermissionClass.has_mutate_object_permission(info, poll)
            url_uuid = ""
            if poll.template_uuid:
                url_uuid = poll.template_uuid
            else:
                url_uuid = uuid.uuid4()
                poll.template_uuid = url_uuid
                poll.save()

            return OpenAccessPollTemplate(ok=True,
                                          url=info.context.META['HTTP_HOST'] + "/api/v1/poll/poll_templates/" + str(
                                              url_uuid))
        else:
            return OpenAccessPollTemplate(ok=False, url=None)


class CloseAccessPollTemplate(graphene.Mutation):
    """
    close access Poll template by poll_id
    """

    class Arguments:
        poll_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, info, poll_id):
        poll = poll_models.Poll.objects.filter(id=poll_id).first()

        PermissionClass.has_permission(info)
        if poll:
            PermissionClass.has_mutate_object_permission(info, poll)

            poll.template_uuid = None
            poll.save()

            return CloseAccessPollTemplate(ok=True)
        else:
            return CloseAccessPollTemplate(ok=False)


class PollMutation(graphene.ObjectType):
    create_poll = CreatePoll.Field()
    update_poll = UpdatePoll.Field()
    update_poll_setting = UpdatePollSetting.Field()
    delete_poll = DeletePoll.Field()
    create_poll_tag = CreatePollTag.Field()
    open_access_poll_template = OpenAccessPollTemplate.Field()
    close_access_poll_template = CloseAccessPollTemplate.Field()
