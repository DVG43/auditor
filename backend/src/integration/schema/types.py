from graphene_django.types import DjangoObjectType
from integration.models import googlesheet as gs_models
from integration.models import telegram as telegram_models


# GoogleSheet
class GoogleSheetIntegrationType(DjangoObjectType):
    class Meta:
        model = gs_models.GoogleSheetIntegration
        fields = ("id", "user")


class GoogleSheetCredentialsType(DjangoObjectType):
    class Meta:
        model = gs_models.GoogleSheetCredentials


# Telegram
class TelegramVariableType(DjangoObjectType):
    class Meta:
        model = telegram_models.TelegramVariable


class TelegramIntegrationType(DjangoObjectType):
    class Meta:
        model = telegram_models.TelegramIntegration


class TelegramChatsType(DjangoObjectType):
    class Meta:
        model = telegram_models.TelegramChats
