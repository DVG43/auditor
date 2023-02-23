import json
import pytest
from django.forms.models import model_to_dict
from model_bakery import baker

from poll.models.poll import Poll
from poll.models.questions import DivisionQuestion, YesNoQuestion, ManyFromListQuestion, TextQuestion, RatingQuestion, \
    MediaQuestion, FinalQuestion, FreeAnswer
from user.models import User


def get_valid_data(data):
    return {
            'DivisionQuestion': data.division_question,
            'YesNoQuestion': data.yes_no_question,
            'ManyFromListQuestion': data.many_from_list_question,
            'TextQuestion': data.text_question,
            'RatingQuestion': data.rating_question,
            'MediaQuestion': data.media_question,
            'FinalQuestion': data.final_question,
            'FreeAnswer': data.free_answer,
        }


def create_question_test(model_name, client, data, poll):
    question_data = {
        'DivisionQuestion': data.division_question,
        'YesNoQuestion': data.yes_no_question,
        'ManyFromListQuestion': data.many_from_list_question,
        'TextQuestion': data.text_question,
        'RatingQuestion': data.rating_question,
        'MediaQuestion': data.media_question,
        'FinalQuestion': data.final_question,
        'FreeAnswer': data.free_answer,
    }
    question_data = question_data[model_name]
    response = client.post(
        f'/v1/polls/{poll.pk}/questions/',
        json.dumps(question_data),
        content_type='application/json'
    )
    response_data = response.json()['result']
    return response.status_code, response_data


def create_question_test_with_reletions(client, question_data, poll, model, item_keys, attached_type_keys=None):
    response = client.post(
        f'/v1/polls/{poll.pk}/questions/',
        json.dumps(question_data),
        content_type='application/json'
    )
    response_data = response.json()['result']
    question_object = model.objects.get(pk=response_data['question_id'])

    obtained_data = model_to_dict(
        question_object,
        fields=question_data.keys()
    )
    obtained_data['items'] = []
    for item in question_object.items.all():
        obtained_data['items'].append(
            model_to_dict(
                item,
                fields=item_keys
            )
        )
    if attached_type_keys is not None:
        obtained_data['attached_type'] = []
        for item in question_object.attached_type.all():
            obtained_data['attached_type'].append(
                model_to_dict(
                    item,
                    fields=attached_type_keys
                )
            )
    return obtained_data


@pytest.mark.django_db
@pytest.mark.parametrize('model', [
    'DivisionQuestion',
    'YesNoQuestion',
    'ManyFromListQuestion',
    'TextQuestion',
    'RatingQuestion',
    'MediaQuestion',
    'FinalQuestion',
    'FreeAnswer'
])
class TestCreateQuestion:
    def test_post_create_question(self, model, get_user_client, create_question_data):
        author = baker.make(User, email='test@test.com')
        poll = baker.make(Poll, user=author)
        client = get_user_client(author)

        status_code, obtained_data = create_question_test(
            model_name=model,
            client=client,
            data=create_question_data,
            poll=poll
        )

        valid_data = get_valid_data(data=create_question_data)[model]
        valid_data['question_id'] = obtained_data['question_id']
        obtained_data.pop('order_id', None)
        obtained_data.pop('tagsAnswerFree', None)
        assert valid_data == obtained_data


@pytest.mark.django_db
class TestCreateQuestionWithReletions:
    @pytest.mark.usefixtures('create_user', 'get_user_client', 'create_poll', 'create_question_data', 'create_item_data')
    def test_post_create_manyfromlistquestion_reletions(self, create_user, get_user_client, create_poll, create_question_data,
                                                 create_item_data):
        model = ManyFromListQuestion
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        question_data = create_question_data.many_from_list_question
        item_question = create_item_data.item_question

        question_data['items'] = [item_question]
        obtained_data = create_question_test_with_reletions(
            client=client,
            question_data=question_data,
            poll=poll,
            model=model,
            item_keys=item_question.keys()
        )
        valid_data = question_data
        assert valid_data == obtained_data

    @pytest.mark.usefixtures('create_user', 'get_user_client', 'create_poll', 'create_question_data', 'create_item_data')
    def test_post_create_final_question_reletions(self, create_user, get_user_client, create_poll, create_question_data,
                                                 create_item_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        question_data = create_question_data.final_question
        item_question = create_item_data.item_question
        model = FinalQuestion

        question_data['items'] = [item_question]
        obtained_data = create_question_test_with_reletions(
            client=client,
            question_data=question_data,
            poll=poll,
            model=model,
            item_keys=item_question.keys()
        )
        valid_data = question_data
        assert valid_data == obtained_data

    @pytest.mark.usefixtures('create_user', 'get_user_client', 'create_poll', 'create_question_data',
                             'create_item_data')
    def test_post_create_media_question_reletions(self, create_user, get_user_client, create_poll, create_question_data,
                                        create_item_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        question_data = create_question_data.media_question
        item_question = create_item_data.media_item_question
        attached_type = create_item_data.media_attached_type
        model = MediaQuestion

        question_data['items'] = [item_question]
        question_data['attached_type'] = [attached_type]
        obtained_data = create_question_test_with_reletions(
            client=client,
            question_data=question_data,
            poll=poll,
            model=model,
            item_keys=item_question.keys(),
            attached_type_keys=attached_type.keys()
        )
        valid_data = question_data
        assert valid_data == obtained_data

    @pytest.mark.usefixtures('create_user', 'get_user_client', 'create_poll', 'create_question_data',
                             'create_item_data')
    def test_post_create_yes_no_question_reletions(self, create_user, get_user_client, create_poll, create_question_data,
                                        create_item_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        question_data = create_question_data.yes_no_question
        item_question = create_item_data.item_question
        attached_type = create_item_data.yes_no_attached_type
        model = YesNoQuestion

        question_data['items'] = [item_question]
        question_data['attached_type'] = [attached_type]
        obtained_data = create_question_test_with_reletions(
            client=client,
            question_data=question_data,
            poll=poll,
            model=model,
            item_keys=item_question.keys(),
            attached_type_keys=attached_type.keys()
        )
        valid_data = question_data
        assert valid_data == obtained_data

    @pytest.mark.usefixtures('create_user', 'get_user_client', 'create_poll', 'create_question_data',
                             'create_item_data')
    def test_create_free_answer_reletions(self, create_user, get_user_client, create_poll,
                                                   create_question_data,
                                                   create_item_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        question_data = create_question_data.free_answer
        item_question = create_item_data.items_free_answer
        attached_type = create_item_data.free_answer_attached_type
        model = FreeAnswer

        question_data['items'] = [item_question]
        question_data['attached_type'] = [attached_type]
        obtained_data = create_question_test_with_reletions(
            client=client,
            question_data=question_data,
            poll=poll,
            model=model,
            item_keys=item_question.keys(),
            attached_type_keys=attached_type.keys()
        )

        valid_data = question_data
        assert valid_data == obtained_data
