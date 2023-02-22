from rest_framework import serializers
from poll.models.questions import ManyFromListQuestion, DivisionQuestion, YesNoQuestion, RatingQuestion, TextQuestion, \
    MediaQuestion, FinalQuestion, HeadingQuestion, FreeAnswer, ItemQuestion, MediaItemQuestion, ItemsFreeAnswer, \
    FreeAnswerAttachedType, MediaAttachedType, YesNoAttachedType, ItemBase

# Questions Serializers


QUESTION_BASE_FIELDS = [
    'question_id', 'question_type', 'order_id', 'description', 'poll',
    'caption',
    'require', 'mix_answers', 'time_for_answer', 'type_for_show', 'title_image',
    'resize_image', 'test_mode', 'updated_at', 'created_at',
]


class DivisionQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DivisionQuestion
        fields = QUESTION_BASE_FIELDS + [
            'comment'
        ]


class ManyFromListQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManyFromListQuestion
        fields = QUESTION_BASE_FIELDS + [
            'description_mode', 'count_of_answer', 'current_number_value', 'answer_from',
            'answer_to', 'answer_time', 'comment'
        ]


class YesNoQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = YesNoQuestion
        fields = QUESTION_BASE_FIELDS + [
            'description_mode', 'max_video_duration', 'is_video'
        ]


class RatingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingQuestion
        fields = QUESTION_BASE_FIELDS + [
            'rating'
        ]


class TextQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextQuestion
        fields = QUESTION_BASE_FIELDS + [
            'text'
        ]


class MediaQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaQuestion
        fields = QUESTION_BASE_FIELDS + [
            'description_mode', 'max_video_duration', 'is_video',
            'resize_image'
        ]


class FinalQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalQuestion
        fields = QUESTION_BASE_FIELDS + [
            'description_mode', 'max_video_duration', 'is_video', 'show_my_answers',
            'correct_answers', 'point_for_answers', 'button_mode', 'button_text', 'button_url',
            'reopen'
        ]


class HeadingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeadingQuestion
        fields = ['question_id', 'question_type', 'caption', 'order_id', 'poll', 'updated_at',
                  'created_at']


class FreeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeAnswer
        fields = QUESTION_BASE_FIELDS + [
            'answer_time', 'description_mode'
        ]


# Questions subclass Serializers
# Items


class ItemQuestionSubClassSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        instance = super().create(validated_data)
        question = self.context.get('question')
        if question:
            question.items.add(instance)
            question.save()
        ItemBase.normalize_order_id(question.items.all())
        return instance

    def update(self, instance, validated_data):
        old_order_id = instance.order_id
        instance = super().update(instance, validated_data)
        instance.normalize_order_id_other(
            old_order_id=old_order_id,
            new_order_id=instance.order_id
        )
        return instance


class ItemQuestionSerializer(ItemQuestionSubClassSerializer):
    class Meta:
        model = ItemQuestion
        fields = ['item_question_id', 'order_id', 'text', 'text', 'photo_path', 'points',
                  'selected', 'userAnswer', 'userAnswerText', 'updated_at', 'created_at']


class MediaItemQuestionSerializer(serializers.ModelSerializer):
    item_question_id = serializers.IntegerField(source='media_question_id', read_only=True)

    class Meta:
        model = MediaItemQuestion
        fields = ['item_question_id', 'points']

    def create(self, validated_data):
        instance = super().create(validated_data)
        question = self.context.get('question')
        if question:
            question.items.add(instance)
            question.save()
        return instance


class ItemsFreeAnswerSerializer(ItemQuestionSubClassSerializer):
    class Meta:
        model = ItemsFreeAnswer
        fields = ['item_question_id', 'order_id', 'text', 'checked', 'photo_path', 'count_of_input',
                  'selected', 'points', 'type_answer_row', 'updated_at', 'created_at']


# attached_types


class AttachedTypeSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        instance = super().create(validated_data)
        question = self.context.get('question')
        if question:
            question.attached_type.add(instance)
            question.save()
        return instance


class FreeAnswerAttachedTypeSerializer(AttachedTypeSerializer):
    class Meta:
        model = FreeAnswerAttachedType
        fields = [
            'attached_id', 'type', 'active'
        ]


class MediaAttachedTypeSerializer(AttachedTypeSerializer):
    class Meta:
        model = MediaAttachedType
        fields = [
            'media_attached_id', 'type', 'active', 'count', 'duration', 'symbols', 'size'
        ]


class YesNoAttachedTypeSerializer(AttachedTypeSerializer):
    class Meta:
        model = YesNoAttachedType
        fields = [
            'attached_id', 'type', 'active', 'count', 'duration', 'symbols', 'size'
        ]
