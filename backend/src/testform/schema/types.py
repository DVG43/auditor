from graphene_django import DjangoObjectType

from testform.models import TestForm, TestFormQuestion, TFQuestionType, BaseTFQuestion, FinalTFQuestion


class TestFormType(DjangoObjectType):
    class Meta:
        model = TestForm


class TestFormQuestionType(DjangoObjectType):
    class Meta:
        model = TestFormQuestion


class ParentQuestionType(DjangoObjectType):
    class Meta:
        model = TFQuestionType


class BaseTFQuestionType(DjangoObjectType):
    class Meta:
        model = BaseTFQuestion


class FinalTFQuestionType(DjangoObjectType):
    class Meta:
        model = FinalTFQuestion
