import graphene

from graphql_jwt.decorators import login_required
from graphql_utils.permissions import PermissionClass
from testform.schema import types
from testform.models import TestFormQuestion, TFQuestionType


class QueryTestForm(graphene.ObjectType):
    testform_by_id = graphene.Field(types.TestFormType, id=graphene.ID())
    all_testform_questions = graphene.List(types.TestFormQuestionType, testform_id=graphene.Int())
    testform_question_by_id = graphene.Field(types.TestFormQuestionType, question_id=graphene.Int())

    @login_required
    def resolve_testform_by_id(self, info, id=None):
        """
        Получение всех вопросов по тесту
        """
        PermissionClass.has_permission(info)
        ret = TestForm.objects.get(pk=id)
        return ret

    @login_required
    def resolve_all_testform_questions(self, info, testform_id=None):
        """
        Получение всех вопросов по тесту
        """
        PermissionClass.has_permission(info)
        ret = TestFormQuestion.objects.filter(testform=testform_id)
        return ret

    @login_required
    def resolve_testform_question_by_id(self, info, question_id=None):
        """
        Получение конкретного вопроса по questionId.
        """
        PermissionClass.has_permission(info)
        ret = TestFormQuestion.objects.filter(question_id=question_id).first()
        return ret
