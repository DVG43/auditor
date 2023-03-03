import graphene
from graphene_django.types import ObjectType
from graphql_jwt.decorators import login_required

from graphql_utils.utils_graphql import PermissionClass
from poll.schema import types
from poll.models import (
    questions as poll_questions,
)


# class QueryQuestions(ObjectType):
#     all_questions = graphene.List(types.PollType, poll_id=graphene.Int())
#     questions_by_id = graphene.Field(
#         types.PollType,
#         qstn_id=graphene.Int(),
#         qstn_type=graphene.String()
#     )
