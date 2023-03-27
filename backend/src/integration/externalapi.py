# Интерация с внешним API
import logging
import requests
from http import HTTPStatus

from rest_framework.response import Response

logging.basicConfig(filename='apilog.log', level=logging.INFO)


def externalAPI(array, api_link, param):
    questions = array['questions']
    user_answers = array['user_answers']
    data = {key: ' ' for key in param.split(' ')}
    api_list = list(data.keys())

    bool_answer = {'да': True, 'нет': False, 'yes': True, 'no': False}

    answer = dict()

    for question in questions:
        for item in question['items']:
            answer[item['item_question_id']] = item['text']

    for idx, item in enumerate(user_answers):
        if item['items_question'][0] in answer.keys() \
                and str(answer[item['items_question'][0]]).lower() in bool_answer.keys():
            data[api_list[idx]] = bool_answer[str(answer[item['items_question'][0]]).lower()]
        elif item['items_question']:
            data[api_list[idx]] = answer[item['items_question'][0]]

    try:
        res = requests.post(api_link, data=data)
        logging.info(f'data post to {api_link}: {data}, status: {res.status_code}')
    except requests.exceptions.RequestException as er:
        logging.error(f'{er}')
        return Response({'error': f'{er}'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return res.status_code
