import graphene
from graphene_django.types import ObjectType
from graphql_jwt.decorators import login_required

from graphql_utils.utils_graphql import PermissionClass
from integration.schema import types
from integration.models.googlesheet import GoogleSheetCredentials, GoogleSheetIntegration


class QueryGoogleSheet(ObjectType):
    all_credentials = graphene.List(types.GoogleSheetCredentialsType)
    all_integrations = graphene.List(types.GoogleSheetIntegrationType)
    credentials_by_user_id = graphene.Field(types.GoogleSheetCredentialsType, user_id=graphene.Int())
    integration_by_survey_id = graphene.Field(types.GoogleSheetIntegrationType, survey_id=graphene.Int())

    @login_required
    def resolve_all_credentials(self, info):
        PermissionClass.has_permission(info)
        ret = GoogleSheetCredentials.objects.filter(
            user=info.context.user
        ).all()
        return ret

    @login_required
    def resolve_all_integrations(self, info):
        PermissionClass.has_permission(info)
        ret = GoogleSheetIntegration.objects.filter(
            user=info.context.user).all()
        return ret
