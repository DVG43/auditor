import graphene
from graphene_django import DjangoObjectType
from django.apps import apps

from testform.models import (
    TestForm,
    TestFormQuestion,
    TFQuestionType,
    BaseTFQuestion,
    FinalTFQuestion,
)


class TestFormType(DjangoObjectType):
    class Meta:
        model = TestForm


class ParentQuestionType(DjangoObjectType):
    class Meta:
        model = TFQuestionType


class BaseTFQuestionType(DjangoObjectType):
    class Meta:
        model = BaseTFQuestion
        exclude = ('tfquestiontype_ptr',)


class FinalTFQuestionType(DjangoObjectType):
    class Meta:
        model = FinalTFQuestion
        exclude = ('tfquestiontype_ptr',)


class QType(graphene.Union):
    class Meta:
        types = (BaseTFQuestionType, FinalTFQuestionType)


class TestFormQuestionType(DjangoObjectType):
    class Meta:
        model = TestFormQuestion
        fields = ('question_id', 'testform', 'caption', 'description', 'require', 'question_type')

    question_data = QType()

    def resolve_question_data(self, info):
        model = apps.get_model('testform', self.question_type)
        return model.objects.filter(testform_question__question_id=self.pk).first()
