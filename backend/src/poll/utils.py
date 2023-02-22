from poll.models.questions import DivisionQuestion, ManyFromListQuestion, YesNoQuestion, RatingQuestion, TextQuestion, \
    MediaQuestion, FinalQuestion, HeadingQuestion, FreeAnswer, ItemQuestion, MediaItemQuestion, ItemsFreeAnswer, \
    TagsFreeAnswer, YesNoAttachedType, MediaAttachedType, FreeAnswerAttachedType, YesNoAnswers, ManyFromListAttachedType
from poll.serializers import questions as questions_serializers_v1
from poll.serializers_v2 import questions as questions_serializers_v2

USER_ROLE = [
    ('redactor', 'Redactor'),
    ('view_responses', 'view_responses'),
    ('author', 'Author')
]
REDACTOR = 'redactor'
VIEW_RESPONSES = 'view_responses'
AUTHOR = 'author'

USER_ACCESS_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# QUESTIONS CLASSES

QUESTION_MODELS = {
    'DivisionQuestion': DivisionQuestion,
    'ManyFromListQuestion': ManyFromListQuestion,
    'YesNoQuestion': YesNoQuestion,
    'RatingQuestion': RatingQuestion,
    'TextQuestion': TextQuestion,
    'MediaQuestion': MediaQuestion,
    'FinalQuestion': FinalQuestion,
    'HeadingQuestion': HeadingQuestion,
    'FreeAnswer': FreeAnswer
}

QUESTION_SERIALIZERS_V1 = {
    'DivisionQuestion': questions_serializers_v1.DivisionQuestionSerializer,
    'ManyFromListQuestion': questions_serializers_v1.ManyFromListQuestionSerializer,
    'YesNoQuestion': questions_serializers_v1.YesNoQuestionSerializer,
    'RatingQuestion': questions_serializers_v1.RatingQuestionSerializer,
    'TextQuestion': questions_serializers_v1.TextQuestionSerializer,
    'MediaQuestion': questions_serializers_v1.MediaQuestionSerializer,
    'FinalQuestion': questions_serializers_v1.FinalQuestionSerializer,
    'HeadingQuestion': questions_serializers_v1.HeadingQuestionSerializer,
    'FreeAnswer': questions_serializers_v1.FreeAnswerSerializer
}

QUESTION_SERIALIZERS_V2 = {
    'DivisionQuestion': questions_serializers_v2.DivisionQuestionSerializer,
    'ManyFromListQuestion': questions_serializers_v2.ManyFromListQuestionSerializer,
    'YesNoQuestion': questions_serializers_v2.YesNoQuestionSerializer,
    'RatingQuestion': questions_serializers_v2.RatingQuestionSerializer,
    'TextQuestion': questions_serializers_v2.TextQuestionSerializer,
    'MediaQuestion': questions_serializers_v2.MediaQuestionSerializer,
    'FinalQuestion': questions_serializers_v2.FinalQuestionSerializer,
    'HeadingQuestion': questions_serializers_v2.HeadingQuestionSerializer,
    'FreeAnswer': questions_serializers_v2.FreeAnswerSerializer
}

# SUB QUESTIONS CLASSES

ITEM_MODELS = {
    'ManyFromListQuestion': ItemQuestion,
    'YesNoQuestion': ItemQuestion,
    'MediaQuestion': MediaItemQuestion,
    'FinalQuestion': ItemQuestion,
    'FreeAnswer': ItemsFreeAnswer
}

ITEM_SERIALIZERS_V2 = {
    'ManyFromListQuestion': questions_serializers_v2.ItemQuestionSerializer,
    'YesNoQuestion': questions_serializers_v2.ItemQuestionSerializer,
    'MediaQuestion': questions_serializers_v2.MediaItemQuestionSerializer,
    'FinalQuestion': questions_serializers_v2.ItemQuestionSerializer,
    'FreeAnswer': questions_serializers_v2.ItemsFreeAnswerSerializer
}


ATTACHED_TYPE_MODELS = {
    'YesNoQuestion': YesNoAttachedType,
    'MediaQuestion': MediaAttachedType,
    'FreeAnswer': FreeAnswerAttachedType,
    'ManyFromListQuestion': ManyFromListAttachedType
}

ATTACHED_TYPE_SERIALIZERS_V2 = {
    'YesNoQuestion': questions_serializers_v2.YesNoAttachedTypeSerializer,
    'MediaQuestion': questions_serializers_v2.MediaAttachedTypeSerializer,
    'FreeAnswer': questions_serializers_v2.FreeAnswerAttachedTypeSerializer
}

TAGS_QUESTION_MODELS = {
    'FreeAnswer': TagsFreeAnswer
}

ANSWERS_QUESTIONS = {
    'YesNoQuestion': YesNoAnswers
}
