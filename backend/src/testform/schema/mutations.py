import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from enum import Enum

from django.apps import apps
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required
from graphql_utils.permissions import PermissionClass

from testform.schema import types
from testform.models import TestFormQuestion, TFQuestionType, TestForm
from testform.utils import EnumQuestion, EnumTypeAnswer
from testform.serializers import TestFormSerializer

UserModel = get_user_model()

ChoiceTypeQuestion = graphene.Enum.from_enum(EnumQuestion)
ChoiceTypeAnswer = graphene.Enum.from_enum(EnumTypeAnswer)


class crtUpdTestForm(SerializerMutation):
    """
    Создание шаблона теста
    """

    class Meta:
        serializer_class = TestFormSerializer
        model_operations = ['create', 'update']
        lookup_field = 'id'
        model_class = TestForm

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)

        if "folder" in input:
            folder = Folder.objects.filter(pk=input["folder"]).first()
            PermissionClass.has_mutate_object_permission(info, folder)
        else:
            folder = None
        input.update({'owner': info.context.user,
                      'last_modified_user': info.context.user.email,
                      'folder': folder})
        instance = TestFormSerializer.create(
            TestFormSerializer(),
            validated_data=input
        )
        return instance


class BaseQuestionData(graphene.InputObjectType):
    order_id = graphene.Int(required=False)
    type_answer = ChoiceTypeAnswer(required=False)
    max_time = graphene.Int(required=False)


class FinalQuestionData(graphene.InputObjectType):
    order_id = graphene.Int(required=False)
    answer = graphene.String(required=False)


class CrtTFQuestion(graphene.Mutation):
    """
    Создание нового вопроса, имеет поля:
    - testformId - id шаблона теста (обязательное поле)

    - caption - текст вопроса, по умолчанию пустая строка
    - questionType - тип вопроса по выбору из вариантов, по умолчанию общий (BaseTFQuiestion)
    - description - описание вопроса, по умолчанию пустая строка
    - require - статус вопроса(обязательный или нет), по умолчанию False

    При создании новго вопроса автоматически создается указанный тип вопроса.
    На данный момент общий(BaseTFQuiestion) | завершающий(FinalTFQuestion)
    """

    class Arguments:
        caption = graphene.String(required=False)
        question_type = ChoiceTypeQuestion(required=False)
        description = graphene.String(required=False)
        testform_id = graphene.ID(required=True)
        require = graphene.Boolean(required=False)

    question = graphene.Field(types.TestFormQuestionType)

    @staticmethod
    @login_required
    def mutate(cls, info, **input):
        PermissionClass.has_permission(info)
        question = TestFormQuestion(**input)
        question.save()
        return CrtTFQuestion(question=question)


class UpdTFQuestion(graphene.Mutation):
    """
    Изменение вопроса по его id, имеет поля:
    - questionId - id вопроса (обязательное поле)

    - caption - текст вопроса
    - questionType - тип вопроса по выбору из вариантов
    - description - описание вопроса
    - require - статус вопроса(обязательный или нет)
    - mainQData | finalQData - в зависимости от типа вопроса, данные для обновления

    """
    class Arguments:
        caption = graphene.String(required=False)
        question_type = ChoiceTypeQuestion(required=False)
        description = graphene.String(required=False)
        question_id = graphene.ID(required=True)
        require = graphene.Boolean(required=False)
        main_qdata = BaseQuestionData(required=False)
        final_qdata = FinalQuestionData(required=False)

    question = graphene.Field(types.TestFormQuestionType)

    @staticmethod
    @login_required
    def mutate(cls, info, **input):
        PermissionClass.has_permission(info)
        extra_data = input.pop('main_qdata') if 'main_qdata' in input else None
        if not extra_data:
            extra_data = input.pop('final_qdata') if 'final_qdata' in input else None

        obj_id = input.pop('question_id')
        question = TestFormQuestion.objects.get(pk=obj_id)
        for k, v in input.items():
            if k == 'question_type':
                if isinstance(v, EnumQuestion):
                    v = v._value_
                elif v.count('.'):
                    v = v.split('.')[-1]
            setattr(question, k, v)
        question.save()

        if extra_data:
            model = apps.get_model('testform', question.question_type.split('.')[-1])
            extra_model = model.objects.filter(testform_question=question).first()
            for k, v in extra_data.items():
                if k == 'type_answer':
                    if isinstance(v, EnumTypeAnswer):
                        v = v._value_
                    elif v.count('.'):
                        v = v.split('.')[-1]
                setattr(extra_model, k, v)
            extra_model.save()
            for i, v in enumerate(TFQuestionType.objects
                                                .filter(testform_question__testform=question.testform)
                                                .order_by('-updated_at', '-created_at'), start=1):
                v.order_id = i
                v.save()

        return UpdTFQuestion(question=question)


class MutationTestForm(graphene.ObjectType):
    crt_upd_testform = crtUpdTestForm.Field()
    crt_tf_question = CrtTFQuestion.Field()
    upd_tf_question = UpdTFQuestion.Field()
