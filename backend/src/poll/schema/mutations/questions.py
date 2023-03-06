import graphene
from graphql_jwt.decorators import login_required
from graphene_django.rest_framework.mutation import SerializerMutation

from graphql_utils.utils_graphql import PermissionClass

# from poll.schema import types
from poll.models import (
    poll as poll_models,
    questions as qstn_models,
)
from poll.serializers import (
    questions as qstn_serializers,
)


class CrtUpdFreeQuestions(SerializerMutation):

    class Meta:
        serializer_class = qstn_serializers.FreeAnswerSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.FreeAnswer

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)

        poll = poll_models.Poll.objects.get(id=input['poll'])
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


class CrtUpdManyQuestions(SerializerMutation):

    class Meta:
        serializer_class = qstn_serializers.ManyFromListQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.ManyFromListQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)

        poll = poll_models.Poll.objects.get(id=input['poll'])
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
    class Meta:
        serializer_class = qstn_serializers.YesNoQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.YesNoQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)

        poll = poll_models.Poll.objects.get(id=input['poll'])
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
    class Meta:
        serializer_class = qstn_serializers.FinalQuestionSerializer
        model_operations = ['create', 'update']
        lookup_field = 'question_id'
        model_class = qstn_models.FinalQuestion

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        PermissionClass.has_permission(info)

        poll = poll_models.Poll.objects.get(id=input['poll'])
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

        poll = poll_models.Poll.objects.get(id=input['poll'])
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


class QstnMutation(graphene.ObjectType):
    crt_upd_free_question = CrtUpdFreeQuestions.Field()
    crt_upd_many_question = CrtUpdManyQuestions.Field()
    crt_upd_yes_no_question = CrtUpdYesNoQuestions.Field()
    crt_upd_final_question = CrtUpdFinalQuestions.Field()
    crt_upd_division_question = CrtUpdDivisionQuestions.Field()
    crt_upd_item_question = CrtUpdItemQuestions.Field()
