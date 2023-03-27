import logging
import telegram
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.db import models
from integration.service import get_item_questions, get_user_answers, get_captions_questions, \
    get_free_answer, get_yes_no_answer
from poll.models.poll import Poll
from poll.models.surveypassing import SurveyPassing


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class TelegramVariable(models.Model):
    poll = models.ForeignKey(Poll, related_name='telegram_variables', on_delete=models.CASCADE)
    question_id = models.IntegerField()
    caption = models.CharField(max_length=255, blank=True)


class TelegramIntegration(models.Model):
    poll = models.OneToOneField(Poll, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, blank=True, null=True)
    message = models.CharField(max_length=255, default='', blank=True, null=True)
    is_active = models.BooleanField(default=False, blank=True, null=True)

    def update_variable_in_message(self):
        captions = get_captions_questions(poll_id=self.poll.pk)

        for user_answer in captions:
            variable = TelegramVariable.objects.filter(poll=self.poll,
                                                       question_id=int(user_answer['question_id'])).first()
            if not variable:
                variable = TelegramVariable(poll=self.poll, question_id=user_answer['question_id'], caption='')

            user_answer['old_caption'] = variable.caption
            variable.caption = user_answer['caption']
            variable.save()

        message = self.message
        for user_answer_item in captions:
            text_to_replace = '{{ ' + user_answer_item['old_caption'] + ' }}'
            replace_text = '{{ ' + user_answer_item['caption'] + ' }}'
            message = message.replace(text_to_replace, replace_text)
        self.message = message
        self.save()
        return message

    def send_message(self, request, survey_passing_id=None, message=None):
        bot = telegram.Bot(token=self.token)
        if not message:
            message = self.message

        if survey_passing_id:

            survey_passing = SurveyPassing.objects.filter(id=survey_passing_id).first()
            items = get_item_questions(self.poll)
            user_answer_items = get_user_answers(survey_passing_id=survey_passing_id, items=items)
            user_answer_items += get_free_answer(survey_passing_id=survey_passing_id, poll_id=self.poll)
            user_answer_items += get_yes_no_answer(survey_passing_id=survey_passing_id, poll_id=self.poll)

            for user_answer_item in user_answer_items:
                text_to_replace = '{{ ' + user_answer_item['caption'] + ' }}'
                message = message.replace(text_to_replace, user_answer_item['text'])

            message = message.replace('{{ Ссылка }}', self.poll.obj_url(request))
            message = message.replace('{{ Ссылка на отчет }}', survey_passing.obj_report_url(request))
            message = message.replace('{{ Дата }}',
                                      str(timezone.localtime(survey_passing.created_at).strftime("%d.%m.%Y %H:%M:%S")))
            message = message.replace('{{ Название формы }}', str(self.poll.name))

            try:
                message = message.replace('{{ Автор }}', survey_passing.user.secretguestprofile.full_name)
            except AttributeError:
                message = message.replace('{{ Автор }}', get_client_ip(request))

        message = mark_safe(message)
        for chat in self.chats.all():
            try:
                chat.count_of_sent += 1
                _message = message.replace("{{ № ответа }}", str(chat.count_of_sent))
                bot.sendMessage(chat.chat_id, text=_message)
                chat.save()
            except Exception as err:
                logger = logging.getLogger(__name__)
                print('error', err)
                logger.error(err)
                continue


class TelegramChats(models.Model):
    bot = models.ForeignKey(TelegramIntegration, on_delete=models.CASCADE, related_name='chats')
    chat_id = models.CharField(max_length=255, blank=True, null=True)
    count_of_sent = models.IntegerField(default=0, blank=True, null=True)
