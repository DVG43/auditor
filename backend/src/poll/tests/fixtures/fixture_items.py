import pytest


class CreateItemData:
    item_question = {
        'order_id': 1,
        'text': 'text',
        'checked': False,
        'photo_path': 'photo_path',
        'points': 1,
        'selected': False,
        'userAnswer': False,
        'userAnswerText': 'text',
    }
    media_item_question = {
        'points': 1
    }
    # TODO add tests for the typeAnswerRow field
    items_free_answer = {
        "order_id": 1,
        # "typeAnswerRow": "text",
        "text": "text",
        "checked": False,
        "selected": False,
        "points": False
    }
    yes_no_attached_type = {
        'type': 'text',
        'active': True,
        'count': 1,
        'duration': 1,
        'symbols': 1,
        'size': 1,
    }
    free_answer_attached_type = {
        'type': 'test',
        'active': True
    }
    media_attached_type = {
        'type': 'text',
        'active': True,
        'count': 1,
        'duration': 1,
        'symbols': 1,
        'size': 1,
    }


class UpdateItemData:
    item_question = {
        'order_id': 1,
        'text': '1asf111',
        'checked': True,
        'photo_path': 'photo_path11',
        'points': 11,
        'selected': True,
        'userAnswer': True,
        'userAnswerText': 'text111',
    }
    media_item_question = {
        'points': 2
    }
    # TODO add tests for the typeAnswerRow field
    items_free_answer = {
        "order_id": 1,
        # "typeAnswerRow": "text",
        "text": "text",
        "checked": False,
        "selected": False,
        "points": False
    }
    yes_no_attached_type = {
        'type': 'text',
        'active': True,
        'count': 1,
        'duration': 1,
        'symbols': 1,
        'size': 1,
    }
    free_answer_attached_type = {
        'type': 'test',
        'active': True
    }
    media_attached_type = {
        'type': 'text',
        'active': True,
        'count': 1,
        'duration': 1,
        'symbols': 1,
        'size': 1,
    }


@pytest.fixture
def create_item_data():
    return CreateItemData

@pytest.fixture
def update_item_data():
    return UpdateItemData
