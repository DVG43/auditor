from django.contrib import admin

from testform.models import TestForm, BaseTFQuestion, TestFormQuestion, FinalTFQuestion


@admin.register(TestForm)
class TestFormAdmin(admin.ModelAdmin):
    list_display = ("name", )


@admin.register(TestFormQuestion)
class TFQuestionAdmin(admin.ModelAdmin):
    list_display = ("question_id", 'caption')


@admin.register(BaseTFQuestion)
class BaseTFQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", 'type_answer', 'tfquestiontype_ptr_id', 'order_id')


@admin.register(FinalTFQuestion)
class FinalTFQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", 'answer')
