from django.contrib import admin

from poll.models.analitics import PollAnalitics
from poll.models.surveypassing import SurveyPassing
from poll.models.poll import Poll, PollTags
from poll.models.questions import ItemQuestion
from poll.models.answer import UserAnswerQuestion


class PollAnaliticsModelAdmin(admin.ModelAdmin):
	list_display = ('id', 'poll_id', 'avarage_age', 'men_total',
	                'women_total', 'women_before_18', 'men_before_18',
	                'women_in_18_24', 'men_in_18_24', 'women_in_25_35',
	                'men_in_25_35', 'women_in_36_45', 'men_in_36_45', 
	                'women_older_46', 'men_older_46', 'from_desktop',
	                'from_mobile', 'from_other')
	list_display_links = ('id', )
	class Meta:
		model = PollAnalitics


class SurveyPassingModelAdmin(admin.ModelAdmin):
	list_display = ('id', 'poll', 'user', 'sex', 'platform', 'age')
	list_display_links = ('id', )
	class Meta:
		model = SurveyPassing


class PollAdmin(admin.ModelAdmin):
    list_display = ('owner', 'id', 'name', 'count_answers')


class PollTagsAdmin(admin.ModelAdmin):
    list_display = ('tag_id', 'name')


class ItemQuestionAdmin(admin.ModelAdmin):
    list_display = ('item_question_id', )


class UserAnswerQuestionAdmin(admin.ModelAdmin):
    list_display = ('survey', 'poll_id', 'question_id')


admin.site.register(UserAnswerQuestion, UserAnswerQuestionAdmin)
admin.site.register(ItemQuestion, ItemQuestionAdmin)
admin.site.register(PollTags, PollTagsAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(PollAnalitics, PollAnaliticsModelAdmin)
admin.site.register(SurveyPassing, SurveyPassingModelAdmin)


# """
# Provide configuration for admin panel poll tables.
# """

# from poll.models.poll import Poll, PollSettings
# from poll.models.questions import DivisionQuestion, ItemQuestion, ManyFromListQuestion, MediaFile, MediaQuestion, \
#     OneFromListQuestion, RatingQuestion, TextQuestion, MediaItemQuestion, MediaAttachedType
# class PollAdmin(admin.ModelAdmin):
#     list_display = ('user', 'poll_id', 'title', 'count_answers')
#     search_fields = ('user__email', 'poll_id', 'title')
#     list_filter = ('test_mode_global',)
#
#
# class PollQuestionAdmin(admin.ModelAdmin):
#     search_fields = ('poll__user__email',)
#
#
# class QuestionAdmin(admin.ModelAdmin):
#     search_fields = ('poll__user__email', 'caption', 'title_image', 'order_id', 'description', 'question_type', 'poll__title')
#     list_display = ('caption', 'poll', 'question_type', 'order_id', )
#     list_filter = ('require', 'mix_answers', 'time_for_answer', 'test_mode')
#
#
# class MediaFileAdmin(admin.ModelAdmin):
#     search_fields = ('file_id', 'path_to_file')
#     list_display = ('path_to_file', 'file_id')
#
#
# class MediaQuestionAdmin(admin.ModelAdmin):
#     list_filter = ('description_mode', 'is_video', 'resize_image')
#
#
# class PollSettingsAdmin(admin.ModelAdmin):
#     list_display = ('poll',)
#     search_fields = ('poll__user__email', 'poll__title')
#     list_filter = ('isFormActive', 'mixQuestions', 'showProgress',
#     'allowRefillingForm',
#     'usePassword',
#     'showAnalytics',
#     'showCorrectAnswers',
#     'showWrongAnswers',
#     'askLocation'
#     )
#
#
# class ItemQuestionAdmin(admin.ModelAdmin):
#     search_fields = ('order_id', 'text',)
#     list_display = ('order_id', 'points', 'text')
#     list_filter = ('checked', 'selected')
#
#
# class RatingQuestionAdmin(admin.ModelAdmin):
#     search_fields = ('poll__user__email', 'caption', 'title_image', 'order_id', 'description', 'question_type', 'poll__title', 'rating')
#     list_display = ('caption', 'poll', 'question_type', 'order_id', 'rating')
#     list_filter = ('require', 'mix_answers', 'time_for_answer', 'test_mode')
#
#
# class MediaAttachedTypeAdmin(admin.ModelAdmin):
#     search_fields = ('type', 'count', 'symbols', 'duration', 'size')
#     list_display = ('type', 'count', 'duration', 'symbols', 'size')
#     list_filter = ('active',)
#
#
# class MediaItemQuestionAdmin(admin.ModelAdmin):
#     search_fields = ('media_question_id', 'points')
#     list_display = ('media_question_id', 'points')
#
#
# admin.site.register(Poll, PollAdmin)
# admin.site.register(PollSettings, PollSettingsAdmin)
# admin.site.register(DivisionQuestion, QuestionAdmin)
# admin.site.register(ItemQuestion, ItemQuestionAdmin)
# admin.site.register(ManyFromListQuestion, QuestionAdmin)
# admin.site.register(MediaFile, MediaFileAdmin)
# admin.site.register(MediaQuestion, QuestionAdmin)
# admin.site.register(OneFromListQuestion, QuestionAdmin)
# admin.site.register(RatingQuestion, RatingQuestionAdmin)
# admin.site.register(TextQuestion, QuestionAdmin)
# admin.site.register(MediaAttachedType, MediaAttachedTypeAdmin)
# admin.site.register(MediaItemQuestion, MediaItemQuestionAdmin)
