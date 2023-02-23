import json
import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from poll.utils import QUESTION_MODELS, REDACTOR, VIEW_RESPONSES, AUTHOR
from poll.models.poll import Poll
from poll.models.user_access import UserAccess
from user.models import User


def update_question_request(client, poll_author, model_name, data, poll=None):
    model = QUESTION_MODELS[model_name]
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
    if not poll:
        poll = baker.make(Poll, user=poll_author)
    question = baker.make(model, poll=poll)

    response = client.put(
        f'/v1/polls/questions/{question.pk}/{model_name}/',
        json.dumps(question_data),
        content_type='application/json'
    )
    return response.status_code


def delete_question_request(client, poll_author, model_name, poll=None):
    model = QUESTION_MODELS[model_name]

    if not poll:
        poll = baker.make(Poll, user=poll_author)
    question = baker.make(model, poll=poll)

    response = client.delete(
        f'/v1/polls/questions/{question.pk}/{model_name}/',
        content_type='application/json'
    )
    return response.status_code


def get_question_request(client, poll_author, model_name, poll=None):
    model = QUESTION_MODELS[model_name]
    if not poll:
        poll = baker.make(Poll, user=poll_author)
    question = baker.make(model, poll=poll)
    response = client.get(
        f'/v1/polls/questions/{question.pk}/{model_name}/',
        content_type='application/json'
    )
    return response.status_code


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
class TestQuestionPermission:
    def test_update_question_NOT_AUTHOR_permission_403(
            self, model, get_user_client, update_question_data):
        not_author = baker.make(User, email='author@test.com')
        author = baker.make(User, email='notauthor@test.com')

        client = get_user_client(not_author)

        status_code = update_question_request(
            client=client,
            poll_author=author,
            model_name=model,
            data=update_question_data,
        )
        assert 403 == status_code

    def test_update_question_ANONYMOUS_permission_403(self, model, get_user_client, update_question_data):
        author = baker.make(User, email='notauthor@test.com')
        anonymous_client = APIClient()
        status_code = update_question_request(
            client=anonymous_client,
            poll_author=author,
            model_name=model,
            data=update_question_data,
        )
        assert 401 == status_code

    def test_put_question_REDACTOR_permission_200(self, model, get_user_client, update_question_data):
        redactor = baker.make(User, email='redactor@test.com')
        author = baker.make(User, email='author@test.com')

        poll = baker.make(Poll, user=author)
        client = get_user_client(redactor)

        UserAccess.objects.create(
            user=redactor,
            poll=poll,
            role=REDACTOR,
        )
        status_code = update_question_request(
            client=client,
            poll_author=author,
            poll=poll,
            model_name=model,
            data=update_question_data,
        )
        assert 200 == status_code

    def test_put_question_VIEW_RESPONSES_permission_403(self, model, get_user_client, update_question_data):
        view_responses = baker.make(User, email='redactor@test.com')
        author = baker.make(User, email='author@test.com')

        poll = baker.make(Poll, user=author)
        client = get_user_client(view_responses)

        UserAccess.objects.create(
            user=view_responses,
            poll=poll,
            role=VIEW_RESPONSES,
        )
        status_code = update_question_request(
            client=client,
            poll_author=author,
            poll=poll,
            model_name=model,
            data=update_question_data,
        )
        assert 403 == status_code

    def test_delete_question_REDACTOR_permission_200(self, model, get_user_client):
        redactor = baker.make(User, email='redactor@test.com')
        author = baker.make(User, email='author@test.com')

        poll = baker.make(Poll, user=author)
        client = get_user_client(redactor)

        UserAccess.objects.create(
            user=redactor,
            poll=poll,
            role=REDACTOR,
        )
        status_code = delete_question_request(
            client=client,
            poll_author=author,
            poll=poll,
            model_name=model,
        )
        assert 200 == status_code

    def test_delete_question_VIEW_RESPONSES_permission_403(self, model, get_user_client):
        view_responses = baker.make(User, email='redactor@test.com')
        author = baker.make(User, email='author@test.com')

        poll = baker.make(Poll, user=author)
        client = get_user_client(view_responses)

        UserAccess.objects.create(
            user=view_responses,
            poll=poll,
            role=VIEW_RESPONSES,
        )
        status_code = delete_question_request(
            client=client,
            poll_author=author,
            poll=poll,
            model_name=model,
        )
        assert 403 == status_code

    def test_get_questions_AUTHOR(self, model, get_user_client):
        author = baker.make(User, email='author@test.com')
        client = get_user_client(author)

        _author = baker.make(User)
        poll = baker.make(Poll, user=_author)
        UserAccess.objects.create(
            user=author,
            poll=poll,
            role=AUTHOR,
        )
        status_code = get_question_request(
            client=client,
            poll_author=_author,
            poll=poll,
            model_name=model,
        )
        assert 200 == status_code

    def test_get_questions_REDACTOR(self, model, get_user_client):
        redactor = baker.make(User, email='author@test.com')
        client = get_user_client(redactor)

        author = baker.make(User)
        poll = baker.make(Poll, user=baker.make(User))
        UserAccess.objects.create(
            user=redactor,
            poll=poll,
            role=REDACTOR,
        )
        status_code = get_question_request(
            client=client,
            poll_author=author,
            poll=poll,
            model_name=model,
        )
        assert 200 == status_code

    def test_get_questions_VIEW_RESPONSES(self, model, get_user_client):
        view_responses = baker.make(User, email='author@test.com')
        client = get_user_client(view_responses)

        another_author = baker.make(User)
        poll = baker.make(Poll, user=another_author)
        UserAccess.objects.create(
            user=view_responses,
            poll=poll,
            role=VIEW_RESPONSES,
        )
        status_code = get_question_request(
            client=client,
            poll_author=another_author,
            poll=poll,
            model_name=model,
        )
        assert 200 == status_code

    def test_get_questions_ANONYMOUS(self, model, get_user_client):
        another_author = baker.make(User)
        poll = baker.make(Poll, user=another_author)

        anonymous_client = APIClient()
        status_code = get_question_request(
            client=anonymous_client,
            poll_author=another_author,
            poll=poll,
            model_name=model,
        )
        assert 200 == status_code
