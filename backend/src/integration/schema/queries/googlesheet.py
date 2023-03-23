import graphene
from graphene_django.types import ObjectType
from graphql_jwt.decorators import login_required

from graphql_utils.utils_graphql import PermissionClass
from integration.schema import types
from integration.models.googlesheet import GoogleSheetCredentials, GoogleSheetIntegration


class QueryGoogleSheet(ObjectType):
    all_credentials = graphene.List(types.GoogleSheetCredentialsType)
    all_integrations = graphene.List(types.GoogleSheetIntegrationType)
    integration_by_survey_id = graphene.Field(types.GoogleSheetIntegrationType, survey_id=graphene.Int())

    @login_required
    def resolve_all_credentials(self, info):
        PermissionClass.has_permission(info)
        result = GoogleSheetCredentials.objects.filter(
            user=info.context.user
        ).all()
        return result

    @login_required
    def resolve_all_integrations(self, info):
        PermissionClass.has_permission(info)
        result = GoogleSheetIntegration.objects.filter(
            user=info.context.user).all()
        return result

    @login_required
    def resolve_integration_by_survey_id(self, info, survey_id):
        PermissionClass.has_permission(info)
        result = GoogleSheetIntegration.objects.get(survey_id=survey_id)
        return result
