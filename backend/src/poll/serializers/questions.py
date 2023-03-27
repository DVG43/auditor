from rest_framework import serializers

from poll.models.questions import DivisionQuestion, ItemQuestion, ManyFromListQuestion, YesNoQuestion, \
    RatingQuestion, MediaFile, MediaQuestion, TextQuestion, MediaItemQuestion, MediaAttachedType, FinalQuestion, \
    YesNoAnswers, YesNoAttachedType, HeadingQuestion, FreeAnswer, ItemsFreeAnswer, FreeAnswerAttachedType, \
    TagsFreeAnswer, ItemTagsFreeAnswer, ManyFromListAttachedType, PageQuestion, SectionQuestion


def max_min_validator(value):
    if value > 100:
        raise serializers.ValidationError('Point cannot be more than 100.')
    elif value <= 0:
        raise serializers.ValidationError('Rating cannot be 0 or less than 0.')
    else:
        return value


class BaseQuestionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(read_only=True)
    question_type = serializers.CharField(read_only=True, max_length=100, default='Question')
    order_id = serializers.IntegerField(default=0)
    description = serializers.CharField(max_length=512)
    caption = serializers.CharField(max_length=512)
    parent_id = serializers.UUIDField(required=False)

    require = serializers.BooleanField(required=False)
    mix_answers = serializers.BooleanField(required=False)
    time_for_answer = serializers.BooleanField(required=False)
    type_for_show = serializers.IntegerField(default=0, required=False)
    title_image = serializers.CharField(max_length=512, required=False)
    resize_image = serializers.BooleanField(required=False)
    test_mode = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        instance.order_id = validated_data.get('order_id', instance.order_id)
        instance.description = validated_data.get('description', instance.description)
        instance.caption = validated_data.get('caption', instance.caption)

        # Необязательные поля
        instance.require = validated_data.get('require', instance.require)
        instance.mix_answers = validated_data.get('mix_answers', instance.mix_answers)
        instance.time_for_answer = validated_data.get('time_for_answer', instance.time_for_answer)
        instance.type_for_show = validated_data.get('type_for_show', instance.type_for_show)
        instance.title_image = validated_data.get('title_image', instance.title_image)
        instance.resize_image = validated_data.get('resize_image', instance.resize_image)
        instance.test_mode = validated_data.get('test_mode', instance.test_mode)


class DivisionQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DivisionQuestion
        fields = '__all__'


class ItemQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemQuestion
        fields = [
            'item_question_id', 'order_id', 'text',
            'checked', 'photo_path', 'points', 'selected',
            'userAnswer', 'userAnswerText'
        ]

    def create(self, validated_data):
        instance = super(ItemQuestionSerializer, self).create(validated_data)
        return instance


class MediaAttachedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAttachedType
        fields = '__all__'


class MediaItemQuestionSerializer(serializers.ModelSerializer):
    item_question_id = serializers.IntegerField(source='media_question_id', read_only=True)

    class Meta:
        model = MediaItemQuestion
        fields = ['item_question_id', 'points']


class YesNoAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = YesNoAnswers
        fields = '__all__'


class YesNoAttachedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = YesNoAttachedType
        fields = ['attached_id', 'type', 'active', 'count', 'duration', 'symbols', 'size']


class YesNoQuestionSerializer(serializers.ModelSerializer):
    items = ItemQuestionSerializer(many=True, required=False)
    yes_no_answers = YesNoAnswersSerializer(many=True, required=False)
    attached_type = YesNoAttachedTypeSerializer(many=True, required=False)

    class Meta:
        model = YesNoQuestion
        fields = '__all__'

    @staticmethod
    def create(validated_data):
        question_items = validated_data.pop('items', [])
        attached_types = validated_data.pop('attached_type', [])
        yes_no_answers = validated_data.pop('yes_no_answers', [])

        yes_no_question = YesNoQuestion.objects.create(**validated_data)

        for question_item in question_items:
            yes_no_question.items.add(ItemQuestion.objects.create(**question_item))

        for attached_type in attached_types:
            yes_no_question.attached_type.add(YesNoAttachedType.objects.create(**attached_type))

        for yes_no_answer in yes_no_answers:
            yes_no_question.yes_no_answers.add(YesNoAnswers.objects.create(**yes_no_answer))

        validated_data['items'] = ItemQuestionSerializer(yes_no_question.items.all(), many=True).data
        validated_data['yes_no_answers'] = YesNoAnswersSerializer(yes_no_question.yes_no_answers.all(), many=True).data
        validated_data['attached_type'] = YesNoAttachedTypeSerializer(yes_no_question.attached_type.all(),
                                                                      many=True).data
        return yes_no_question

    def update(self, instance, validated_data):
        question_items = validated_data.pop('items', None)
        attached_types = validated_data.pop('attached_type', None)
        yes_no_answers = validated_data.pop('yes_no_answers', None)

        super(YesNoQuestionSerializer, self).update(instance, validated_data)

        if question_items:
            instance.items.clear()
            instance.update_or_create_items(question_items)

        if attached_types:
            instance.attached_type.clear()
            instance.update_or_create_attached_type(attached_types)

        if yes_no_answers:
            instance.yes_no_answers.clear()
            instance.update_or_create_yes_no_answers(yes_no_answers)

        instance.save()
        return instance


class ManyFromListQuestionAttachedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManyFromListAttachedType
        fields = [
            'attached_id', 'type', 'active'
        ]


class ManyFromListQuestionSerializer(BaseQuestionSerializer):
    comment = serializers.CharField(max_length=512)
    poll = serializers.CharField(max_length=64)
    answer_time = serializers.IntegerField(default=0, required=False)
    description_mode = serializers.BooleanField(required=False)
    count_of_answer = serializers.IntegerField(required=False)
    current_number_value = serializers.IntegerField(required=False)
    answer_from = serializers.IntegerField(required=False)
    answer_to = serializers.IntegerField(required=False)
    attached_type = ManyFromListQuestionAttachedTypeSerializer(many=True, required=False)
    items = ItemQuestionSerializer(many=True, required=False)

    class Meta:
        model = ManyFromListQuestion
        fields = '__all__'

    def create(self, validated_data):
        question_items = validated_data.pop('items', [])
        attached_types = validated_data.pop('attached_type', [])
        many_from_list_question = ManyFromListQuestion.objects.create(**validated_data)
        for question_item in question_items:
            many_from_list_question.items.add(ItemQuestion.objects.create(**question_item))
        for attached_type in attached_types:
            many_from_list_question.attached_type.add(ManyFromListAttachedType.objects.create(**attached_type))
        validated_data['items'] = ItemQuestionSerializer(many_from_list_question.items.all(), many=True).data
        validated_data['attached_type'] = ManyFromListQuestionAttachedTypeSerializer(
            many_from_list_question.attached_type.all(),
            many=True).data
        return many_from_list_question

    def update(self, instance, validated_data):
        super(ManyFromListQuestionSerializer, self).update(instance, validated_data)

        # Необязательные поля
        instance.description_mode = validated_data.get('description_mode', instance.description_mode)
        instance.count_of_answer = validated_data.get('count_of_answer', instance.count_of_answer)
        instance.current_number_value = validated_data.get('current_number_value', instance.current_number_value)
        instance.answer_from = validated_data.get('answer_from', instance.answer_from)
        instance.answer_to = validated_data.get('answer_to', instance.answer_to)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.answer_time = validated_data.get('answer_time', instance.answer_time)

        _items = validated_data.get('items', [])
        if _items:
            instance.items.clear()
            for question_item in _items:
                instance.items.add(ItemQuestion.objects.create(**question_item))
        instance.save()
        return instance


class MediaQuestionSerializer(serializers.ModelSerializer):
    attached_type = MediaAttachedTypeSerializer(many=True, read_only=True)
    items = MediaItemQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = MediaQuestion
        fields = '__all__'

    def create(self, validated_data):
        question_items = validated_data.pop('items', [])
        attached_types = validated_data.pop('attached_type', [])

        media_question = MediaQuestion.objects.create(**validated_data)

        for question_item in question_items:
            max_min_validator(int(question_item['points']))
            media_question.items.add(MediaItemQuestion.objects.create(**question_item))

        for attached_type in attached_types:
            media_question.attached_type.add(MediaAttachedType.objects.create(**attached_type))

        validated_data['items'] = MediaItemQuestionSerializer(media_question.items.all(), many=True).data
        validated_data['attached_type'] = MediaAttachedTypeSerializer(media_question.attached_type.all(),
                                                                      many=True).data
        return media_question

    def update(self, instance, validated_data):
        _items = validated_data.pop('items', [])
        _attached_type = validated_data.pop('attached_type', [])

        super(MediaQuestionSerializer, self).update(instance, validated_data)

        if _items:
            instance.items.clear()
            for question_item in _items:
                max_min_validator(int(question_item['points']))
                instance.items.add(MediaItemQuestion.objects.create(**question_item))

        if _attached_type:
            instance.attached_type.clear()
            for attached in _attached_type:
                instance.attached_type.add(MediaAttachedType.objects.create(**attached))
        instance.save()
        return instance


class RatingQuestionSerializer(BaseQuestionSerializer):
    rating = serializers.IntegerField()
    poll = serializers.CharField(max_length=64)

    def create(self, validated_data):
        return RatingQuestion.objects.create(**validated_data)

    def update(self, instance, validated_data):
        super(RatingQuestionSerializer, self).update(instance, validated_data)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.save()
        return instance


class MediaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = ['file_id', 'path_to_file']


class TextQuestionSerializer(BaseQuestionSerializer):
    text = serializers.CharField(max_length=1024)
    poll = serializers.CharField(max_length=64)

    def create(self, validated_data):
        return TextQuestion.objects.create(**validated_data)

    def update(self, instance, validated_data):
        super(TextQuestionSerializer, self).update(instance, validated_data)
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance


class CheckQuestionSerializer(BaseQuestionSerializer):
    checked = serializers.BooleanField()
    poll = serializers.CharField(max_length=64)

    def create(self, validated_data):
        return TextQuestion.objects.create(**validated_data)

    def update(self, instance, validated_data):
        super(CheckQuestionSerializer, self).update(instance, validated_data)
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance


class NumberQuestionSerializer(BaseQuestionSerializer):
    number = serializers.FloatField()
    poll = serializers.CharField(max_length=64)

    def create(self, validated_data):
        return TextQuestion.objects.create(**validated_data)

    def update(self, instance, validated_data):
        super(NumberQuestionSerializer, self).update(instance, validated_data)
        instance.number = validated_data.get('number', instance.number)
        instance.save()
        return instance


class DateQuestionSerializer(BaseQuestionSerializer):
    date = serializers.DateTimeField()
    poll = serializers.CharField(max_length=64)

    def create(self, validated_data):
        return TextQuestion.objects.create(**validated_data)

    def update(self, instance, validated_data):
        super(DateQuestionSerializer, self).update(instance, validated_data)
        instance.date = validated_data.get('date', instance.date)
        instance.save()
        return instance


class FinalQuestionSerializer(BaseQuestionSerializer):
    items = ItemQuestionSerializer(many=True)
    description_mode = serializers.BooleanField(required=False)
    max_video_duration = serializers.IntegerField(required=False)
    is_video = serializers.BooleanField(required=False)

    show_my_answers = serializers.BooleanField(required=False)
    correct_answers = serializers.BooleanField(required=False)
    point_for_answers = serializers.BooleanField(required=False)
    button_mode = serializers.BooleanField(required=False)

    button_text = serializers.CharField(required=False)
    button_url = serializers.CharField(required=False)
    reopen = serializers.BooleanField(required=False)
    poll = serializers.CharField(required=True)

    class Meta:
        model = FinalQuestion
        fields = '__all__'

    def create(self, validated_data):
        question_items = validated_data.pop('items', [])

        final_question = FinalQuestion.objects.create(**validated_data)
        for question_item in question_items:
            final_question.items.add(ItemQuestion.objects.create(**question_item))
        validated_data['items'] = question_items
        return final_question

    def update(self, instance, validated_data):
        super(FinalQuestionSerializer, self).update(instance, validated_data)
        _items = validated_data.get('items', [])
        if _items:
            instance.items.clear()
            for question_item in _items:
                instance.items.add(ItemQuestion.objects.create(**question_item))

        instance.description_mode = validated_data.get('description_mode', instance.description_mode)
        instance.max_video_duration = validated_data.get('max_video_duration', instance.max_video_duration)
        instance.is_video = validated_data.get('is_video', instance.is_video)

        instance.show_my_answers = validated_data.get('show_my_answers', instance.show_my_answers)
        instance.correct_answers = validated_data.get('correct_answers', instance.correct_answers)
        instance.point_for_answers = validated_data.get('point_for_answers', instance.point_for_answers)
        instance.button_mode = validated_data.get('button_mode', instance.button_mode)

        instance.button_text = validated_data.get('button_text', instance.button_text)
        instance.button_url = validated_data.get('button_url', instance.button_url)
        instance.reopen = validated_data.get('reopen', instance.reopen)
        instance.save()
        return instance


class HeadingQuestionSerializer(serializers.ModelSerializer):
    poll = serializers.CharField(max_length=64)

    class Meta:
        model = HeadingQuestion
        fields = [
            'caption',
            'question_id',
            'question_type',
            'order_id',
            'poll',
            'parent_id'
        ]


class PageQuestionSerializer(serializers.ModelSerializer):
    poll = serializers.CharField(max_length=64)

    class Meta:
        model = PageQuestion
        fields = [
            'caption',
            'question_id',
            'question_type',
            'order_id',
            'poll',
            'parent_id',
            'page_id'
        ]


class SectionQuestionSerializer(serializers.ModelSerializer):
    poll = serializers.CharField(max_length=64)

    class Meta:
        model = SectionQuestion
        fields = [
            'caption',
            'question_id',
            'question_type',
            'order_id',
            'poll',
            'parent_id',
            'section_id'
        ]


class ItemTagsFreeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemTagsFreeAnswer
        fields = ['id', 'tag']

    def create(self, validated_data):
        tag_name = validated_data['tag']
        item = self.context.get('item', None)
        if item:
            tag = item.tags.filter(tag=tag_name).first()
            if not tag:
                tag = ItemTagsFreeAnswer.objects.create(tag=tag_name)
                item.tags.add(tag)
        else:
            tag = ItemTagsFreeAnswer.objects.create(tag=tag_name)
        return tag


class ItemsFreeAnswerSerializer(serializers.ModelSerializer):
    tagsAnswerFreeItem = ItemTagsFreeAnswerSerializer(many=True, required=False)
    typeAnswerRow = serializers.CharField(source='type_answer_row', required=False)

    class Meta:
        model = ItemsFreeAnswer
        fields = [
            'item_question_id', 'order_id', 'text',
            'checked', 'photo_path', 'selected', 'points',
            'count_of_input', 'tagsAnswerFreeItem', 'typeAnswerRow'
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tagsAnswerFreeItem', [])
        item = ItemsFreeAnswer.objects.create(**validated_data)

        for tag in tags:
            item.tags.add(ItemTagsFreeAnswer.objects.create(**tag))
        item.save()
        validated_data['tags'] = TagsFreeAnswerSerializer(item.tags.all(), many=True).data
        return item

    def to_representation(self, instance):
        resp = super(ItemsFreeAnswerSerializer, self).to_representation(instance)
        if 'tagsAnswerFreeItem' not in resp:
            resp['tagsAnswerFreeItem'] = TagsFreeAnswerSerializer(instance.tags.all(), many=True).data
        return resp


class FreeAnswerAttachedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeAnswerAttachedType
        fields = [
            'attached_id', 'type', 'active'
        ]


class TagsFreeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagsFreeAnswer
        fields = ['id', 'tag']

    def create(self, validated_data):
        tag_name = validated_data['tag']
        question = self.context['question']

        tag = question.tags.filter(tag=tag_name).first()
        if not tag:
            tag = TagsFreeAnswer.objects.create(tag=tag_name)
            question.tags.add(tag)
        return tag


class FreeAnswerSerializer(BaseQuestionSerializer):
    answer_time = serializers.IntegerField(default=0)
    description_mode = serializers.BooleanField(required=False)
    attached_type = FreeAnswerAttachedTypeSerializer(many=True, required=False)
    items = ItemsFreeAnswerSerializer(many=True, required=False)
    tagsAnswerFree = TagsFreeAnswerSerializer(many=True, required=False, source='tags')
    poll = serializers.CharField(max_length=64)

    class Meta:
        model = FreeAnswer
        fields = [
            'question_type', 'order_id', 'description', 'poll', 'caption',
            'require', 'mix_answers', 'time_for_answer', 'type_for_show', 'title_image', 'resize_image', 'test_mode',
            'answer_time', 'description_mode', 'attached_type', 'items', 'tagsAnswerFree', 'parent_id'
        ]

    def create(self, validated_data):
        question_items = validated_data.pop('items', [])
        question_attached_type = validated_data.pop('attached_type', [])
        tags = validated_data.pop('tagsAnswerFree', [])

        free_answer = FreeAnswer.objects.create(**validated_data)
        for question_item in question_items.copy():
            question_item['type_answer_row'] = question_item.pop('typeAnswerRow', '')
            free_answer.items.add(ItemsFreeAnswer.objects.create(**question_item))

        for attached_type in question_attached_type:
            free_answer.attached_type.add(FreeAnswerAttachedType.objects.create(**attached_type))

        for tag in tags:
            free_answer.tags.add(TagsFreeAnswer.objects.create(**tag))

        validated_data['items'] = ItemsFreeAnswerSerializer(free_answer.items.all(), many=True).data
        validated_data['attached_type'] = FreeAnswerAttachedTypeSerializer(free_answer.attached_type.all(),
                                                                           many=True).data
        validated_data['tags'] = TagsFreeAnswerSerializer(free_answer.tags.all(), many=True).data
        return free_answer

    def update(self, instance, validated_data):
        super(FreeAnswerSerializer, self).update(instance, validated_data)

        _items = validated_data.get('items', [])
        if _items:
            instance.items.clear()
            instance.update_or_create_items(_items)

        _attached_type = validated_data.get('attached_type', [])
        if _attached_type:
            instance.attached_type.clear()
            instance.update_or_create_attached_type(_attached_type)

        instance.description_mode = validated_data.get('description_mode', instance.description_mode)
        instance.answer_time = validated_data.get('answer_time', instance.answer_time)
        instance.save()
        return instance
