from rest_framework import serializers
from poll.models.poll import Poll, PollSettings, PollTags
from poll.utils import QUESTION_SERIALIZERS_V1
# from accounts.serializers import UserSerializer


class JSONSerializerField(serializers.Field):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class PollSettingsSerializer(serializers.ModelSerializer):
    maxTimeRange = JSONSerializerField(required=False)
    groupsForRefilling = JSONSerializerField(required=False)
    groupsForOnlyOneFilling = JSONSerializerField(required=False)
    useAnswersTimeRestriction = serializers.CharField(required=False, allow_blank=True)
    redirectMethod = serializers.CharField(required=False, allow_blank=True)
    redirectPath = serializers.CharField(required=False, allow_blank=True)
    formInactiveMessage = serializers.CharField(required=False, allow_blank=True)
    language = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = PollSettings
        exclude = ('poll',)

    def to_representation(self, instance):
        ret = super(PollSettingsSerializer, self).to_representation(instance)
        ret['maxTimeRange'] = instance.maxTimeRange
        ret['groupsForRefilling'] = instance.groupsForRefilling
        ret['groupsForOnlyOneFilling'] = instance.groupsForOnlyOneFilling

        ret['useAnswersTimeRestriction'] = instance.useAnswersTimeRestriction
        ret['redirectMethod'] = instance.redirectMethod
        ret['redirectPath'] = instance.redirectPath
        ret['formInactiveMessage'] = instance.formInactiveMessage
        ret['language'] = instance.language
        return ret


class PollTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollTags
        fields = ['tag_id', 'name']


class PollSerializer(serializers.ModelSerializer):
    """
    Poll model serializer implementation.
    """
    setting = PollSettingsSerializer(required=False)
    tags = PollTagsSerializer(many=True, required=False)
    tags_list = PollTagsSerializer(many=True, required=False)

    class Meta:
        model = Poll
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'last_modified_user',
            'last_modified_date',
            'delete_id',
            'deleted_since',
            'owner'
        ]

    def __init__(self, *args, **kwargs):
        super(PollSerializer, self).__init__(*args, **kwargs)
        self.owner = None
        if 'request' in self.context:
            self.owner = self.context.get('request').user

    def to_representation(self, instance):
        questions = instance.get_questions()
        instance.normalize_questions_order_id()
        questions_serialized = []
        questions_for_serializer = {}

        # put questions by type in Dict[key: question_type, value: list of questions]
        for question in questions:
            prev = questions_for_serializer.get(question.question_type, [])
            questions_for_serializer[question.question_type] = [*prev, question]

        for key in questions_for_serializer.keys():
            questions_serialized.extend(
                QUESTION_SERIALIZERS_V1[key](questions_for_serializer[key], many=True).data)

        questions_serialized = sorted(questions_serialized, key=lambda k: k['order_id'])


        if hasattr(instance, 'setting'):
            setting = PollSettingsSerializer(instance.setting).data
        else:
            setting = None

        tags = PollTagsSerializer(instance.tags_list, many=True).data
        response = {
            'id': instance.id,
            'author': instance.owner.email,  # profile.full_name,
            'name': instance.name,
            'test_mode_global': instance.test_mode_global,
            'questions': questions_serialized,
            'count_answers': instance.count_answers,
            'tags': tags,
            'setting': setting,
            'new_survey_passing': instance.new_survey_passing(),
            'last_open': instance.last_open,
            # 'telegram_integration': instance.telegram_integration_is_active(),
            # 'googlesheet_integration': instance.googlesheet_integration_is_active()
        }
        request = self.context.get('request')
        if request and request.user:
            if request.user == instance.owner:
                response['user_role'] = 'author'
            else:
                response['user_role'] = ''
                access = request.user.poll_access.filter(poll=instance)
                if access.exists():
                    response['user_role'] = access.first().role
        return response

    def loсal_update(self, question, model_class, model_serializer):
        if 'question_id' in question:
            edit_qu = model_class.objects.filter(question_id=question['question_id'])
            if edit_qu.count() > 0:
                model_serializer.update(edit_qu.first(), question)
        else:
            new_div = model_serializer.create(question)
            new_div.save()

    def update(self, instance, validated_data):
        poll_setting = validated_data.pop('setting', {})
        poll_setting['poll'] = instance

        if hasattr(instance, 'setting'):
            PollSettingsSerializer.update(PollSettingsSerializer(), instance=instance.setting, validated_data=poll_setting)
        else:
            PollSettingsSerializer.create(PollSettingsSerializer(), validated_data=poll_setting)

        tags = validated_data.pop('tags', [])
        instance.tags_list.clear()
        for tag in tags:
            instance_tag, created = PollTags.objects.get_or_create(**tag)
            instance.tags_list.add(instance_tag)

        return super(PollSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        poll = Poll()
        poll_setting = validated_data.pop('setting', {})
        poll.owner = self.owner
        poll.name = validated_data.get('name')
        poll.image = validated_data.get('image', '')
        poll.test_mode_global = validated_data.get('test_mode_global', False) in ['true', 'True', True]
        poll.host_project = validated_data.get('host_project')
        poll.folder = validated_data.get('folder')
        poll.last_modified_user = validated_data.get('last_modified_user')
        poll.save()
        tags = validated_data.get('tags', [])
        for tag in tags:
            instance_tag, created = PollTags.objects.get_or_create(**tag)
            poll.tags_list.add(instance_tag)
        poll.save()
        poll_setting['poll'] = poll
        PollSettingsSerializer.create(PollSettingsSerializer(), validated_data=poll_setting)
        return poll


class PollListSerializer(serializers.ModelSerializer):
    setting = PollSettingsSerializer(required=False, read_only=True)
    tags = PollTagsSerializer(many=True, required=False, source='tags_list')
    author = serializers.CharField(read_only=True, source='owner.email')
    new_survey_passing = serializers.SerializerMethodField()
    # telegram_integration = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ['id', 'name', 'test_mode_global', 'count_answers', 'last_open', 'new_survey_passing',
                  'author', 'tags', 'setting']

    def get_new_survey_passing(self, instance):
        return instance.new_survey_passing()

    # def get_telegram_integration(self, instance):
    #     return instance.telegram_integration_is_active()

    def to_representation(self, instance):
        resp = super(PollListSerializer, self).to_representation(instance)
        request = self.context.get('request')
        if request.user == instance.owner:
            resp['user_role'] = 'author'
        else:
            resp['user_role'] = ''
            access = request.user.poll_access.filter(poll=instance)
            if access.exists():
                resp['user_role'] = access.first().role
        return resp
