import graphene
from enum import Enum
from rest_framework.generics import get_object_or_404
from graphql_jwt.decorators import login_required
from graphene_django.rest_framework.mutation import SerializerMutation

from graphql_utils.permissions import PermissionClass
from poll.utils import ITEM_MODELS, QUESTION_MODELS
from poll.models import (
    poll as poll_models,
    questions as qstn_models,
)
from poll.serializers import (
    questions as qstn_serializers,
)
from poll.service import update_questions_order


class CrtUpdPageQuestions(SerializerMutation):
    """
    Создание|Обновление страницы Чеклиста.
    Для вложенных вопросов в поле <parent_id>
    нужно указать <page_id> данной страницы
    """

    class Meta:
        serializer_class = qstn_serializers.PageQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.PageQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        question_id = input.get('question_id', None)

        obj, created = qstn_models.PageQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                         defaults={**input})
        update_questions_order(obj, created)
        return obj


class CrtUpdSectionQuestions(SerializerMutation):
    """
    Создание|Обновление секции Чеклиста.
    Для вложенных вопросов в поле <parent_id>
    нужно указать <section_id> данной страницы
    """

    class Meta:
        serializer_class = qstn_serializers.SectionQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.SectionQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        question_id = input.get('question_id', None)

        obj, created = qstn_models.SectionQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                            defaults={**input})
        update_questions_order(obj, created)
        return obj


class CrtUpdHeadQuestions(SerializerMutation):
    """
    Создание|Обновление головного вопроса
    """

    class Meta:
        serializer_class = qstn_serializers.HeadingQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.HeadingQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        question_id = input.get('question_id', None)

        obj, created = qstn_models.HeadingQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                            defaults={**input})
        update_questions_order(obj, created)
        return obj


class CrtUpdNumberQuestions(SerializerMutation):
    """
    Создание|Обновление числового вопроса
    """

    class Meta:
        serializer_class = qstn_serializers.NumberQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.NumberQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        question_id = input.get('question_id', None)

        obj, created = qstn_models.NumberQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                           defaults={**input})
        update_questions_order(obj, created)
        return obj


class CrtUpdDateQuestions(SerializerMutation):
    """
    Создание|Обновление вопроса даты
    """

    class Meta:
        serializer_class = qstn_serializers.DateQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.DateQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        question_id = input.get('question_id', None)

        obj, created = qstn_models.DateQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                         defaults={**input})
        update_questions_order(obj, created)
        return obj


class CrtUpdCheckQuestions(SerializerMutation):
    """
    Создание|Обновление вопроса чекбокса (Булевого)
    """

    class Meta:
        serializer_class = qstn_serializers.CheckQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.CheckQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        question_id = input.get('question_id', None)

        obj, created = qstn_models.CheckQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                          defaults={**input})
        update_questions_order(obj, created)
        return obj


class CrtUpdRatingQuestions(SerializerMutation):
    class Meta:
        serializer_class = qstn_serializers.RatingQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.RatingQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        question_id = input.get('question_id', None)

        obj, created = qstn_models.RatingQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                           defaults={**input})
        update_questions_order(obj, created)
        return obj


class CrtUpdTextQuestions(SerializerMutation):
    """
    Создание|Обновление текстового вопроса
    """

    class Meta:
        serializer_class = qstn_serializers.TextQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.TextQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        question_id = input.get('question_id', None)

        obj, created = qstn_models.TextQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                         defaults={**input})
        update_questions_order(obj, created)
        return obj


class CrtUpdFreeQuestions(SerializerMutation):
    """
    Создание|Обновление FreeAnswer вопроса
    """

    class Meta:
        serializer_class = qstn_serializers.FreeAnswerSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.FreeAnswer

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        items, attached_types = [], []
        if 'items' in input:
            items = input['items']
            del input['items']
        if 'attached_type' in input:
            attached_types = input['attached_type']
            del input['attached_type']

        question_id = input.get('question_id', None)

        obj, created = qstn_models.FreeAnswer.objects.update_or_create(poll=poll, question_id=question_id,
                                                                       defaults={**input})
        if items:
            for item in items:
                crt_item = qstn_models.ItemsFreeAnswer(**item)
                crt_item.save()
                obj.items.add(crt_item)

        if attached_types:
            for attached_type in attached_types:
                crt_attype = qstn_models.FreeAnswerAttachedType(**attached_type)
                crt_attype.save()
                obj.attached_type.add(crt_attype)

        update_questions_order(obj, created)
        return obj


