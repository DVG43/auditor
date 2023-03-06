import graphene
from graphene_django.types import ObjectType
from graphql_jwt.decorators import login_required

from graphql_utils.utils_graphql import PermissionClass
from poll.schema import types
from poll.models import (
    questions as poll_questions,
)


# class QueryQuestions(ObjectType):
#     pass
