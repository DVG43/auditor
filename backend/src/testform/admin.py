from django.contrib import admin

from testform.models import (
    TestForm,
    TestFormQuestion,
    BaseTFQuestion,
    FinalTFQuestion,
)


class BaseTFQuestionInline(admin.TabularInline):
    model = BaseTFQuestion
    extra = 0
    fields = ('order_id', 'max_time', 'type_answer')

    def has_add_permission(self, request, obj):
        if obj.tfquestiontype_set.count():
            return False
        return True


class FinalTFQuestionInline(admin.TabularInline):
    model = FinalTFQuestion
    extra = 0
    fields = ('order_id', 'answer', )
    readonly_fields = ('order_id', )

    def has_add_permission(self, request, obj):
        if obj.tfquestiontype_set.count():
            return False
        return True


@admin.register(TestForm)
class TestFormAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "time_to_answer")
    search_fields = ("name", "owner")


@admin.register(TestFormQuestion)
class TestFormQuestionQuestionAdmin(admin.ModelAdmin):
    list_display = ("question_id", "question_type", "testform", "caption")
    search_fields = ("testform", )
    inlines = [FinalTFQuestionInline, BaseTFQuestionInline]