class CrtUpdMediaQuestions(SerializerMutation):
    """
    Создание|Обновление Media вопроса
    """

    class Meta:
        serializer_class = qstn_serializers.MediaQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.MediaQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        items, attached_types = [], []
        if 'items' in input:
            items = input['items']
            del input['items']
        if 'attached_type' in input:
            attached_types = input['attached_type']
            del input['attached_type']

        question_id = input.get('question_id', None)

        obj, created = qstn_models.MediaQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                          defaults={**input})

        if items:
            for item in items:
                crt_item = qstn_models.MediaItemQuestion(**item)
                crt_item.save()
                obj.items.add(crt_item)

        if attached_types:
            for attached_type in attached_types:
                crt_attype = qstn_models.MediaAttachedType(**attached_type)
                crt_attype.save()
                obj.attached_type.add(crt_attype)

        update_questions_order(obj, created)
        return obj


class CrtUpdYesNoQuestions(SerializerMutation):
    """
    Создание|Обновление вопроса с одиночным выбором
    """

    class Meta:
        serializer_class = qstn_serializers.YesNoQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.YesNoQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        items, attached_types, yes_no_answers = [], [], []
        if 'items' in input:
            items = input['items']
            del input['items']
        if 'attached_type' in input:
            attached_types = input['attached_type']
            del input['attached_type']
        if 'yes_no_answers' in input:
            yes_no_answers = input['yes_no_answers']
            del input['yes_no_answers']

        question_id = input.get('question_id', None)

        question_obj, created = qstn_models.YesNoQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                                   defaults={**input})
        if items:
            for item in items:
                crt_item = qstn_models.ItemQuestion(**item)
                crt_item.save()
                question_obj.items.add(crt_item)

        if attached_types:
            for attached_type in attached_types:
                crt_attype = qstn_models.YesNoAttachedType(**attached_type)
                crt_attype.save()
                question_obj.attached_type.add(crt_attype)

        if yes_no_answers:
            for yes_no_answer in yes_no_answers:
                crt_yesnoanswer = qstn_models.YesNoAnswers(**yes_no_answer)
                crt_yesnoanswer.save()
                question_obj.yes_no_answers.add(crt_yesnoanswer)

        update_questions_order(question_obj, created)
        return question_obj


class CrtUpdFinalQuestions(SerializerMutation):
    """
    Создание|Обновление финального вопроса
    """

    class Meta:
        serializer_class = qstn_serializers.FinalQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.FinalQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        items = []
        if 'items' in input:
            items = input['items']
            del input['items']

        question_id = input.get('question_id', None)

        obj, created = qstn_models.FinalQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                          defaults={**input})
        if 'items' in input:
            for item in items:
                crt_item = qstn_models.ItemQuestion(**item)
                crt_item.save()
                obj.items.add(crt_item)

        update_questions_order(obj, created)
        return obj


class CrtUpdDivisionQuestions(SerializerMutation):
    class Meta:
        serializer_class = qstn_serializers.DivisionQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.DivisionQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        question_id = input.get('question_id', None)

        obj, created = qstn_models.DivisionQuestion.objects.update_or_create(poll=poll, question_id=question_id,
                                                                             defaults={**input})
        update_questions_order(obj, created)
        return obj


class CrtUpdItemSet(SerializerMutation):
    class Meta:
        serializer_class = qstn_serializers.ItemSetSerializer
        model_operations = ['create', 'update']
        lookup_field = 'item_set_id'
        model_class = qstn_models.ItemSet

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)

        item_id = input.get('item_set_id', None)

        obj, created = qstn_models.ItemSet.objects.update_or_create(item_set_id=item_id,
                                                                    defaults={**input})
        return obj


class CrtUpdItemQuestions(SerializerMutation):
    class Meta:
        serializer_class = qstn_serializers.ItemQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'item_question_id'
        model_class = qstn_models.ItemQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)

        item_id = input.get('item_question_id', None)

        obj, created = qstn_models.TextQuestion.objects.update_or_create(item_question_id=item_id,
                                                                         defaults={**input})
        return obj


