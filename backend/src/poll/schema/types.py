from graphene_django.types import DjangoObjectType
from poll.models import analitics as analitics_models
from poll.models import answers as answers_models
from poll.models import poll as poll_models
from poll.models import polltheme as polltheme_models
from poll.models import questions as questions_models
from poll.models import surveypassing as surveypassing_models
from poll.models import user_access as user_access_models


# Analitics
class PollAnaliticsType(DjangoObjectType):
    class Meta:
        model = analitics_models.PollAnalitics


# Answer
class AnswerQuestionType(DjangoObjectType):
    class Meta:
        model = answers_models.AnswerQuestion


class UserAnswerQuestionType(DjangoObjectType):
    class Meta:
        model = answers_models.UserAnswerQuestion


# Poll
class PollTagsType(DjangoObjectType):
    class Meta:
        model = poll_models.PollTags


class PollType(DjangoObjectType):
    class Meta:
        model = poll_models.Poll


class PollSettingsType(DjangoObjectType):
    class Meta:
        model = poll_models.PollSettings


# PollTheme
class PollThemeType(DjangoObjectType):
    class Meta:
        model = polltheme_models.PollTheme


# Questions
class DivisionQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.DivisionQuestion


class EventType(DjangoObjectType):
    class Meta:
        model = questions_models.Event


class ItemQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.ItemQuestion


class ManyFromListAttachedType(DjangoObjectType):
    class Meta:
        model = questions_models.ManyFromListAttachedType


class ManyFromListQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.ManyFromListQuestion


class YesNoAnswersType(DjangoObjectType):
    class Meta:
        model = questions_models.YesNoAnswers


class YesNoAttachedType(DjangoObjectType):
    class Meta:
        model = questions_models.YesNoAttachedType


class YesNoQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.YesNoQuestion


class MediaFileType(DjangoObjectType):
    class Meta:
        model = questions_models.MediaFile


class MediaAttachedType(DjangoObjectType):
    class Meta:
        model = questions_models.MediaAttachedType


class MediaItemQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.MediaItemQuestion


class MediaQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.MediaQuestion


class TextQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.TextQuestion


class FinalQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.FinalQuestion


class HeadingQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.HeadingQuestion


class FreeAnswerAttachedType(DjangoObjectType):
    class Meta:
        model = questions_models.FreeAnswerAttachedType


class ItemTagsFreeAnswerType(DjangoObjectType):
    class Meta:
        model = questions_models.ItemTagsFreeAnswer


class ItemsFreeAnswerType(DjangoObjectType):
    class Meta:
        model = questions_models.ItemsFreeAnswer


class FreeAnswerType(DjangoObjectType):
    class Meta:
        model = questions_models.FreeAnswer


class TagsFreeAnswerType(DjangoObjectType):
    class Meta:
        model = questions_models.TagsFreeAnswer


# SurveyPassing
class SurveyPassingType(DjangoObjectType):
    class Meta:
        model = surveypassing_models.SurveyPassing


# User Access
class UserAccessType(DjangoObjectType):
    class Meta:
        model = user_access_models.UserAccess


class InvitationsType(DjangoObjectType):
    class Meta:
        model = user_access_models.Invitations
