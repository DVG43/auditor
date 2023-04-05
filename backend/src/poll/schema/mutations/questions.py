import graphene
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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})
        if 'question_id' in input.keys():
            question_id = input.pop('question_id')
            qstn_models.PageQuestion.objects.filter(question_id=question_id).update(**input)
            ret = qstn_models.PageQuestion.objects.get(pk=question_id)
        else:
            ret = qstn_models.PageQuestion(**input)
        ret.save()

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

        ret = qstn_models.SectionQuestion(**input)
        ret.save()

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

        ret = qstn_models.HeadingQuestion(**input)
        ret.save()

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

        ret = qstn_models.NumberQuestion(**input)
        ret.save()

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

        ret = qstn_models.DateQuestion(**input)
        ret.save()

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

        ret = qstn_models.CheckQuestion(**input)
        ret.save()

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

        ret = qstn_models.RatingQuestion(**input)
        ret.save()

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

        ret = qstn_models.TextQuestion(**input)
        ret.save()

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

        items, attached_types = [], []
        if 'items' in input:
            items = input['items']
            del input['items']
        if 'attached_type' in input:
            attached_types = input['attached_type']
            del input['attached_type']

        ret = qstn_models.FreeAnswer(**input)
        ret.save()

        if items:
            for item in items:
                crt_item = qstn_models.ItemsFreeAnswer(**item)
                crt_item.save()
                ret.items.add(crt_item)

        if attached_types:
            for attached_type in attached_types:
                crt_attype = qstn_models.FreeAnswerAttachedType(**attached_type)
                crt_attype.save()
                ret.attached_type.add(crt_attype)

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

        items, attached_types = [], []
        if 'items' in input:
            items = input['items']
            del input['items']
        if 'attached_type' in input:
            attached_types = input['attached_type']
            del input['attached_type']

        ret = qstn_models.MediaQuestion(**input)
        ret.save()

        if items:
            for item in items:
                crt_item = qstn_models.MediaItemQuestion(**item)
                crt_item.save()
                ret.items.add(crt_item)

        if attached_types:
            for attached_type in attached_types:
                crt_attype = qstn_models.MediaAttachedType(**attached_type)
                crt_attype.save()
                ret.attached_type.add(crt_attype)

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

        items, attached_types = [], []
        if 'items' in input:
            items = input['items']
            del input['items']
        if 'attached_type' in input:
            attached_types = input['attached_type']
            del input['attached_type']

        ret = qstn_models.ManyFromListQuestion(**input)
        ret.save()

        if items:
            for item in items:
                crt_item = qstn_models.ItemQuestion(**item)
                crt_item.save()
                ret.items.add(crt_item)

        if attached_types:
            for attached_type in attached_types:
                crt_attype = qstn_models.ManyFromListAttachedType(**attached_type)
                crt_attype.save()
                ret.attached_type.add(crt_attype)

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})

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

        ret = qstn_models.YesNoQuestion(**input)
        ret.save()

        if items:
            for item in items:
                crt_item = qstn_models.ItemQuestion(**item)
                crt_item.save()
                ret.items.add(crt_item)

        if attached_types:
            for attached_type in attached_types:
                crt_attype = qstn_models.YesNoAttachedType(**attached_type)
                crt_attype.save()
                ret.attached_type.add(crt_attype)

        if yes_no_answers:
            for yes_no_answer in yes_no_answers:
                crt_yesnoanswer = qstn_models.YesNoAnswers(**yes_no_answer)
                crt_yesnoanswer.save()
                ret.yes_no_answers.add(crt_yesnoanswer)

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})
        items = []
        if 'items' in input:
            items = input['items']
            del input['items']

        ret = qstn_models.FinalQuestion(**input)
        ret.save()

        if 'items' in input:
            for item in items:
                crt_item = qstn_models.ItemQuestion(**item)
                crt_item.save()
                ret.items.add(crt_item)

        poll.normalize_questions_order_id()
        return ret


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
        poll = get_object_or_404(poll_models.Poll, id=input['poll'])
        PermissionClass.has_mutate_object_permission(info, poll)

        input.update({'poll': poll})
        ret = qstn_models.DivisionQuestion(**input)
        ret.save()
        poll.normalize_questions_order_id()
        return ret


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

        ret = qstn_models.ItemQuestion(**input)
        ret.save()
        return ret


class DeleteItemQuestions(graphene.Mutation):
    """
    Удаляет вариант ответа из вопроса.
    Принимает {item_id: int, item_type: string}, где
    qstn_type == "PageQuestion"|"ManyFromListQuestion"|"YesNoQuestion"
    |"SectionQuestion"|"TextQuestion"|"MediaQuestion"
    |"DateQuestion"|"NumberQuestion"|"FreeAnswer"
    """

    class Arguments:
        item_id = graphene.ID()
        item_type = graphene.String()

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, root, item_id, item_type):
        PermissionClass.has_permission(root)
        if item_type in ITEM_MODELS:
            item = ITEM_MODELS(item_type).objects.filter(
                id=item_id
            ).first()
            if item:
                item.delete()
                return DeleteItemQuestions(ok=True)
        return DeleteItemQuestions(ok=False)


class DeleteQuestion(graphene.Mutation):
    """
    Удаляет вопрос из чеклиста.
    Принимает {question_id: int, qstn_type: string}, где
    qstn_type == "PageQuestionType"|"ManyFromListQuestionType"|"YesNoQuestionType"
    |"SectionQuestionType"|"TextQuestionType"|"MediaQuestionType"
    |"DateQuestionType"|"NumberQuestionType"|"FreeAnswerType"
    """

    class Arguments:
        qstn_id = graphene.ID()
        qstn_type = graphene.String()
    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(cls, info, qstn_id, qstn_type):
        PermissionClass.has_permission(info)
        index = qstn_type.rfind('type')
        question_type = qstn_type[:index]
        if question_type in QUESTION_MODELS.keys():
            question = QUESTION_MODELS[question_type].objects.filter(
                question_id=qstn_id
            ).first()
            if question:
                PermissionClass.has_mutate_object_permission(
                    info,
                    question.poll
                )
                question.delete()
                question.poll.normalize_questions_order_id()
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
    crt_upd_item_question = CrtUpdItemQuestions.Field()
    delete_item_question = DeleteItemQuestions.Field()
    delete_question = DeleteQuestion.Field()