class CrtUpdManyQuestions(SerializerMutation):
    """
    Создание|Обновление вопроса с множественным выбором
    """

    class Meta:
        serializer_class = qstn_serializers.ManyFromListQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.ManyFromListQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)
        poll = get_object_or_404(poll_models.Poll, id=input.pop('poll'))
        PermissionClass.has_mutate_object_permission(info, poll)

        items, attached_types = [], []
        if 'items' in input:
            items = input['items']
            del input['items']
        if 'attached_type' in input:
            attached_types = input['attached_type']
            del input['attached_type']

        question_id = input.get('question_id', None)

        question_obj, created = qstn_models.ManyFromListQuestion.objects.update_or_create(poll=poll,
                                                                                          question_id=question_id,
                                                                                          defaults={**input})
        if items:
            for item in items:
                crt_item = qstn_models.ItemQuestion(**item)
                crt_item.save()
                question_obj.items.add(crt_item)

        if attached_types:
            for attached_type in attached_types:
                crt_attype = qstn_models.ManyFromListAttachedType(**attached_type)
                crt_attype.save()
                question_obj.attached_type.add(crt_attype)

        update_questions_order(question_id, created)
        return question_obj


class ItemEnum(Enum):
    ManyFromListItemType = 'ManyFromListQuestion'
    YesNoItemType = 'YesNoQuestion'
    MediaItemType = 'MediaQuestion'
    FinalQuestionItemType = 'FinalQuestion'
    FreeAnswerItemType = 'FreeAnswer'


ChoiceItemType = graphene.Enum.from_enum(ItemEnum)


class DeleteItemQuestions(graphene.Mutation):
    """
    Удаляет вариант ответа из вопроса.
    Принимает аргументы (itemId: ID, itemType: ItemType)
    """

    class Arguments:
        item_id = graphene.ID()
        item_type = ChoiceItemType(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, root, item_id, item_type):
        PermissionClass.has_permission(root)
        if item_type in ITEM_MODELS.keys():
            item = ITEM_MODELS[item_type].objects.filter(
                pk=item_id
            ).first()
            if item:
                item.delete()
                return DeleteItemQuestions(ok=True)
        return DeleteItemQuestions(ok=False)


class QuestionEnum(Enum):
    PageQuestionType = 'PageQuestion'
    SectionQuestionType = 'SectionQuestion'
    DivisionQuestionType = 'DivisionQuestion'
    NumberQuestionType = 'NumberQuestion'
    DateQuestionType = 'DateQuestion'
    CheckQuestionType = 'CheckQuestion'
    ManyFromListQuestionType = 'ManyFromListQuestion'
    YesNoQuestionType = 'YesNoQuestion'
    RatingQuestionType = 'RatingQuestion'
    TextQuestionType = 'TextQuestion'
    MediaQuestionType = 'MediaQuestion'
    FinalQuestionType = 'FinalQuestion'
    HeadingQuestionType = 'HeadingQuestion'
    FreeAnswerType = 'FreeAnswer'


ChoiceQuestionType = graphene.Enum.from_enum(QuestionEnum)


class DeleteQuestion(graphene.Mutation):
    """
    Удаляет вопрос из чеклиста.
    Принимает аргументы (questionId: ID, questionType: QuestionType)
    """

    class Arguments:
        question_id = graphene.ID()
        question_type = ChoiceQuestionType(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, info, question_id, question_type):
        PermissionClass.has_permission(info)
        if question_type in QUESTION_MODELS.keys():
            question = QUESTION_MODELS[question_type].objects.filter(
                question_id=question_id
            ).first()
            if question:
                PermissionClass.has_mutate_object_permission(
                    info,
                    question.poll
                )
                question.delete()
                return DeleteQuestion(ok=True)
        return DeleteQuestion(ok=False)


class QstnMutation(graphene.ObjectType):
    crt_upd_page_question = CrtUpdPageQuestions.Field()
    crt_upd_section_question = CrtUpdSectionQuestions.Field()
    crt_upd_text_question = CrtUpdTextQuestions.Field()
    crt_upd_number_question = CrtUpdNumberQuestions.Field()
    crt_upd_date_question = CrtUpdDateQuestions.Field()
    crt_upd_check_question = CrtUpdCheckQuestions.Field()
    crt_upd_free_question = CrtUpdFreeQuestions.Field()
    crt_upd_media_question = CrtUpdMediaQuestions.Field()
    crt_upd_many_question = CrtUpdManyQuestions.Field()
    crt_upd_yes_no_question = CrtUpdYesNoQuestions.Field()
    crt_upd_item_set = CrtUpdItemSet.Field()
    crt_upd_item_question = CrtUpdItemQuestions.Field()
    delete_item_question = DeleteItemQuestions.Field()
    delete_question = DeleteQuestion.Field()
