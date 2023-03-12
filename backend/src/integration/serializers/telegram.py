from django.db.models import F, Value, BooleanField
from rest_framework import serializers

from integration.models.telegram import TelegramIntegration, TelegramChats
from poll.models.questions import ManyFromListQuestion, YesNoQuestion, FreeAnswer


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


class TelegramChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramChats
        fields = ['chat_id']


class TelegramIntegrationSerializer(serializers.ModelSerializer):
    chats = TelegramChatSerializer(many=True)
    isActive = serializers.BooleanField(source='is_active')

    class Meta:
        model = TelegramIntegration
        fields = ['chats', 'token', 'message', 'isActive']

    def create(self, validated_data):
        chats = validated_data.pop('chats', [])
        telegram_integration = get_or_none(TelegramIntegration, poll_id=self.context.get('poll_id'))
        if not telegram_integration:
            telegram_integration = TelegramIntegration.objects.create(poll_id=self.context.get('poll_id'),
                                                                      **validated_data)
        else:
            telegram_integration.message = validated_data.get('message', '')
            telegram_integration.is_active = validated_data.get('is_active', False)
            telegram_integration.token = validated_data.get('token', '')
            telegram_integration.save()
        chats_ids = list(map(lambda x: x['chat_id'], chats))
        telegram_integration.chats.exclude(chat_id__in=chats_ids).delete()
        for chat in chats:
            telegram_integration.chats.get_or_create(
                bot=telegram_integration,
                chat_id=chat['chat_id']
            )
        return telegram_integration

    def update(self, instance, validated_data):
        chats = validated_data.pop('chats', [])
        super(TelegramIntegrationSerializer, self).update(instance, validated_data)
        if chats:
            chats_ids = list(map(lambda x: x['chat_id'], chats))
            instance.chats.exclude(chat_id__in=chats_ids).delete()
            for chat in chats:
                instance.chats.get_or_create(
                    bot=instance,
                    chat_id=chat['chat_id']
                )
        return instance

    def to_representation(self, instance):
        representation = super(TelegramIntegrationSerializer, self).to_representation(instance)
        representation['chats'] = TelegramChatSerializer(instance.chats.all(), many=True).data

        question_ids = ManyFromListQuestion.objects.filter(poll_id=instance.poll.pk).values_list('question_id',
                                                                                                 flat=True)

        variables_question = list(ManyFromListQuestion.objects.annotate(
            questionType=F('question_type'),
            answer=Value(False, output_field=BooleanField())
        ).filter(question_id__in=question_ids).values('caption', 'questionType', 'answer'))

        questions = [
            *FreeAnswer.objects.filter(poll_id=instance.poll.pk).prefetch_related("items"),
            *YesNoQuestion.objects.filter(poll_id=instance.poll.pk).prefetch_related("items"),
        ]

        for question in questions:
            variables_question.append({
                "caption": question.caption,
                "questionType": question.question_type,
                "answer": False
            })

        representation['variables'] = variables_question
        representation['variables'].extend(
            [
                {
                    "caption": "Ссылка",
                    "questionType": "Service",
                    "answer": False
                },
                {
                    "caption": "Автор",
                    "questionType": "Service",
                    "answer": False
                },
                {
                    "caption": 'Дата',
                    "questionType": "Service",
                    "answer": False
                },
                {
                    "caption": '№ ответа',
                    "questionType": "Service",
                    "answer": False
                },
                {
                    "caption": 'Ссылка на отчет',
                    "questionType": "Service",
                    "answer": False
                },
                {
                    "caption": 'Название формы',
                    "questionType": "Service",
                    "answer": False
                },
            ]
        )
        return representation
