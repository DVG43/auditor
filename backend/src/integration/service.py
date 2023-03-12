import datetime
from django.db import models

from poll.models.poll import Poll
from poll.models.surveypassing import SurveyPassing
from poll.models.questions import YesNoQuestion
from poll.serializers.answer import UserAnswerSerializer
from poll.models.answer import UserAnswerQuestion
from poll.models.questions import ManyFromListQuestion, FreeAnswer


def get_item_questions(poll_id):
    items = []
    for i in ManyFromListQuestion.objects.filter(poll_id=poll_id).all():
        items.extend(list(
            map(lambda x: {'text': x[0], 'caption': i.caption, 'item_question_id': x[1], 'question_id': i.pk},
                i.items.all().values_list('text', 'item_question_id'))))
    return items


def get_captions_questions(poll_id):
    items = ManyFromListQuestion.objects.filter(poll_id=poll_id).values('caption', 'question_id')
    return list(items)


def get_user_answers(survey_passing_id, items):
    user_answers = []
    for user_answer in UserAnswerQuestion.objects.filter(survey_id=survey_passing_id):
        user_answers.extend(user_answer.items_question)

    user_answer_items = list(filter(lambda x: x['item_question_id'] in user_answers, items))
    return user_answer_items


# the function is called every time the user finishes taking the poll
def survey_passing_event_finish(poll, request, survey_passing_id):
    if poll.telegram_integration_is_active():
        poll.telegramintegration.send_message(
            request=request,
            survey_passing_id=survey_passing_id
        )

