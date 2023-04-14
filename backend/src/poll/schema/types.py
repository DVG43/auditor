import graphene
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required
from poll.models import analitics as analitics_models
from poll.models import answer as answer_models
from poll.models import poll as poll_models
from poll.models import polltheme as polltheme_models
from poll.models import questions as questions_models
from poll.models import surveypassing as surveypassing_models
from poll.models import user_access as user_access_models
from folders.models import Folder


# Analitics
class PollAnaliticsType(DjangoObjectType):
    class Meta:
        model = analitics_models.PollAnalitics


# Answer
class AnswerQuestionType(DjangoObjectType):
    class Meta:
        model = answer_models.AnswerQuestion


class UserAnswerQuestionType(DjangoObjectType):
    class Meta:
        model = answer_models.UserAnswerQuestion


# Poll
class PollTagsType(DjangoObjectType):
    class Meta:
        model = poll_models.PollTags


class FolderType(DjangoObjectType):
    class Meta:
        model = Folder


class PollType(DjangoObjectType):
    folder = graphene.Field(FolderType)

    class Meta:
        model = poll_models.Poll
        fields = '__all__'


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


class ItemSetQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.ItemSet


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


class NumberQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.NumberQuestion


class DateQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.DateQuestion


class CheckQuestionType(DjangoObjectType):
    class Meta:
        model = questions_models.CheckQuestion


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


class QuestionType(graphene.Union):
    class Meta:
        types = (
            TextQuestionType,
            NumberQuestionType,
            DateQuestionType,
            CheckQuestionType,
            YesNoQuestionType,
            ManyFromListQuestionType,
        )


class SectionQuestionType(DjangoObjectType):
    sections = graphene.List(lambda: SectionQuestionType)
    questions = graphene.List(QuestionType)

    class Meta:
        model = questions_models.SectionQuestion

    @login_required
    def resolve_sections(self, info):
        return questions_models.SectionQuestion.objects.filter(
            parent_id=self.section_id
        )

    @login_required
    def resolve_questions(self, info):
        ret = list()

        ret.extend(questions_models.TextQuestion.objects.filter(parent_id=self.section_id))
        ret.extend(questions_models.NumberQuestion.objects.filter(parent_id=self.section_id))
        ret.extend(questions_models.DateQuestion.objects.filter(parent_id=self.section_id))
        ret.extend(questions_models.CheckQuestion.objects.filter(parent_id=self.section_id))
        ret.extend(questions_models.YesNoQuestion.objects.filter(parent_id=self.section_id))
        ret.extend(questions_models.ManyFromListQuestion.objects.filter(parent_id=self.section_id))

        return ret


class PageQuestionType(DjangoObjectType):
    item_sets = graphene.List(ItemSetQuestionType)
    sections = graphene.List(SectionQuestionType)
    questions = graphene.List(QuestionType)

    class Meta:
        model = questions_models.PageQuestion

    @login_required
    def resolve_sections(self, info):
        return questions_models.SectionQuestion.objects.filter(
            parent_id=self.page_id
        )

    @login_required
    def resolve_questions(self, info):
        ret = list()

        ret.extend(questions_models.TextQuestion.objects.filter(parent_id=self.page_id))
        ret.extend(questions_models.NumberQuestion.objects.filter(parent_id=self.page_id))
        ret.extend(questions_models.DateQuestion.objects.filter(parent_id=self.page_id))
        ret.extend(questions_models.CheckQuestion.objects.filter(parent_id=self.page_id))
        ret.extend(questions_models.YesNoQuestion.objects.filter(parent_id=self.page_id))
        ret.extend(questions_models.ManyFromListQuestion.objects.filter(parent_id=self.page_id))

        return ret

    @login_required
    def resolve_item_sets(self, info):
        return questions_models.ItemSet.objects.filter(
            poll=self.poll
        )


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
