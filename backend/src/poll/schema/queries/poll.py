import graphene
from graphene_django.types import ObjectType
from graphql_jwt.decorators import login_required

from graphql_utils.utils_graphql import PermissionClass
from poll.schema import types
from poll.models import (
    poll as poll_models,
    # questions as questions_models
)
# from poll.serializers import (
#     poll as poll_serializers,
#     questions as questions_serializers
# )
from rest_framework.generics import get_object_or_404


class QueryPoll(ObjectType):
    all_polls = graphene.List(types.PollType)
    all_poll_tags = graphene.List(types.PollTagsType, poll_id=graphene.Int())
    poll_by_id = graphene.Field(types.PollType, poll_id=graphene.Int())
    poll_setting_by_id = graphene.Field(types.PollSettingsType, poll_id=graphene.Int())
    poll_tag_by_id = graphene.Field(types.PollTagsType, tag_id=graphene.Int())

    @login_required
    def resolve_all_polls(self, info):
        PermissionClass.has_permission(info)
        # PermissionClass.has_query_object_permission(info, prj_id)
        ret = poll_models.Poll.objects.filter(
            owner=info.context.user,
            deleted_id__isnull=True,
        ).all()
        return ret

    @login_required
    def resolve_all_poll_tags(self, info, poll_id=None):
        PermissionClass.has_permission(info)
        # PermissionClass.has_query_object_permission(info, prj_id)
        ret = poll_models.PollTags.objects.filter(
            poll=poll_id).all()
        return ret

    # @login_required
    # def resolve_all_poll_questions(self, info, poll_id=None, prj_id=None):
    #     PermissionClass.has_permission(info)
    #     PermissionClass.has_query_object_permission(info, prj_id)
    #     division = questions_models.DivisionQuestion.objects.filter(poll_id=poll_id).all()
    #     division_questions = questions_serializers.DivisionQuestionSerializer(division, many=True)
    #
    #     yes_no = questions_models.YesNoQuestion.objects.filter(poll_id=poll_id).all()
    #     yesno_questions = questions_serializers.YesNoQuestionSerializer(yes_no, many=True)
    #
    #     manyfromlist = questions_models.ManyFromListQuestion.objects.filter(poll_id=poll_id).all()
    #     manyfromlist_questions = questions_serializers.ManyFromListQuestionSerializer(manyfromlist, many=True)
    #
    #     text = questions_models.TextQuestion.objects.filter(poll_id=poll_id).all()
    #     text_questions = questions_serializers.TextQuestionSerializer(text, many=True)
    #
    #     rating = questions_models.RatingQuestion.objects.filter(poll_id=poll_id).all()
    #     rating_questions = questions_serializers.RatingQuestionSerializer(rating, many=True)
    #
    #     media = questions_models.MediaQuestion.objects.filter(poll_id=poll_id).all()
    #     media_questions = questions_serializers.MediaQuestionSerializer(media, many=True)
    #
    #     final = questions_models.FinalQuestion.objects.filter(poll_id=poll_id).all()
    #     final_questions = questions_serializers.FinalQuestionSerializer(final, many=True)
    #
    #     heading = questions_models.HeadingQuestion.objects.filter(poll_id=poll_id).all()
    #     heading_question = questions_serializers.HeadingQuestionSerializer(heading, many=True)
    #
    #     free_answer = questions_models.FreeAnswer.objects.filter(poll_id=poll_id).all()
    #     free_answer_serializer = questions_serializers.FreeAnswerSerializer(free_answer, many=True)
    #     return {'result':  (division_questions.data,
    #                         yesno_questions.data,
    #                         manyfromlist_questions.data,
    #                         text_questions.data,
    #                         rating_questions.data,
    #                         media_questions.data,
    #                         final_questions.data,
    #                         heading_question.data,
    #                         free_answer_serializer.data)}

    @login_required
    def resolve_poll_by_id(self, info, poll_id=None):
        PermissionClass.has_permission(info)

        ret = get_object_or_404(poll_models.Poll, id=poll_id)
        # prj_id = ret.host_project.id
        # PermissionClass.has_query_object_permission(info, prj_id)

        return ret

    @login_required
    def resolve_poll_setting_by_id(self, info, poll_id=None):
        PermissionClass.has_permission(info)

        ret = poll_models.PollSettings.objects.get(id=poll_id)
        prj_id = ret.poll.host_project.id
        PermissionClass.has_query_object_permission(info, prj_id)

        return ret

    @login_required
    def resolve_poll_tag_by_id(self, info, tag_id=None):
        PermissionClass.has_permission(info)

        ret = poll_models.PollTags.objects.get(tag_id=tag_id)
        polls = ret.poll_set.all()
        for poll in polls:
            prj_id = poll.host_project.id
            PermissionClass.has_query_object_permission(info, prj_id)

        return ret
