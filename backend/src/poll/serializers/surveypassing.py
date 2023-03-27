import datetime

from rest_framework import serializers

from poll.models.poll import Poll
from poll.models.surveypassing import SurveyPassing
from poll.serializers.answer import UserAnswerSerializer
from poll.utils import QUESTION_SERIALIZERS_V1


class SurveyPassingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyPassing
        fields = '__all__'
        optional_fields = ['sex', 'platform', 'age', 'user_name',
                           'survey_title', 'status', 'questions']
        read_only_fields = ('created_at', )

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
        questions_get = Poll.objects.get(id=validated_data['poll_id'])

        if questions_get.pagequestion_set:
            questions.extend(list(questions_get.pagequestion_set.values_list('question_id', 'question_type')))
        if questions_get.sectionquestion_set:
            questions.extend(list(questions_get.sectionquestion_set.values_list('question_id', 'question_type')))
        if questions_get.yesnoquestion_set:
            questions.extend(list(questions_get.yesnoquestion_set.values_list('question_id', 'question_type')))
        if questions_get.manyfromlistquestion_set:
            questions.extend(list(questions_get.manyfromlistquestion_set.values_list('question_id', 'question_type')))
        if questions_get.textquestion_set:
            questions.extend(list(questions_get.textquestion_set.values_list('question_id',  'question_type')))
        if questions_get.mediaquestion_set:
            questions.extend(list(questions_get.mediaquestion_set.values_list('question_id',  'question_type')))
        if questions_get.freeanswer_set:
            questions.extend(list(questions_get.freeanswer_set.values_list('question_id',  'question_type')))
        if questions_get.datequestion_set:
            questions.extend(list(questions_get.datequestion_set.values_list('question_id',  'question_type')))
        if questions_get.numberquestion_set:
            questions.extend(list(questions_get.numberquestion_set.values_list('question_id',  'question_type')))
        if questions_get.checkquestion_set:
            questions.extend(list(questions_get.checkquestion_set.values_list('question_id',  'question_type')))

        survey = SurveyPassing()
        survey.user = user
        survey.age = validated_data.get('age', None)
        survey.sex = validated_data.get('sex', None)
        survey.platform = validated_data.get('platform', None)
        survey.created_at = validated_data.get('created_at', datetime.datetime.utcnow())
        survey.user_name = validated_data.get('user_name', 'Anonymous')
        survey.survey_title = validated_data.get('survey_title', 'Untitled')
        survey.questions = questions

        event = 'new'
        if 'user_answers' in validated_data and validated_data['user_answers'][-1]['event'] != 'points':
            event = validated_data['user_answers'][-1]['event']

        survey.status = event
        survey.poll = Poll(id=validated_data['poll_id'])
        survey.save()
        return survey
