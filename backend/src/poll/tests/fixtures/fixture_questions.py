import pytest


class CreateQuestionData:
    base_question = {
        # 'order_id': 22,
        'description': 'test description',
        'caption': 'caption title',
        'require': True,
        'mix_answers': True,
        'time_for_answer': True,
        'type_for_show': 22,
        'title_image': 'title image',
        'resize_image': True,
        'test_mode': True
    }
    division_question = {
        'comment': 'test',
        'question_type': 'DivisionQuestion',
        **base_question
    }
    yes_no_question = {
        'items': [],
        'attached_type': [],
        'yes_no_answers': [],
        'description_mode': True,
        'max_video_duration': 2,
        'is_video': True,
        'question_type': 'YesNoQuestion',
        **base_question
    }
    many_from_list_question = {
        'items': [],
        'description_mode': True,
        'count_of_answer': 3,
        'current_number_value': 3,
        'answer_from': 2,
        'answer_to': 2,
        'answer_time': 3,
        'comment': 'test comment',
        'question_type': 'ManyFromListQuestion',
        **base_question
    }
    text_question = {
        'text': 'text question',
        'question_type': 'TextQuestion',
        **base_question
    }
    final_question = {
        'description_mode': True,
        'max_video_duration': 12,
        'is_video': True,
        'items': [],

        'show_my_answers': True,
        'correct_answers': True,
        'point_for_answers': True,
        'button_mode': True,
        'button_text': 'test text',
        'button_url': 'button-url',
        'question_type': 'FinalQuestion',
        **base_question
    }
    rating_question = {
        'rating': 3,
        'question_type': 'RatingQuestion',
        **base_question
    }
    media_question = {
        'description_mode': True,
        'max_video_duration': 12,
        'is_video': True,
        'attached_type': [],
        'items': [],
        'resize_image': True,
        'question_type': 'MediaQuestion',
        **base_question
    }
    free_answer = {
        'items': [],
        'attached_type': [],
        'description_mode': True,
        'answer_time': 2,
        'question_type': 'FreeAnswer',
        **base_question
    }


class UpdateQuestionData:
    base_question = {
        # 'order_id': 33,
        'description': 'test new description',
        'caption': 'caption new title',
        'require': False,
        'mix_answers': False,
        'time_for_answer': False,
        'type_for_show': 33,
        'title_image': 'title new image',
        'resize_image': False,
        'test_mode': False
    }
    division_question = {
        'comment': 'new test',
        'question_type': 'DivisionQuestion',
        **base_question,
    }
    yes_no_question = {
        # 'items': [],
        # 'attached_type': [],
        # 'yes_no_answers': [],
        'description_mode': False,
        'max_video_duration': 3,
        'is_video': False,
        'question_type': 'YesNoQuestion',
        **base_question,
    }
    many_from_list_question = {
        'description_mode': False,
        'count_of_answer': 11,
        'current_number_value': 33,
        'answer_from': 22,
        'answer_to': 22,
        'answer_time': 33,
        'comment': 'test new comment',
        'question_type': 'ManyFromListQuestion',
        **base_question,
    }
    text_question = {
        'text': 'text new question',
        'question_type': 'TextQuestion',
        **base_question,
    }
    final_question = {
        'description_mode': False,
        'max_video_duration': 33,
        'is_video': False,
        # 'items': [],

        'show_my_answers': False,
        'correct_answers': False,
        'point_for_answers': False,
        'button_mode': False,
        'button_text': 'test new text',
        'button_url': 'new-button-url',
        'question_type': 'FinalQuestion',
        **base_question,
    }
    rating_question = {
        'rating': 33,
        'question_type': 'RatingQuestion',
    }
    media_question = {
        'description_mode': False,
        'max_video_duration': 22,
        'is_video': False,
        # 'attached_type': [],
        # 'items': [],
        'resize_image': False,
        'question_type': 'MediaQuestion',
        **base_question,
    }
    free_answer = {
        # 'items': [],
        # 'attached_type': [],
        'description_mode': True,
        'answer_time': 5,
        'question_type': 'FreeAnswer',
        **base_question
    }

@pytest.fixture
def create_question_data():
    return CreateQuestionData

@pytest.fixture
def update_question_data():
    return UpdateQuestionData

@pytest.fixture
def create_question():
    def make_question(poll, question_data, question_model):
        question_data.pop('items', None)
        question_data.pop('attached_type', None)
        question_data.pop('yes_no_answers', None)
        return question_model.objects.create(
            poll=poll,
            **question_data
        )
    return make_question
