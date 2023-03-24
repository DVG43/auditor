import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required

from poll.permissions import PermissionPollClass
from poll.models import (
    answer as answer_models,
    surveypassing as surveypassing_models,
    poll as poll_models
)
from poll.schema import types
from poll.serializers import answer as answer_serializers
from poll.serializers import surveypassing as surveypassing_serializers


class CreateUserAnswer(SerializerMutation):
    """
    Mutation for creating UserAnswerQuestion instance
    """
    class Meta:
        serializer_class = answer_serializers.UserAnswerSerializer
        model_operations = ['create']
        lookup_field = 'id'
        model_class = answer_models.UserAnswerQuestion
        convert_choices_to_enum = True

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionPollClass.has_permission(info)

        # sp = surveypassing_models.SurveyPassing.objects.filter(id=input["survey_id"]).first()
        # PermissionPollClass.has_mutate_object_permission(info, sp.poll)

        # input.update({"user": user, "poll": poll, 'poll_id': poll.id})
        print(input)
        instance = answer_serializers.UserAnswerSerializer.create(
            answer_serializers.UserAnswerSerializer(),
            validated_data=input
        )
        return instance


class EventChoice(graphene.Enum):
    NEW = 'New'
    STARTED = 'Started'
    INPROGRESS = 'In progress'
    COMPLETED = 'Completed'


class CreateUserAnswerInput(graphene.InputObjectType):
    question_id = graphene.Int(required=True)
    poll_id = graphene.Int(required=True)
    survey_id = graphene.ID(required=True)

    text = graphene.String(required=False, default_value=None)
    item_question = graphene.List(graphene.List(graphene.Int), required=False)
    event = EventChoice(required=False, default_value='NEW')
    during = graphene.Int(required=False, default_value=1)
    question_type = graphene.String(required=False)
    yes_no_answers_id = graphene.List(graphene.Int, required=False)
    points = graphene.Int(required=False, default_value=0)
    accepted = graphene.Boolean(required=False, default_value=False)
    video_answer = graphene.String(required=False, default_value=None)
    photo_answer = graphene.String(required=False, default_value=None)
    audio_answer = graphene.String(required=False, default_value=None)
    file_answer = graphene.String(required=False, default_value=None)
    text_answer = graphene.String(required=False, default_value=None)


class CrtUserAnswer(graphene.Mutation):
    """
    Mutation for model UserAnswerQuestion for creating new instance
    """

    class Arguments:
        new_instance = CreateUserAnswerInput()

    user_answer_item = graphene.Field(types.UserAnswerQuestionType)

    @staticmethod
    @login_required
    def mutate(cls, info, **input):
        PermissionPollClass.has_permission(info)
        instance = answer_serializers.UserAnswerSerializer.create(
            answer_serializers.UserAnswerSerializer(),
            validated_data=input['new_instance']
        )

        return CrtUserAnswer(user_answer_item=instance)


class UserAnswerMutation(graphene.ObjectType):
    crt_UserAnswers = CrtUserAnswer.Field()
