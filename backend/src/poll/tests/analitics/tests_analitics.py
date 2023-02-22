import pytest
from pytest_django.asserts import assertTemplateUsed
import requests
import socket
from django.conf import settings
from django.db import models

from user.models import User
from poll.models.poll import Poll
from poll.models.surveypassing import SurveyPassing 
from poll.models.analitics import PollAnalitics

class Data():
    def __init__(self, sex, age, platform):
        self.sex = sex
        self.age = age
        self.platform = platform


@pytest.fixture()
def set_data():
    return [(Data('male', 17, 'Desktop'), 'output'),
            (Data('female', 17, 'Mobile'), 'output'),
            (Data('male', 21, 'Desktop'), 'output'),
            (Data('female', 21, 'Mobile'), 'output'),
            (Data('male', 27, 'Desktop'), 'output'),
            (Data('female', 27, 'Mobile'), 'output'),
            (Data('male', 37, 'Desktop'), 'output'),
            (Data('female', 37, 'Mobile'), 'output'),
            (Data('male', 47, 'Desktop'), 'output'),
            (Data('female', 47, 'Mobile'), 'output'),
    ]

@pytest.fixture(scope='module')
def set_uris():
    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)
    uri_auth = 'http://' + IP + ':9002' + '/v1/authentication/token/obtaining/'
    uri_reg = 'http://' + IP + ':9002' + '/v1/users/registration/'
    uri_create_pollanalitics = 'http://' + IP + ':9002' + '/v1/analitics/pollanalitics/'
    uri_create_poll = 'http://' + IP + ':9002' + '/v1/polls/'
    uri_create_survey_passing = 'http://' + IP + ':9002' + '/v1/polls/sp/'
    uri_delete_survey_passing = 'http://' + IP + ':9002' + '/v1/polls/sp/multiple-delete/'

    return {
        'uri_auth': uri_auth,
        'uri_reg': uri_reg,
        'uri_create_pollanalitics': uri_create_pollanalitics,
        'uri_create_poll': uri_create_poll,
        'uri_create_survey_passing': uri_create_survey_passing,
        'uri_delete_survey_passing': uri_delete_survey_passing
    }


@pytest.fixture()
def create_user_and_token(set_uris):    
   
    response = requests.post(set_uris['uri_reg'], data={"email":"x@x.com", 
                             "password":"1", "first_name": "Ivan",
                             "last_name": "Pupkin",
                             "phone": 84954545678,
                             "birthday": "1990-06-30",
                             "address": "Moscow, Gogol street 12-4-67"})

    response = requests.post(set_uris['uri_auth'], data={"email":"x@x.com", 
                             "password":"1"})
    token = response.json()['token']

    return ['x@x.com', token]


def test_analitics(create_user_and_token, set_uris, set_data):

    poll_id = 1
# Test CREATE 
    response = requests.post(set_uris['uri_create_pollanalitics'], 
                            headers={'Authorization': 'jwt {}'.format(create_user_and_token[1])},
                            data={'poll_id': poll_id})
    pollanalitics_url = response.json()['url']
    assert response.status_code == 201
# Test PUT    
    for el in set_data:
        response = requests.post(set_uris['uri_create_survey_passing'], 
                            headers={'Authorization': 'jwt {}'.format(create_user_and_token[1])},
                            data={"user": 'x@x.com',
                                  "poll_id": poll_id,
                                  "sex": el[0].sex,
                                  "age": el[0].age,
                                  "platform": el[0].platform,
                                  'createdAt':'2020-09-22 14:56',
                                  'user_name':'x@x',
                                  'survey_title':'TEST',
                                  'status': 'new'})
        survey_id = int(response.json()['survey_id'])
        response = requests.put(pollanalitics_url, 
                                headers={'Authorization': 'jwt {}'.format(create_user_and_token[1])},
                                data={'poll_id': poll_id, 'survey_id':survey_id})
        assert response.status_code == 200
    survey_ids_list = response.json()['survey_id']
    survey_ids_str = str(survey_ids_list).strip('[]')
    payload = {'survey_ids': survey_ids_str}
# Test resolving of fields        
    assert response.json()['avarage_age'] == 29 
    assert response.json()['men_total'] == 5
    assert response.json()['women_total'] == 5
    assert response.json()['total'] == 10
    assert response.json()['percent_men_total'] == '50%'
    assert response.json()['percent_women_total'] == '50%'
    assert response.json()['women_before_18'] == 1
    assert response.json()['men_before_18'] == 1
    assert response.json()['percent_women_before_18'] == '50%'
    assert response.json()['percent_men_before_18'] == '50%'
    assert response.json()['percent_before_18_total'] == '20%'
    assert response.json()['women_in_18_24'] == 1
    assert response.json()['men_in_18_24'] == 1
    assert response.json()['percent_women_in_18_24'] == '50%'
    assert response.json()['percent_men_in_18_24'] == '50%'
    assert response.json()['percent_in_18_24_total'] == '20%'
    assert response.json()['women_in_25_35'] == 1
    assert response.json()['men_in_25_35'] == 1
    assert response.json()['percent_women_in_25_35'] == '50%'
    assert response.json()['percent_men_in_25_35'] == '50%'
    assert response.json()['percent_in_25_35_total'] == '20%'
    assert response.json()['women_in_36_45'] == 1
    assert response.json()['men_in_36_45'] == 1
    assert response.json()['percent_women_in_36_45'] == '50%'
    assert response.json()['percent_men_in_36_45'] == '50%'
    assert response.json()['percent_in_36_45_total'] == '20%'
    assert response.json()['women_older_46'] == 1
    assert response.json()['men_older_46'] == 1
    assert response.json()['percent_women_older_46'] == '50%'
    assert response.json()['percent_men_older_46'] == '50%'
    assert response.json()['percent_older_46_total'] == '20%'
    assert response.json()['percent_from_desktop'] == '50%'
    assert response.json()['percent_from_mobile'] == '50%'
    assert response.json()['percent_from_other'] == '0%'
    
    response = requests.delete(set_uris['uri_delete_survey_passing'], 
                            headers={'Authorization': 'jwt {}'.format(create_user_and_token[1])},
                            params=payload)

# Test DELETE
    response = requests.delete(pollanalitics_url, 
                                headers={'Authorization': 'jwt {}'.format(create_user_and_token[1])})
    assert response.status_code == 204
