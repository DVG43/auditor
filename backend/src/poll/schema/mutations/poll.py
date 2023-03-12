import uuid

import graphene
from django.utils import timezone
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required

from graphql_utils.utils_graphql import PermissionClass
# from projects.models import Project
from folders.models import Folder
from poll.models import (
    poll as poll_models,
    questions as qstn_models,
)
from poll.schema import types
from poll.serializers import (
    poll as poll_serializers,
    questions as qstn_serializers,
)


class CreatePoll(SerializerMutation):
    class Meta:
        serializer_class = poll_serializers.PollSerializer
        model_operations = ['create']
        lookup_field = 'id'
        model_class = poll_models.Poll

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        # PermissionClass.has_mutate_object_permission(info, prj_id)

        # host_project = Project.objects.filter(pk=prj_id).first()
        if "folder" in input:
            folder = Folder.objects.filter(pk=input["folder"]).first()
        else:
            folder = None
        input.update({'owner': info.context.user,
                      'last_modified_user': info.context.user.email,
                      'folder': folder})

        poll = poll_serializers.PollSerializer.create(
            poll_serializers.PollSerializer(),
            validated_data=input
        )

        return poll


class UpdatePollInput(graphene.InputObjectType):
    name = graphene.String(required=False)
    description = graphene.String(required=False)
    folder = graphene.ID(required=False)
    image = graphene.String(required=False)
    tag_color = graphene.String(required=False)
    test_mode_global = graphene.Boolean(required=False)
    count_answers = graphene.Int(required=False)


class UpdatePoll(graphene.Mutation):
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

            # PermissionClass.has_mutate_object_permission(info, prj_id)
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

            # PermissionClass.has_mutate_object_permission(info, prj_id)
            poll_setting.update(**input['poll_set_input'])

            return UpdatePollSetting(ok=True, poll_setting=poll_setting.first())
        else:
            return UpdatePollSetting(ok=False)


class DeletePoll(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        poll_id = graphene.ID()

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, root, poll_id):
        poll = poll_models.Poll.objects.filter(id=poll_id).first()

        PermissionClass.has_permission(root)
        if poll:
            # prj_id = poll.host_project.id
            # PermissionClass.has_mutate_object_permission(root, prj_id)

            poll.deleted_id = uuid.uuid4()
            poll.deleted_since = timezone.now()

            poll.save()
            return DeletePoll(ok=True)
        else:
            return DeletePoll(ok=False)


class CreatePollTagInput(graphene.InputObjectType):
    name = graphene.String(required=False)


class CreatePollTag(graphene.Mutation):
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
                prj_id = get_poll.host_project.id

                PermissionClass.has_mutate_object_permission(info, prj_id)
                for tag in tags:
                    serialized_tag = poll_serializers.PollTagsSerializer(tag)

                    if not serialized_tag.data['name'] in str(get_poll.tags_list.values_list('name')):
                        get_poll.tags_list.get_or_create(name=tag['name'])
        except Exception as ex:
            return {'error': f'{ex}'}
        return CreatePollTag(ok=True)


class AllPollQuestions(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        poll_id = graphene.ID(required=True)

    division_questions = graphene.List(types.DivisionQuestionType)
    yesno_questions = graphene.List(types.YesNoQuestionType)
    manyfromlist_questions = graphene.List(types.ManyFromListQuestionType)
    text_questions = graphene.List(types.TextQuestionType)
    media_questions = graphene.List(types.MediaQuestionType)
    final_questions = graphene.List(types.FinalQuestionType)
    heading_question = graphene.List(types.HeadingQuestionType)
    free_answer_question = graphene.List(types.FreeAnswerType)

    @staticmethod
    @login_required
    def mutate(cls, info, poll_id, **input):

        PermissionClass.has_permission(info)

        division = qstn_models.DivisionQuestion.objects.filter(poll_id=poll_id).all()
        yes_no = qstn_models.YesNoQuestion.objects.filter(poll_id=poll_id).all()
        manyfromlist = qstn_models.ManyFromListQuestion.objects.filter(poll_id=poll_id).all()
        text = qstn_models.TextQuestion.objects.filter(poll_id=poll_id).all()
        media = qstn_models.MediaQuestion.objects.filter(poll_id=poll_id).all()
        final = qstn_models.FinalQuestion.objects.filter(poll_id=poll_id).all()
        heading = qstn_models.HeadingQuestion.objects.filter(poll_id=poll_id).all()
        free_answer = qstn_models.FreeAnswer.objects.filter(poll_id=poll_id).all()

        return AllPollQuestions(
            division_questions=division,
            yesno_questions=yes_no,
            manyfromlist_questions=manyfromlist,
            text_questions=text,
            media_questions=media,
            final_questions=final,
            heading_question=heading,
            free_answer_question=free_answer
        )


class PollMutation(graphene.ObjectType):
    all_poll_questions = AllPollQuestions.Field()
    create_poll = CreatePoll.Field()
    update_poll = UpdatePoll.Field()
    update_poll_setting = UpdatePollSetting.Field()
    delete_poll = DeletePoll.Field()
    create_poll_tag = CreatePollTag.Field()
