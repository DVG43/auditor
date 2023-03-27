import graphene

from graphql_utils.utils_graphql import PermissionClass
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required

import settings
from http import HTTPStatus
from rest_framework.response import Response
from integration.serializers.googlesheet import GoogleSheetIntegrationSerializer
from integration.models.googlesheet import GoogleSheetIntegration, GoogleSheetCredentials
from graphql import GraphQLError


SESSION = {}


class CreateUserGoogleCredentials(SerializerMutation):
    """
    Create Google Credentials for user and return redirect url
    """

    class Meta:
        serializer_class = GoogleSheetIntegrationSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'
        model_class = GoogleSheetIntegration

    @classmethod
    @login_required
    def get_serializer_kwargs(cls, root, info, **input):
        PermissionClass.has_permission(info)
        input.update({'user': info.context.user})

        if GoogleSheetIntegration.objects.filter(id=input['id']).exists():
            raise GraphQLError('The GS Integration object is already exist.')

        SESSION['data'] = input
        SESSION['user'] = info.context.user

        authorization_url, state = GoogleSheetCredentials.get_google_auth_url(
            settings.CREDENTIALS_FILE_NAME)

        return CreateUserGoogleCredentials(authorization_url=authorization_url)


class IntegrationMutation(graphene.ObjectType):
    create_credentials = CreateUserGoogleCredentials.Field()
