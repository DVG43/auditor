from poll.query import get_or_none
from poll.models.answer import UserAnswerQuestion
from poll.models.questions import YesNoQuestion, FreeAnswer
from poll.utils import QUESTION_SERIALIZERS_V1


def get_serialized_questions(questions):
    data = []
    for question in questions:
        serializer = QUESTION_SERIALIZERS_V1[question.question_type]
        serialized_questions = serializer(question)
        data.append(serialized_questions.data)
    return data


def swap(a, b, swap_list):
    swap_list[b], swap_list[a] = swap_list[a], swap_list[b]
    return swap_list


def update_order_yes_no_answer_items(item_question_id: int, old_order_id: int, order_id: int):
    """
    Update answer ordering in UserAnswerQuestion
    for saving matching answer to question after change order_id
    """
    yes_no_question = get_or_none(YesNoQuestion, items__item_question_id=item_question_id)
    if not yes_no_question:
        return None

    len_items = yes_no_question.items.count()
    answers = UserAnswerQuestion.objects.filter(question_id=yes_no_question.question_id)
    for answer in answers:
        if not answer.yes_no_answers_id:
            continue

        items = answer.yes_no_answers_id
        if len(answer.yes_no_answers_id) < len_items:
            items.extend([None for _ in range(len_items - len(answer.yes_no_answers_id))])

        if old_order_id != order_id and items:
            answer.yes_no_answers_id = swap(swap_list=items, a=old_order_id - 1, b=order_id - 1)

    UserAnswerQuestion.objects.bulk_update(answers, ['yes_no_answers_id'])


def update_order_free_answer_items(item_question_id: int, old_order_id: int, order_id: int):
    """
    Update answer ordering in UserAnswerQuestion
    for saving matching answer to question after change order_id
    """
    free_answer_question = get_or_none(FreeAnswer, items__item_question_id=item_question_id)
    if not free_answer_question:
        return None

    len_items = free_answer_question.items.count()
    answers = UserAnswerQuestion.objects.filter(question_id=free_answer_question.question_id)
    for answer in answers:
        if not answer.text_answer:
            continue

        items = answer.text_answer
        if len(answer.text_answer) < len_items:
            items.extend([[None] for _ in range(len_items - len(answer.text_answer))])

        if old_order_id != order_id and items:
            answer.text_answer = swap(swap_list=items, a=old_order_id - 1, b=order_id - 1)

    UserAnswerQuestion.objects.bulk_update(answers, ['text_answer'])