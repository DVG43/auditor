import uuid

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone


class ItemBase:
    @staticmethod
    def normalize_order_id(query_set):
        items = []
        for i, v in enumerate(query_set.all(), start=1):
            v.order_id = i
            items.append(v)
        ItemQuestion.objects.bulk_update(items, ["order_id"])
        return query_set


class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=100, default='Question')
    parent_id = models.UUIDField(null=True, blank=True)
    order_id = models.IntegerField(default=0)
    description = models.CharField(max_length=512, null=True, blank=True, default='')
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)
    caption = models.CharField(max_length=255, null=True, blank=True, default='')

    # Необязательные поля
    require = models.BooleanField(default=False)
    mix_answers = models.BooleanField(default=False)
    time_for_answer = models.BooleanField(default=False)
    type_for_show = models.IntegerField(default=0)
    title_image = models.CharField(max_length=512, default='')
    resize_image = models.BooleanField(default=False)
    test_mode = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        ordering = ['order_id', '-updated_at']

    def _update_or_related_objects(self, objects_list, related_name, primary_key_name, model):
        for obj in objects_list:
            obj_id = obj.pop(primary_key_name, None)
            obj_id = int(obj_id) if obj_id else None
            obj, created = model.objects.update_or_create(
                pk=obj_id,
                defaults={**obj},
            )
            getattr(self, related_name).add(obj)
        self.save()
        return getattr(self, related_name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, sort=True):
        # if self.poll.telegram_integration_is_active():
        #     self.poll.telegramintegration.update_variable_in_message()

        result = super(Question, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )
        return result

    @staticmethod
    def normalize_order_id(query_set):
        for i, v in enumerate(query_set.all(), start=1):
            v.order_id = i
            v.save()
        return query_set


