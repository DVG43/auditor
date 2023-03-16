import uuid

import graphene
from django.utils import timezone
from django.contrib.auth import get_user_model
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required

from graphql_utils.utils_graphql import PermissionClass
from poll.models import (
    surveypassing as surveypassing_models,
    poll as poll_models
)
from poll.schema import types
from poll.serializers import surveypassing as surveypassing_serializers


UserModel = get_user_model()


class CreateSurveyPassing(SerializerMutation):
    """
    Mutation for creating SurveyPassing instance
    """
    poll = graphene.Int(required=True)
    user = graphene.Int(required=True)
    questions = graphene.JSONString()

    class Meta:
        serializer_class = surveypassing_serializers.SurveyPassingSerializer
        model_operations = ['create']
        lookup_field = 'id'
        model_class = surveypassing_models.SurveyPassing

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)

        user = UserModel.objects.get(pk=input["user"])
        poll = poll_models.Poll.objects.filter(id=input["poll"])
        input.update({"user": user, "poll": poll})
        instance = surveypassing_serializers.SurveyPassingSerializer.create(
            surveypassing_serializers.SurveyPassingSerializer(),
            validated_data=input, user=user
        )
        return instance


class MultipleDeleteSurveyPassing(graphene.Mutation):
    """
    Mutation for multiple delete SurveyPassing instances
    """
    class Arguments:
        ids = graphene.List(graphene.ID)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, root, ids):
        PermissionClass.has_permission(root)
        sp_list = surveypassing_models.SurveyPassing.objects.filter(id__in=ids).all()
        sp_list.delete()
        return cls(ok=True)


class SurveyPassingMutation(graphene.ObjectType):
    create_surveypassung = CreateSurveyPassing.Field()
    multipledelete_surveypassing = MultipleDeleteSurveyPassing.Field()