# This function create reporting data to trnsmit them to telegram
# Survey duration, Fullness, Test point, Percent of failed answers
def get_reporting_data(survey_passing_id):
    que = []
    points_full_sum = 0
    failed = 0
    ans = []
    not_filled = 0
    duration = 0
    points_curr_sum = 0
    failed_flag = True
    if_all_filled = 0

    survey_passing = SurveyPassing.objects.filter(id=survey_passing_id).first()
    for quest in survey_passing.questions:
        if quest[1] == 'YesNoQuestion':
            qid = YesNoQuestion.objects.get(question_id=quest[0])
            qid_items = qid.items.all()
            for el in qid_items:
                el.checked = True
                if_all_filled += 1
            que.append([quest[0], qid_items, qid.yes_no_answers.all()])
            for el in qid.yes_no_answers.all():             
                points_full_sum = points_full_sum + el.points    
        elif quest[1] == 'ManyFromListQuestion':
            qid1 = ManyFromListQuestion.objects.get(question_id=quest[0])
            que.append([quest[0], qid1.items.all(), []])
            for el in qid1.items.all():
                points_full_sum = points_full_sum + el.points
                if el.checked:
                    if_all_filled += 1

    for user_answer in UserAnswerQuestion.objects.filter(survey_id=survey_passing_id):
        if len(user_answer.items_question) == 0:
            not_filled += 1
        elif user_answer.yes_no_answers_id is not None:
            for el in user_answer.yes_no_answers_id:
                if el is None:
                    not_filled += 1
        if (user_answer.yes_no_answers_id is None) or (user_answer.yes_no_answers_id[0] is None):
            user_answer.yes_no_answers_id = []
        ans.append([user_answer.question_id, user_answer.items_question, 
                    user_answer.yes_no_answers_id, user_answer.during])
        
        duration = duration + user_answer.during

    items = []
    for i in FreeAnswer.objects.filter(poll_id=survey_passing.poll).all():
        items.extend(list(
                map(lambda x: {'text': x[0], 'caption': i.caption, 
                'item_question_id': x[1], 'question_id': i.pk},
                i.items.all().values_list('text', 'item_question_id'))))  

    user_answer_question = UserAnswerQuestion.objects.filter(survey=survey_passing_id)
    for user_answer in user_answer_question:
        answer_serialised = UserAnswerSerializer(user_answer)
        k = 0
        for item in items:
            if (item['question_id'] == answer_serialised.data['question_id']):
                if_all_filled += 1
                str_answer = answer_serialised.data['text_answer'][k][0]
                if str_answer is None:
                    not_filled += 1
                k += 1

    for que_el in que:
        for ans_el in ans:
            if ans_el[0] == que_el[0]:
                for que_items_el in que_el[1]:
                    for ans_items_el in ans_el[1]:
                        if ans_items_el == que_items_el.item_question_id:                                
                            points_curr_sum = points_curr_sum + que_items_el.points
                            failed_flag = failed_flag and que_items_el.checked
                for que_yna_el in que_el[2]:
                    for ans_yna_el in ans_el[2]:
                        if ans_yna_el == que_yna_el.id:                                
                            points_curr_sum = points_curr_sum + que_yna_el.points
                            failed_flag = failed_flag and que_yna_el.checked
                if not failed_flag:
                    failed += 1
                failed_flag = True


    if len(ans) == 0:
        not_filled = if_all_filled

    if if_all_filled != 0:
        fullness = (if_all_filled - not_filled)/if_all_filled*100
    else: 
        fullness = 0

    duration_str = 'Время заполнения ' + str(datetime.time(duration//3600, 
                                             (duration%3600)//60, (duration%3600)%60))

    if points_full_sum > 0:
        test_point_str = ('Оценка в баллах ' + '{}/{} '.format(points_curr_sum, points_full_sum) 
                          + '({}%)'.format(points_curr_sum/points_full_sum*100))
    else:
        test_point_str = ('Оценка в баллах ' + '{}/{} '.format(points_curr_sum, points_full_sum) 
                          + '({}%)'.format(0))
    if len(que) == 0:
        failed_answers_str = 'Провалено {}/{} ({}%)'.format(failed, len(que), 0)
    else:
        failed_answers_str = 'Провалено {}/{} ({}%)'.format(failed, len(que), failed/len(que)*100)

    return {
        'duaration': duration_str,
        'fullness': fullness,
        'test_point': test_point_str,
        'failed_answers': failed_answers_str
        }

def get_yes_no_answers_list(survey_passing_id):

    ans = []
    yes_no_answers_list = []

    survey_passing = SurveyPassing.objects.filter(id=survey_passing_id).first()
    
    for user_answer in UserAnswerQuestion.objects.filter(survey_id=survey_passing_id):
        ans.append([user_answer.question_id, user_answer.items_question, 
                    user_answer.yes_no_answers_id, user_answer.during])

    for el in ans:
        if el[2] is not None:
            for ele in survey_passing.questions:
                if ele[0] == el[0]:
                    qid = YesNoQuestion.objects.get(question_id=ele[0])
                    for elem in el[2]:
                        if elem is None:
                            yes_no_answers_list.append('')
                        for element in qid.yes_no_answers.all():
                            if elem == element.id:
                                yes_no_answers_list.append(element.textAnswer)


    return yes_no_answers_list


def get_free_answer(survey_passing_id, poll_id):
    items = []
    for question in FreeAnswer.objects.filter(poll_id=poll_id).all():
        answer = UserAnswerQuestion.objects.filter(
            survey_id=survey_passing_id, question_id=question.question_id).first()

        items.extend([{
            'text': text_answer[0] if text_answer[0] else "---",
            'caption': question.caption,
            'item_question_id': item.item_question_id,
            'question_id': item.pk,
        } for item, text_answer in zip(question.items.all(), answer.text_answer)])

    return items


def get_yes_no_answer(survey_passing_id, poll_id):
    items = []
    for question in YesNoQuestion.objects.filter(poll_id=poll_id).all():
        answer = UserAnswerQuestion.objects.filter(
            survey_id=survey_passing_id, question_id=question.question_id).first()

        yes_no_answers = {item.id: item.textAnswer for item in question.yes_no_answers.all()}
        items.extend([{
            'text': yes_no_answers[id_answer] if id_answer else "---",
            'caption': question.caption,
            'item_question_id': item.item_question_id,
            'question_id': item.pk,
        } for item, id_answer in zip(question.items.all(), answer.yes_no_answers_id)])
    return items