class PageQuestion(Question):
    """
    Page
    """
    page_id = models.UUIDField(default=uuid.uuid4)

    def __init__(self, *args, **kwargs):
        super(PageQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_question_page'
        verbose_name_plural = 'poll_pages'
        indexes = [
            models.Index(fields=['poll'])
        ]


class SectionQuestion(Question):
    """
    Section
    """
    section_id = models.UUIDField(default=uuid.uuid4)

    def __init__(self, *args, **kwargs):
        super(SectionQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_question_section'
        verbose_name_plural = 'poll_sections'
        indexes = [
            models.Index(fields=['poll'])
        ]


class DivisionQuestion(Question):
    """
    Division
    """
    comment = models.CharField(max_length=512, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(DivisionQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_question_division'
        verbose_name_plural = 'poll_divisions'
        indexes = [
            models.Index(fields=['poll'])
        ]


class ItemSet(models.Model):
    item_set_id = models.AutoField(primary_key=True)
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'poll_item_set'
        verbose_name_plural = 'poll_item_sets'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['poll'])
        ]


class ItemQuestion(models.Model, ItemBase):
    item_question_id = models.AutoField(primary_key=True)
    item_set = models.ForeignKey(ItemSet, on_delete=models.CASCADE, null=True)
    order_id = models.IntegerField(default=0)
    text = models.TextField(default='', blank=True, null=True)
    checked = models.BooleanField(blank=True, null=True, default=False)
    photo_path = models.CharField(max_length=500, default='', blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)
    hex_color = models.CharField(max_length=7, default="#ffffff")
    selected = models.BooleanField(default=False)
    userAnswer = models.BooleanField(default=False)
    userAnswerText = models.TextField(default='')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'poll_question_item'
        verbose_name_plural = 'poll_item_questions'
        ordering = ['order_id', '-updated_at']
        indexes = [
            models.Index(fields=['item_set'])
        ]

    def delete(self, using=None, keep_parents=False):
        yesnoquestion = self.yesnoquestion_set.first()
        finalquestion = self.finalquestion_set.first()
        manyfromlistquestion = self.manyfromlistquestion_set.first()

        result = super(ItemQuestion, self).delete(using=None, keep_parents=False)

        if yesnoquestion:
            self.normalize_order_id(yesnoquestion.items)

        elif finalquestion:
            self.normalize_order_id(finalquestion.items)

        elif manyfromlistquestion:
            self.normalize_order_id(manyfromlistquestion.items)

        return result

    def normalize_order_id_other(self, old_order_id, new_order_id):
        yesnoquestion = self.yesnoquestion_set.first()
        finalquestion = self.finalquestion_set.first()
        manyfromlistquestion = self.manyfromlistquestion_set.first()

        items = None
        if yesnoquestion:
            items = yesnoquestion.items

        elif finalquestion:
            items = finalquestion.items

        elif manyfromlistquestion:
            items = manyfromlistquestion.items

        if items:
            if new_order_id > old_order_id:
                items = items.order_by('order_id', 'updated_at')
            self.normalize_order_id(items)

    def get_question(self):
        yesnoquestion = self.yesnoquestion_set.first()
        if yesnoquestion:
            return yesnoquestion

        finalquestion = self.finalquestion_set.first()
        if finalquestion:
            return finalquestion

        manyfromlistquestion = self.manyfromlistquestion_set.first()
        if manyfromlistquestion:
            return manyfromlistquestion

        return None


class ManyFromListAttachedType(models.Model):
    attached_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=16, default=None, blank=True, null=True)
    active = models.BooleanField(default=False, blank=False, null=False)


class ManyFromListQuestion(Question):
    """
    ManyFromList
    """

    answer_mode_choices = (('ONE', 1),
                           ('SOME', 2),)

    items = models.ManyToManyField(ItemQuestion)
    attached_type = models.ManyToManyField(ManyFromListAttachedType)
    answer_mode = models.IntegerField(choices=answer_mode_choices, default=1)

    # Необязательные поля
    description_mode = models.BooleanField(default=False)
    count_of_answer = models.IntegerField(default=0)
    current_number_value = models.IntegerField(default=None, blank=True, null=True)
    answer_from = models.IntegerField(default=None, blank=True, null=True)
    answer_to = models.IntegerField(default=None, blank=True, null=True)
    answer_time = models.IntegerField(default=0)
    comment = models.CharField(max_length=512, default=None, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(ManyFromListQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_question_many_from_list'
        verbose_name_plural = 'poll_many_from_list'
        indexes = [
            models.Index(fields=['poll'])
        ]


class YesNoAnswers(models.Model):
    textAnswer = models.TextField(default='', blank=True)
    checked = models.BooleanField(default=False)
    points = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'one_from_answer'


class YesNoAttachedType(models.Model):
    attached_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=16, default=None, blank=True, null=True)
    active = models.BooleanField(default=False, blank=False, null=False)
    count = models.PositiveIntegerField(default=0, blank=False, null=False)
    duration = models.IntegerField(default=None, blank=True, null=True)
    symbols = models.PositiveIntegerField(default=None, blank=True, null=True)
    size = models.PositiveIntegerField(default=None, blank=True, null=True)

    class Meta:
        db_table = 'poll_one_from_list_attached_type'


class YesNoQuestion(Question):
    items = models.ManyToManyField(ItemQuestion)
    attached_type = models.ManyToManyField(YesNoAttachedType)
    yes_no_answers = models.ManyToManyField(YesNoAnswers)
    description_mode = models.BooleanField(default=False)
    max_video_duration = models.IntegerField(default=0)
    is_video = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(YesNoQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    def update_or_create_yes_no_answers(self, yes_no_answers):
        return self._update_or_related_objects(
            objects_list=yes_no_answers,
            related_name='yes_no_answers',
            primary_key_name='id',
            model=YesNoAnswers
        )

    def update_or_create_attached_type(self, attached_type):
        return self._update_or_related_objects(
            objects_list=attached_type,
            related_name='attached_type',
            primary_key_name='attached_id',
            model=YesNoAttachedType
        )

    def update_or_create_items(self, items):
        return self._update_or_related_objects(
            objects_list=items,
            related_name='items',
            primary_key_name='item_question_id',
            model=ItemQuestion
        )

    class Meta:
        verbose_name_plural = 'poll_one_from_list'
        indexes = [
            models.Index(fields=['poll'])
        ]


class RatingQuestion(Question):
    """
    Rating
    """
    rating = models.IntegerField(default=0)

    def __init__(self, *args, **kwargs):
        super(RatingQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_question_rating'
        verbose_name_plural = 'poll_rating_questions'
        indexes = [
            models.Index(fields=['poll'])
        ]


class MediaFile(models.Model):
    file_id = models.IntegerField(primary_key=True)
    path_to_file = models.CharField(max_length=2048)

    class Meta:
        db_table = 'poll_media_file'
        verbose_name_plural = 'poll_media_files'


class MediaAttachedType(models.Model):
    media_attached_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=16, default=None, blank=True, null=True)
    active = models.BooleanField(default=False, blank=False, null=False)
    count = models.PositiveIntegerField(default=0, blank=False, null=False)
    duration = models.IntegerField(default=None, blank=True, null=True)
    symbols = models.PositiveIntegerField(default=None, blank=True, null=True)
    size = models.PositiveIntegerField(default=None, blank=True, null=True)

    class Meta:
        db_table = 'poll_media_attached_type'
        verbose_name_plural = 'poll_media_attached_types'


class MediaItemQuestion(models.Model):
    media_question_id = models.AutoField(primary_key=True)
    points = models.PositiveIntegerField(validators=[MaxValueValidator(limit_value=100)], default=0, blank=True,
                                         null=None)

    def get_question(self):
        return self.mediaquestion_set.first()


class MediaQuestion(Question):
    """
    Media
    """
    description_mode = models.BooleanField(default=False)
    max_video_duration = models.IntegerField(default=0, blank=False, null=False)
    is_video = models.BooleanField(default=False)
    attached_type = models.ManyToManyField(MediaAttachedType)
    resize_image = models.BooleanField(default=False)
    items = models.ManyToManyField(MediaItemQuestion)

    def __init__(self, *args, **kwargs):
        super(MediaQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_question_media'
        verbose_name_plural = 'poll_media_questions'
        indexes = [
            models.Index(fields=['poll'])
        ]


class TextQuestion(Question):
    """
    Just Text
    """
    text = models.TextField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(TextQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_question_text'
        verbose_name_plural = 'poll_text_questions'
        indexes = [
            models.Index(fields=['poll'])
        ]


class NumberQuestion(Question):
    """
    Just Number
    """
    number = models.FloatField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(NumberQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_number_question'
        verbose_name_plural = 'poll_number_questions'
        indexes = [
            models.Index(fields=['poll'])
        ]


class DateQuestion(Question):
    """
    Just Date
    """
    date = models.DateTimeField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(DateQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_date_question'
        verbose_name_plural = 'poll_date_questions'
        indexes = [
            models.Index(fields=['poll'])
        ]


class CheckQuestion(Question):
    """
    Just bool Checkbox question
    """
    checked = models.BooleanField(blank=True, null=True, default=False)
    points = models.IntegerField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(CheckQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_check_question'
        verbose_name_plural = 'poll_check_questions'
        indexes = [
            models.Index(fields=['poll'])
        ]


class FinalQuestion(Question):
    description_mode = models.BooleanField(default=False)
    max_video_duration = models.IntegerField(default=0, blank=False, null=False)
    is_video = models.BooleanField(default=False)
    items = models.ManyToManyField(ItemQuestion)

    show_my_answers = models.BooleanField(default=False)
    correct_answers = models.BooleanField(default=False)
    point_for_answers = models.BooleanField(default=False)
    button_mode = models.BooleanField(default=False)
    button_text = models.CharField(max_length=512, default='', blank=True, null=True)
    button_url = models.CharField(max_length=512, default='', blank=True, null=True)
    reopen = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(FinalQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'poll_final_question'
        verbose_name_plural = 'poll_final_questions'
        indexes = [
            models.Index(fields=['poll'])
        ]


class HeadingQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=100, default='Question')
    caption = models.CharField(max_length=100)
    order_id = models.IntegerField(default=0)
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)
    parent_id = models.UUIDField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __init__(self, *args, **kwargs):
        super(HeadingQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__


class FreeAnswerAttachedType(models.Model):
    attached_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=16, default=None, blank=True, null=True)
    active = models.BooleanField(default=False, blank=False, null=False)


class ItemTagsFreeAnswer(models.Model):
    tag = models.CharField(max_length=100)

    def __str__(self):
        return self.tag


class ItemsFreeAnswer(models.Model):
    item_question_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default=0)
    text = models.TextField(default='', blank=True, null=True)
    checked = models.BooleanField(default=False)
    photo_path = models.CharField(max_length=500, default='', blank=True, null=True)
    count_of_input = models.IntegerField(default=0, blank=True, null=True)
    selected = models.BooleanField(default=False)
    points = models.IntegerField(blank=True, null=True)
    type_answer_row = models.CharField(max_length=255, blank=True, null=True)
    tags = models.ManyToManyField(ItemTagsFreeAnswer)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order_id', '-updated_at']

    @staticmethod
    def normalize_order_id(query_set):
        items = []
        for i, v in enumerate(query_set.all(), start=1):
            v.order_id = i
            items.append(v)
        ItemsFreeAnswer.objects.bulk_update(items, ["order_id"])
        return query_set

    def delete(self, using=None, keep_parents=False):
        freeanswer = self.freeanswer_set.first()
        result = super(ItemsFreeAnswer, self).delete(using=None, keep_parents=False)

        if freeanswer:
            self.normalize_order_id(freeanswer.items)
        return result

    def normalize_order_id_other(self, old_order_id, new_order_id):
        freeanswer = self.freeanswer_set.first()

        items = None
        if freeanswer:
            items = freeanswer.items

        if items:
            if new_order_id > old_order_id:
                items = items.order_by('order_id', 'updated_at')
            self.normalize_order_id(items)

    def get_question(self):
        return self.freeanswer_set.first()


class TagsFreeAnswer(models.Model):
    tag = models.CharField(max_length=100)

    def __str__(self):
        return self.tag


class FreeAnswer(Question):
    answer_time = models.IntegerField(default=0)
    description_mode = models.BooleanField(default=False)
    attached_type = models.ManyToManyField(FreeAnswerAttachedType)
    items = models.ManyToManyField(ItemsFreeAnswer)
    tags = models.ManyToManyField(TagsFreeAnswer)

    def __init__(self, *args, **kwargs):
        super(FreeAnswer, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        indexes = [
            models.Index(fields=['poll'])
        ]

    def update_or_create_items(self, items):
        return self._update_or_related_objects(
            objects_list=items,
            related_name='items',
            primary_key_name='item_question_id',
            model=ItemsFreeAnswer
        )

    def update_or_create_attached_type(self, attached_types):
        return self._update_or_related_objects(
            objects_list=attached_types,
            related_name='attached_type',
            primary_key_name='attached_id',
            model=FreeAnswerAttachedType
        )
