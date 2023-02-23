import json
import pytest
from model_bakery import baker

from django.forms.models import model_to_dict
from poll.models.poll import Poll
from poll.serializers.poll import PollSerializer


class Data:
    valid_response_poll = {
        'poll_id': 2,
        'author': 'test@test.com',
        'title': '',
        'test_mode_global': False,
        'questions': [],
        'count_answers': 0,
        'tags': [],
        'setting': None,
        'new_survey_passing': 0,
        'last_open': ''
    }
    requests_poll = {
        'title': 'h48723ef',
        'test_mode_global': True,
        'questions': [],
        'image': 'asd123%6f8',
        'tags': [],
        'setting': {}
    }

    setting = {
        'isFormActive': False,
        'mixQuestions': True,
        'allowRefillingForm': False,
        'groupsForRefilling': [],
        'groupsForOnlyOneFilling': [],
        'usePassword': True,
        'formPassword': '23',
        'useAnswersCountRestriction': True,
        'maxAnswers': '0',
        'useAnswersTimeRestriction': 'text',
        'maxTimeRange': ['1', '23'],
        'isRedirectActive': True,
        'redirectMethod': '123123',
        'redirectPath': '123123',
        'askLocation': True,
        'activeCaptcha': True,
        'useSignature': True,
        }

    default_setting_values = {
        'isFormActive': True,
        'mixQuestions': False,
        'allowRefillingForm': True,
        'groupsForRefilling': [],
        'groupsForOnlyOneFilling': [],
        'usePassword': False,
        'formPassword': None,
        'useAnswersCountRestriction': False,
        'maxAnswers': '0',
        'useAnswersTimeRestriction': '',
        'maxTimeRange': ['', ''],
        'isRedirectActive': False,
        'redirectMethod': '',
        'redirectPath': '',
        'askLocation': False,
        'activeCaptcha': False,
        'useSignature': False,
    }
    tags = [
        {'name': 'Tag1'},
        {'name': 'Tag2'},
        {'name': 'Tag3'}
    ]
    questions = [
        {
            'order_id': 1,
            'caption': 'TestDevision1_caption',
            'description': 'TestDevision1_description',
            'comment': 'TestDevision1_comment',
            'question_type': 'DivisionQuestion'
        },
        {
            'order_id': 2,
            'caption': 'TestDevision2_caption',
            'description': 'TestDevision2_description',
            'comment': 'TestDevision2_comment',
            'question_type': 'DivisionQuestion'
        }
    ]


@pytest.mark.django_db
class TestCreatePoll:

    @pytest.mark.usefixtures('create_user', 'get_user_client')
    def test_create_simple_poll_200(self, create_user, get_user_client):
        user = create_user(email='test@test.com')
        client = get_user_client(user)

        requests_data = Data.requests_poll
        response = client.post('/v1/polls/', json.dumps(requests_data), content_type='application/json')

        poll_id = response.json()['poll_id']
        poll = Poll.objects.get(pk=poll_id)

        valid_data = (
            user,
            requests_data['title'],
            requests_data['image'],
            requests_data['test_mode_global']
        )
        obtained_data = (
            poll.owner,
            poll.title,
            poll.image,
            poll.test_mode_global
        )
        assert valid_data == obtained_data
        assert {'result': 'The poll has been created', 'poll_id': f'{poll_id}'} == response.json()

    @pytest.mark.usefixtures('create_user', 'get_user_client')
    def test_create_poll_with_tags_200(self, create_user, get_user_client):
        user = create_user(email='test@test.com')
        client = get_user_client(user)

        requests_data = Data.requests_poll.copy()
        requests_data['tags'] = Data.tags
        response = client.post('/v1/polls/', json.dumps(requests_data), content_type='application/json')

        poll_id = response.json()['poll_id']
        poll = Poll.objects.get(pk=poll_id)

        obtained_data = list(poll.tags_list.values('name'))
        valid_data = Data.tags
        assert obtained_data == valid_data

    @pytest.mark.usefixtures('create_user', 'get_user_client')
    # testing with all fields
    def test_create_poll_with_full_setting_200(self, create_user, get_user_client):
        user = create_user(email='test@test.com')
        client = get_user_client(user)

        requests_data = Data.requests_poll.copy()
        requests_data['setting'] = Data.setting
        response = client.post('/v1/polls/',
                               json.dumps(requests_data),
                               content_type='application/json')

        poll_id = response.json()['poll_id']
        poll = Poll.objects.get(pk=poll_id)

        obtained_data = model_to_dict(poll.setting, fields=Data.setting.keys())
        valid_data = Data.setting

        assert obtained_data == valid_data

    @pytest.mark.usefixtures('create_user', 'get_user_client')
    # testing with minimum fields
    def test_create_poll_minimum_setting_200(self, create_user, get_user_client):
        user = create_user(email='test@test.com')
        client = get_user_client(user)

        requests_data = Data.requests_poll.copy()
        requests_data['setting'] = {}
        response = client.post('/v1/polls/',
                               json.dumps(requests_data),
                               content_type='application/json')
        poll_id = response.json()['poll_id']
        poll = Poll.objects.get(pk=poll_id)

        obtained_data = model_to_dict(poll.setting, fields=Data.setting.keys())
        valid_data = Data.default_setting_values

        assert obtained_data == valid_data

    @pytest.mark.usefixtures('create_user', 'get_user_client')
    def test_create_poll_200(self, create_user, get_user_client):
        user = create_user(email='test@test.com')
        client = get_user_client(user)

        requests_data = Data.requests_poll
        requests_data['setting'] = Data.setting
        requests_data['tags'] = Data.tags

        response = client.post('/v1/polls/', json.dumps(requests_data), content_type='application/json')

        poll_id = response.json()['poll_id']
        poll = Poll.objects.get(pk=poll_id)

        valid_data = (
            user,
            requests_data['title'],
            requests_data['image'],
            requests_data['test_mode_global'],
            list(poll.tags_list.values('name')),
            model_to_dict(poll.setting, fields=Data.setting.keys())
        )
        obtained_data = (
            poll.owner,
            poll.title,
            poll.image,
            poll.test_mode_global,
            Data.tags,
            Data.setting
        )
        assert valid_data == obtained_data
        assert {'result': 'The poll has been created', 'poll_id': f'{poll_id}'} == response.json()


