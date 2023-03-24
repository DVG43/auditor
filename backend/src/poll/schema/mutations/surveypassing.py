import graphene
from django.contrib.auth import get_user_model
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required

from poll.permissions import PermissionPollClass
from poll.models import (
    surveypassing as surveypassing_models,
    poll as poll_models
)
from poll.schema import types
from poll.serializers import surveypassing as surveypassing_serializers


UserModel = get_user_model()


class CreateSurvey(SerializerMutation):
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
        PermissionPollClass.has_permission(info)

        poll = poll_models.Poll.objects.filter(id=int(input["poll"])).first()
        PermissionPollClass.has_mutate_object_permission(info, poll)

        user = UserModel.objects.get(pk=int(input["user"]))
        input.update({"user": user, "poll": poll, 'poll_id': poll.id})
        instance = surveypassing_serializers.SurveyPassingSerializer.create(
            surveypassing_serializers.SurveyPassingSerializer(),
            validated_data=input, user=user
        )
        return instance


class MultipleDeleteSurvey(graphene.Mutation):
    """
    Mutation for multiple delete SurveyPassing instances
    """
    class Arguments:
        ids = graphene.List(graphene.ID)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, root, info, ids):
        PermissionPollClass.has_permission(root)
        sp_list = surveypassing_models.SurveyPassing.objects.filter(id__in=ids).all()
        for sp in sp_list:
            PermissionPollClass.has_mutate_object_permission(root, sp.poll)
        sp_list.delete()
        return cls(ok=True)


class SurveyPassingMutation(graphene.ObjectType):
    create_survey = CreateSurvey.Field()
    multipledelete_survey = MultipleDeleteSurvey.Field()
