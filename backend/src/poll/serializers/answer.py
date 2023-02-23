from rest_framework import serializers

from poll.models.answer import AnswerQuestion, UserAnswerQuestion


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerQuestion

    # def __init__(self, data):
    #     super(AnswerSerializer, self).__init__(data)
    #     # TODO implement validate
    #     self.is_valid = True

    def to_representation(self, instance):
        return {'poll_id': instance.poll_id,
                'text': instance.text,
                'user_id': instance.user_id,
                'photo_path': instance.photo_path,
                'items_question': instance.items_question,
                'checked': instance.checked,
                'id': instance.id,
                'platform': instance.platform,
                'age': instance.age,
                'during': instance.during,
                'sex': instance.sex,
                'event': instance.event,
                'question_id': instance.question_id,

                }

    def create(self, validated_data):
        new_answer = AnswerQuestion(**validated_data)
        if validated_data['event'] not in ('new', 'started', 'inprogress', 'finished'):
            raise serializers.ValidationError("wrong event, must be 'new', 'started', 'inprogress', 'finished'")
        return new_answer


class UserAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAnswerQuestion
        fields = '__all__'

    def to_representation(self, instance):
        return {'survey_id': instance.survey_id,
                # 'text': instance.text,
                'question_id': instance.question_id,
                'poll_id': instance.poll_id,
                'items_question': instance.items_question,
                'event': instance.event,
                'during': instance.during,
                'video_answer': instance.video_answer,
                'photo_answer': instance.photo_answer,
                'audio_answer': instance.audio_answer,
                'file_answer': instance.file_answer,
                'text_answer': instance.text_answer,
                'accepted': instance.accepted,
                'points': instance.points,
                'yes_no_answers_id': instance.yes_no_answers_id,
                'question_type': instance.question_type,
                'another_answer': instance.another_answer
                }

    def validate_answer(self, value):
        if isinstance(value, list):
            for i in value:
                if type(i) not in [type(None), str, list]:
                    raise serializers.ValidationError('valid value in list null or array of nums')
        return value

    def transform_media(self, data: list):
        if data:
            for index in range(len(data)):
                data[index] = {"path": data[index]}

    def create(self, validated_data):
        self.validate_answer(validated_data.get('video_answer', []))
        self.validate_answer(validated_data.get('photo_answer', []))
        self.validate_answer(validated_data.get('audio_answer', []))
        self.validate_answer(validated_data.get('file_answer', []))
        self.validate_answer(validated_data.get('text_answer', []))

        self.transform_media(validated_data.get('video_answer'))
        self.transform_media(validated_data.get('photo_answer'))
        self.transform_media(validated_data.get('audio_answer'))
        self.transform_media(validated_data.get('file_answer'))


        obj = UserAnswerQuestion.objects.filter(
            survey_id=validated_data['survey_id'],
            question_id=validated_data['question_id'],
            poll_id=validated_data['poll_id']
        ).first()
        if obj:
            for key, value in validated_data.items():
                setattr(obj, key, value)
            obj.save()
        else:
            obj = UserAnswerQuestion(**validated_data)
            obj.save()
        return obj