@pytest.mark.django_db
class TestUpdatePoll:

    def test_update_put_200(self, create_user, get_user_client, create_poll):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        poll_data = model_to_dict(poll, fields=Data.requests_poll.keys())

        requests_data = {'title': 'test_title_24123124'}
        response = client.put(f'/v1/polls/poll/{poll.pk}/',
                              json.dumps(requests_data),
                              content_type='application/json')

        poll = Poll.objects.get(pk=poll.pk)
        valid_data = (
            requests_data['title'],
            poll_data['test_mode_global'],
            poll_data['image']
        )
        obtained_data = (
            poll.title,
            poll.test_mode_global,
            poll.image
        )
        assert obtained_data == valid_data

    def test_update_put_change_all_fields_200(self, create_user, get_user_client, create_poll):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        poll_data = model_to_dict(poll, fields=Data.requests_poll.keys())

        requests_data = Data.requests_poll.copy()
        requests_data['title'] = 'new_title_test22323'
        requests_data['test_mode_global'] = False
        requests_data['image'] = 'test_image_url232332'
        response = client.put(f'/v1/polls/poll/{poll.pk}/',
                              json.dumps(requests_data),
                              content_type='application/json')
        poll = Poll.objects.get(pk=poll.pk)

        valid_data = (
            requests_data['title'],
            requests_data['test_mode_global'],
            requests_data['image']
        )
        obtained_data = (
            poll.title,
            poll.test_mode_global,
            poll.image
        )
        assert obtained_data == valid_data

    def test_update_put_change_tags_200(self, create_user, get_user_client, create_poll):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        requests_data = Data.requests_poll.copy()
        requests_data['tags'] = [
            {'name': 'NewTag1'},
            {'name': 'NewTag2'},
        ]

        client.put(f'/v1/polls/poll/{poll.pk}/',
                   json.dumps(requests_data),
                   content_type='application/json')
        poll = Poll.objects.get(pk=poll.pk)

        obtained_data = list(poll.tags_list.values('name'))
        valid_data = requests_data['tags']
        assert obtained_data == valid_data

    def test_update_put_change_settings_200(self, create_user, get_user_client, create_poll):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        requests_data = Data.requests_poll.copy()
        requests_data['setting'] = Data.setting

        client.put(f'/v1/polls/poll/{poll.pk}/',
                        json.dumps(requests_data),
                        content_type='application/json')
        poll = Poll.objects.get(pk=poll.pk)

        obtained_data = model_to_dict(poll.setting, fields=Data.setting.keys())
        valid_data = Data.setting

        assert obtained_data == valid_data

    def test_delete_200(self, create_user, get_user_client, create_poll):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        client.delete(f'/v1/polls/poll/{poll.pk}/',
                              content_type='application/json')

        assert Poll.objects.filter(pk=poll.pk).exists() is False

@pytest.mark.django_db
class TestGetPoll:
    @pytest.mark.usefixtures('user_client', 'create_poll', 'create_user')
    def test_get_poll_setting_200(self, user_client, create_poll, create_user):
        user = create_user(email='test@test.com')
        poll = create_poll(user=user)
        response = user_client.get(f'/v1/polls/poll/{poll.pk}/')

        valid_response = Data.valid_response_poll.copy()
        valid_response['poll_id'] = poll.pk
        valid_response['title'] = poll.title
        valid_response['test_mode_global'] = poll.test_mode_global
        valid_response['count_answers'] = 0
        valid_response['new_survey_passing'] = 0
        valid_response['last_open'] = ''
        valid_response['telegram_integration'] = False
        valid_response['user_role'] = ''
        valid_response['googlesheet_integration'] = False
        response_data = response.json()['result'][0]
        response_data['last_open'] = ''
        assert response_data == valid_response

@pytest.mark.django_db
class TestPollTags:

    @pytest.mark.usefixtures('get_user_client', 'create_poll', 'create_user')
    def test_create_polls_tags_200(self, create_user, create_poll, get_user_client):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll_1 = create_poll(user=user)
        poll_2 = create_poll(user=user)

        data = {
            'polls': [
                poll_2.pk,
                poll_1.pk,
            ],
            'tags': Data.tags
        }

        response = client.post(f'/v1/polls/poll/tags/', json.dumps(data), content_type='application/json')

        obtained_data_1 = list(poll_1.tags_list.values('name'))
        obtained_data_2 = list(poll_2.tags_list.values('name'))

        valid_response = Data.tags

        assert obtained_data_1 == valid_response
        assert obtained_data_2 == valid_response

    @pytest.mark.usefixtures('get_user_client', 'create_poll', 'create_user')
    def test_get_polls_tags(self, create_user, create_poll, get_user_client):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user=user)
        poll.tags_list.get_or_create(name='test_tag_name')

        response = client.get(f'/v1/polls/poll/{poll.pk}/tags/', content_type='application/json')

        obtained_data_response = response.json()['result'][0]
        obtained_data_response['tag_id'] = 0
        validate_data = {'name': 'test_tag_name', 'tag_id': 0}

        assert obtained_data_response == validate_data
