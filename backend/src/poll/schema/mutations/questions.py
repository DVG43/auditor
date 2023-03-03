import graphene
from graphql_jwt.decorators import login_required
from graphene_django.rest_framework.mutation import SerializerMutation

from graphql_utils.utils_graphql import PermissionClass

# from poll.schema import types
from poll.models import (
    poll as poll_models,
    questions as qstn_models,
)
from poll.serializers import (
    questions as qstn_serializers,
)


class CreateDivisionQuestions(SerializerMutation):
    class Meta:
        serializer_class = qstn_serializers.DivisionQuestionSerializer

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)

        poll = poll_models.Poll.objects.get(id=input['poll'])
        input.update({'poll': poll})
        ret = super().mutate_and_get_payload(root, info, **input)

        poll.normalize_questions_order_id()
        return ret


class QstnMutation(graphene.ObjectType):
    create_division_question = CreateDivisionQuestions.Field()
