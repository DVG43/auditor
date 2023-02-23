from rest_framework import serializers

from poll.models.poll import Poll
from poll.models.surveypassing import SurveyPassing
from poll.serializers.answer import UserAnswerSerializer
from poll.utils import QUESTION_SERIALIZERS_V1


class SurveyPassingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyPassing

    def __init__(self, *args, **kwargs):
        super(SurveyPassingSerializer, self).__init__()
        self.is_valid = True

    def to_representation(self, instance):
        questions = [
            *instance.poll.manyfromlistquestion_set.all(),
            *instance.poll.freeanswer_set.all(),
            *instance.poll.yesnoquestion_set.all(),
            *instance.poll.mediaquestion_set.all(),
        ]

        question_ids = [answer.question_id for answer in instance.useranswerquestion_set.all()]
        questions = [question for question in questions if question.question_id in question_ids]

        questions_serialized = []
        for question in questions:
            questions_serialized.append(QUESTION_SERIALIZERS_V1[question.question_type](question).data)

        serialized_answers = UserAnswerSerializer(instance.useranswerquestion_set, many=True)

        return {
            'survey_id': instance.id,
            'poll_id': instance.poll_id,
            'user_id': instance.user_id,
            'sex': instance.sex,
            'platform': instance.platform,
            'age': instance.age,
            'createdAt': instance.created_at,
            'user_name': instance.user_name,
            'survey_title': instance.survey_title,
            'status': instance.status,
            'questions': sorted(questions_serialized, key=lambda k: k['order_id']),
            'user_answers': serialized_answers.data,
            'test_mode_global': instance.poll.test_mode_global
        }

    def create(self, user, validated_data):
        questions = []
        questions_get = Poll.objects.get(poll_id=validated_data['poll_id'])

        if questions_get.divisionquestion_set:
            questions.extend(list(questions_get.divisionquestion_set.values_list('question_id', 'question_type')))
        if questions_get.yesnoquestion_set:
            questions.extend(list(questions_get.yesnoquestion_set.values_list('question_id', 'question_type')))
        if questions_get.manyfromlistquestion_set:
            questions.extend(list(questions_get.manyfromlistquestion_set.values_list('question_id', 'question_type')))
        if questions_get.textquestion_set:
            questions.extend(list(questions_get.textquestion_set.values_list('question_id',  'question_type')))
        if questions_get.ratingquestion_set:
            questions.extend(list(questions_get.ratingquestion_set.values_list('question_id', 'question_type')))
        if questions_get.mediaquestion_set:
            questions.extend(list(questions_get.mediaquestion_set.values_list('question_id',  'question_type')))
        if questions_get.finalquestion_set:
            questions.extend(list(questions_get.finalquestion_set.values_list('question_id',  'question_type')))
        if questions_get.headingquestion_set:
            questions.extend(list(questions_get.headingquestion_set.values_list('question_id',  'question_type')))
        if questions_get.freeanswer_set:
            questions.extend(list(questions_get.freeanswer_set.values_list('question_id',  'question_type')))


        survey = SurveyPassing()

        survey.user = user
        survey.age = validated_data['age']
        survey.sex = validated_data['sex']
        survey.platform = validated_data['platform']
        survey.created_at = validated_data['createdAt']
        survey.user_name = validated_data['user_name']
        survey.survey_title = validated_data['survey_title']
        survey.questions = questions

        event = 'new'
        if 'user_answers' in validated_data and validated_data['user_answers'][-1]['event'] != 'points':
            event = validated_data['user_answers'][-1]['event']

        survey.status = event
        survey.poll = Poll(poll_id=validated_data['poll_id'])
        survey.save()
        return survey
