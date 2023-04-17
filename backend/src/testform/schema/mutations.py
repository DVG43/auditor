import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from enum import Enum

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from graphql_jwt.decorators import login_required
from graphql_utils.permissions import PermissionClass

from testform.schema import types
from testform.models import TestFormQuestion, TFQuestionType, TestForm
from testform.schema.utils import (
    EnumQuestion,
    EnumTypeAnswer,
    EnumTypeLogo,
    update_attrs,
    normalize_order,
)
from testform.serializers import TestFormSerializer

UserModel = get_user_model()
ChoiceTypeQuestion = graphene.Enum.from_enum(EnumQuestion)
ChoiceTypeAnswer = graphene.Enum.from_enum(EnumTypeAnswer)
ChoiceTypeLogo = graphene.Enum.from_enum(EnumTypeLogo)


class CrtUpdTestForm(SerializerMutation):
    """
    Создание шаблона теста

    При создании нового теста автоматически создается
    два вопроса к нему с дефолтными значениями:
    Общий вопрос и Завершающий
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


class DeleteTestForm(graphene.Mutation):
    """
    Удаление шаблона теста
    """
    class Arguments:
        testform_id = graphene.ID()

    ok = graphene.Boolean()

    def mutate(self, info, testform_id):
        PermissionClass.has_permission(info)
        instance = TestForm.objects.filter(id=testform_id).first()
        if instance:
            instance.deleted_id = uuid.uuid4()
            instance.deleted_since = timezone.now()
            instance.save()
        return DeleteTestForm(ok=False)


class QuestionData(graphene.InputObjectType):
    order_id = graphene.Int(required=False)
    answer_type = graphene.List(ChoiceTypeAnswer, required=False)
    max_time = graphene.Int(required=False)
    button_name = graphene.String(required=False)


class CrtTFQuestion(graphene.Mutation):
    """
    Создание нового вопроса, имеет поля:
    - testformId - id шаблона теста (обязательное поле)

    - caption - текст вопроса, по умолчанию пустая строка
    - questionType - тип вопроса по выбору из вариантов, по умолчанию общий (BaseTFQuiestion)
    - description - описание вопроса, по умолчанию пустая строка
    - require - статус вопроса(обязательный или нет), по умолчанию False

    При создании нового вопроса автоматически создается указанный тип вопроса.
    На данный момент есть только общий(BaseTFQuiestion), который является значением по умолчанию,
    поэтому параметр questionType можно не использовать.
    """

    class Arguments:
        testform_id = graphene.ID(required=True)
        caption = graphene.String(required=False)
        question_type = ChoiceTypeQuestion(required=False)
        description = graphene.String(required=False)
        require = graphene.Boolean(required=False)

    Output = types.TestFormQuestionType

    @staticmethod
    def mutate(cls, info, **input):
        PermissionClass.has_permission(info)
        question = TestFormQuestion(**input)
        question.save()
        return question


class UpdTFQuestion(graphene.Mutation):
    """
    Изменение вопроса по его id, имеет поля:
    - questionId - id вопроса (обязательное поле)

    - caption - текст вопроса
    - questionType - тип вопроса по выбору из вариантов.
    - description - описание вопроса
    - require - статус вопроса(обязательный или нет)
    - questionData - в зависимости от типа вопроса, данные для обновления полей вопроса
    - logoQuestion - тип лого вопроса по выбору: видео или фото
    - urlName - ссылка на видео, указывать в случае если logo_question = video
      Загрузка фото в разработке.

    На данный момент есть только общий(BaseTFQuiestion), который является значением по умолчанию,
    поэтому параметр questionType можно не использовать.
    """
    class Arguments:
        question_id = graphene.ID(required=True)

        caption = graphene.String(required=False)
        question_type = ChoiceTypeQuestion(required=False)
        description = graphene.String(required=False)
        require = graphene.Boolean(required=False)
        question_data = QuestionData(required=False)
        logo_question = ChoiceTypeLogo(required=False)
        url_name = graphene.String(required=False)

    Output = types.TestFormQuestionType

    @staticmethod
    def mutate(cls, info, **input):
        PermissionClass.has_permission(info)
        obj_id = input.pop('question_id')
        question = TestFormQuestion.objects.get(pk=obj_id)
        question_type_data = input.pop('question_data') if 'question_data' in input else None
        # Запрет на изменение порядка и типа вопроса для финального вопроса
        if question.question_type == 'FinalTFQuestion':
            if input.get('question_type'):
                raise ValueError("You cant change type by Final Question")
            elif question_type_data.get('order_id'):
                raise ValueError("You cant change order for Final Question")
        # Валидация типа ответа
        if question_type_data.get('answer_type') is not None and \
                len(question_type_data['answer_type']) == 0:
            raise ValueError("Answer type can't be null")

        if input:
            update_attrs(question, input)

        if question_type_data:
            model = apps.get_model('testform', question.question_type)

            # Валидация введенных данных для соответствующего типа вопроса
            fields = [field.name for field in model._meta.get_fields()]
            if non_fields := set.difference(set(question_type_data.keys()), set(fields)):
                raise KeyError(f"{question.question_type} have not fields: {', '.join(list(non_fields))}")

            # Обновление полей вопроса
            question_type_instance = model.objects.filter(testform_question=question).first()
            update_order = '-updated_at'
            if question_type_data.get('order_id', 0) > question_type_instance.order_id:
                update_order = 'updated_at'
            update_attrs(question_type_instance, question_type_data)

            # Нормализация порядка вопросов теста в случае изменения order_id
            if 'order_id' in question_type_data:
                queryset = TFQuestionType.objects.only('order_id', 'updated_at')\
                    .filter(testform_question__testform=question.testform,
                            order_id__lt=10000)\
                    .order_by('order_id', update_order)
                normalize_order(queryset)

        return question


class DeleteTestFormQuestion(graphene.Mutation):
    """
    Удаление вопроса к тесту
    """

    class Arguments:
        testform_id = graphene.ID()
        question_id = graphene.ID()

    ok = graphene.Boolean()

    def mutate(cls, info, question_id, testform_id):
        PermissionClass.has_permission(info)
        instance = TestFormQuestion.objects.filter(question_id=question_id, testform_id=testform_id).first()
        if instance:
            instance.delete()
            return DeleteTestFormQuestion(ok=True)
        return DeleteTestFormQuestion(ok=False)


class MutationTestForm(graphene.ObjectType):
    crt_upd_testform = CrtUpdTestForm.Field()
    delete_testform = DeleteTestForm.Field()
    crt_testform_question = CrtTFQuestion.Field()
    upd_testform_question = UpdTFQuestion.Field()
    delete_testform_question = DeleteTestFormQuestion.Field()
