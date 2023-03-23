import json
import time
from operator import attrgetter
from typing import Tuple

import google.auth.exceptions
import googleapiclient.discovery

from integration.models.googlesheet import GoogleSheetCredentials, GoogleSheetIntegration
from poll.models.questions import ItemQuestion
from google.oauth2.credentials import Credentials

from accounts.models import User


class GoogleSheetIntegrationService:
    @staticmethod
    def connect_to_google_sheet_api(credentials):
        """
        Connect to GoogleSheet API
        """
        try:
            service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
        except google.auth.exceptions.MutualTLSChannelError:
            time.sleep(2)
            service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
        return service

    def google_sheet_service(self, user):
        google_credentials = GoogleSheetCredentials.objects.get(user=user).google_sheet_credentials
        credentials = Credentials.from_authorized_user_info(json.loads(google_credentials))
        return self.connect_to_google_sheet_api(credentials=credentials)

    @staticmethod
    def create_empty_spreadsheets(service, sheet_name):
        """
        Create empty spreadsheet
        """
        spreadsheet = service.spreadsheets().create(body={
            'properties': {
                'title': sheet_name, 'locale': 'ru_RU'
            },
            'sheets': [{
                'properties': {
                    'sheetType': 'GRID',
                    'sheetId': 0,
                    'title': sheet_name,
                    'gridProperties': {
                        'rowCount': 10000,
                        'columnCount': 10
                    }}}]
        }).execute()
        return spreadsheet

    @staticmethod
    def get_access_to_spreadsheets_for_any_user(credentials, spreadsheet_id):
        """
        Connect to GoogleDrive API to get access to spreadsheets for any user
        """
        try:
            drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)
        except google.auth.exceptions.MutualTLSChannelError:
            time.sleep(2)
            drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body={'type': 'anyone', 'role': 'writer'},
            fields='id'
        ).execute()
        return drive_service

    @staticmethod
    def add_information_to_spreadsheet(sheet_name, service, row_count, spreadsheet_id, values):
        """
        Add information to sheet
        """
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": f"{sheet_name}!A{row_count}:ZZZ{row_count + len(values)}",
                     "majorDimension": "ROWS",
                     "values": values}
                ]}
        ).execute()

    @staticmethod
    def set_default_format_sheet(service, spreadsheet_id, len_spreadsheet_data):
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": 0,
                                "dimension": "ROWS",
                                "startIndex": 0,
                                "endIndex": 2
                            },
                            "properties": {
                                "pixelSize": 100
                            },
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": 0,
                                "dimension": "COLUMNS",
                                "startIndex": 0,
                                "endIndex": 2
                            },
                            "properties": {
                                "pixelSize": 100
                            },
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": 0,
                                "startRowIndex": 0,
                                "endRowIndex": 2,
                                "startColumnIndex": 0,
                                "endColumnIndex": len_spreadsheet_data
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "wrapStrategy": "WRAP",
                                    "horizontalAlignment": 'CENTER',
                                }
                            },
                            "fields": "userEnteredFormat.wrapStrategy"
                        },
                    },
                ]
            }).execute()

    @staticmethod
    def update_sheet(service, spreadsheet_id, requests=None) -> None:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    requests if requests else None,
                ]
            }).execute()


gs_service = GoogleSheetIntegrationService()


class SheetService:
    @staticmethod
    def get_base_caption() -> list:
        """
        Get base captions for firs line in sheet
        """
        return [
            'Дата',
            'Время',
            'Название формы',
            'Ссылка на результаты',
            'Проверяющий',
            'Заполнено',
        ]

    def get_caption(self, questions) -> list:
        """
        Get questions captions for set question caption in first line
        and set question items caption in second line
        """
        first_row = self.get_base_caption()
        second_row = ["" for i in range(len(first_row))]

        for question in questions:
            items = question.items.all()

            if question.question_type in ["YesNoQuestion", "FreeAnswer"]:
                for item_numerator, item in enumerate(items):
                    first_row.append(question.caption)
                    second_row.append(item.text)
                continue

            if question.question_type == "ManyFromListQuestion":
                if question.count_of_answer == 1:
                    first_row.extend([question.caption, ""])
                    second_row.extend(["", "Баллы"])
                    continue

                for item_numerator, item in enumerate(items):
                    first_row.extend([question.caption, ""])
                    second_row.extend([item.text, "Баллы"])
                continue

        return [first_row, second_row]

    @staticmethod
    def get_base_row_data(request, survey, count_question, count_answers) -> list:
        """
        Get base row data which using in each answer row
        """
        try:
            email = survey.owner.email
        except:
            email = "anonymous"
        return [
            survey.created_at.strftime("%d.%m.%Y"),  # date
            survey.created_at.strftime("%H:%M:%S"),  # time
            survey.poll.title,  # poll title
            survey.obj_report_url(request),  # report answer url
            email,  # email of user who gave answer
            str(round(count_answers / count_question * 100, 2)) + "%",  # completed percentage
        ]

    def get_questions_row_data(self, survey, questions) -> Tuple[list, int]:
        """
        Get questions row data with answers and count user answer in current survey
        """

        count_user_answers = 0
        row_data = []
        for question in questions:
            answer = survey.useranswerquestion_set.filter(question_id=question.question_id).first()
            if not answer:
                count_items = len(question.items.all())
                mul = 1
                if question.question_type == "ManyFromListQuestion" and question.count_of_answer != 1:
                    mul = 2
                row_data.extend(["" for i in range(count_items * mul)])
                continue

            if question.question_type == "YesNoQuestion":
                row_data.extend(self.answer_yes_no_question(answer=answer, question=question))

            elif question.question_type == "FreeAnswer":
                row_data.extend(self.answer_free_answer_question(answer=answer))

            elif question.question_type == "ManyFromListQuestion":
                row_data.extend(self.answer_many_from_list_question(
                    answer=answer, question=question, test_mode=survey.poll.test_mode_global,
                ))

            if answer.items_question or answer.text_answer or answer.yes_no_answers_id:
                count_user_answers += 1

        return row_data, count_user_answers

    @staticmethod
    def answer_yes_no_question(answer, question) -> list:
        """
        Get an answers to the Yes No question
        """
        answers = ["" for i in range(len(question.items.all()))]
        yes_no_answers = {item.id: int(item.checked) for item in question.yes_no_answers.all()}
        for i, yes_no_id in enumerate(answer.yes_no_answers_id):
            if yes_no_id is None:
                try:
                    answers[i] = ""
                except IndexError:
                    break
                continue
            try:
                answers[i] = yes_no_answers[yes_no_id]
            except IndexError:
                break
            except KeyError:
                break
        return answers

    @staticmethod
    def answer_many_from_list_question(answer, test_mode, question) -> list:
        """
        Get an answers to the ManyFromList question
        """
        answers = {}
        items = question.items.all()
        for item in items:
            answers[item.item_question_id] = "не выбран"
            answers[f"{item.item_question_id}_points"] = 0 if test_mode else ""

        if not answer.items_question and question.count_of_answer == 1:
            return ['', '']

        for item_id in answer.items_question:
            try:
                item_question = question.items.get(item_question_id=item_id)
            except ItemQuestion.DoesNotExist:
                if len(answer.items_question) == 1:
                    count = (len(items) * 2) if question.count_of_answer != 1 else 2
                    return ['' for i in range(count)]
                continue
            if question.count_of_answer == 1:
                return [item_question.text, item_question.points if test_mode else ""]
            answers[item_id] = "выбран"
            answers[f"{item_id}_points"] = item_question.points if test_mode else ""

        return list(answers.values())

    @staticmethod
    def answer_free_answer_question(answer) -> list:
        """
        Get an answers to the FreeAnswer question
        """
        free_answers = []
        for text_items in answer.text_answer:
            for text in text_items:
                free_answers.append(text if text else '')
        return free_answers

    @staticmethod
    def get_poll_questions(poll) -> list:
        questions = [
            *poll.yesnoquestion_set.all(),
            *poll.manyfromlistquestion_set.all(),
            *poll.freeanswer_set.all()
        ]
        questions = sorted(questions, key=attrgetter('order_id'))
        return questions

    def get_all_questions_position(self, questions: list) -> list:
        """
        Get all questions column position in sheet
        for using in insert/move/delete column operations
        """

        positions = []
        start_index = len(self.get_base_caption())

        for question in questions:
            items = question.items.all()
            len_items = len(items)
            question_type = question.__class__.__name__

            # because ManyFromListQuestion have columns with points
            multiplier = 1
            point = 0
            if question_type == "ManyFromListQuestion":
                multiplier = 2
                point = 1
                if question.count_of_answer == 1:
                    len_items = 1

            question_position = {
                "order_id": question.order_id,
                "type": question_type,
                "start_column_index": start_index,
                "end_column_index": start_index + len_items * multiplier,
                "items": [],
            }

            start_item_index = start_index
            for item in items:
                question_position["items"].append({
                    "order_id": item.order_id,
                    "start_column_index": start_item_index + item.order_id - 1,
                    "end_column_index": start_item_index + item.order_id + point
                })
                start_item_index += point

            start_index += len_items * multiplier
            positions.append(question_position)

        return positions

    def move_question_in_sheet(self, order_id_before, order_id_after, question, item=None):
        """
        Move columns in sheet when change order questions
        """
        google_sheet_integration = GoogleSheetIntegration.objects.get(id=question.poll_id)
        service = gs_service.google_sheet_service(user=google_sheet_integration.user)

        questions = self.get_poll_questions(poll=question.poll)
        questions_positions = self.get_all_questions_position(questions=questions)

        if not item:
            # find positions for move question
            position_before = next(
                item for item in questions_positions if item["order_id"] == order_id_before)
            position_after = next(
                item for item in questions_positions if item["order_id"] == order_id_after)
        else:
            # find positions for move question item
            question_position = next(
                item for item in questions_positions if item["order_id"] == question.order_id)
            position_before = next(
                item for item in question_position['items'] if item["order_id"] == order_id_before)
            position_after = next(
                item for item in question_position['items'] if item["order_id"] == order_id_after)

        requests = {
            "moveDimension": {
                "source": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": position_before["start_column_index"],
                    "endIndex": position_before["end_column_index"],
                },
                "destinationIndex": position_after["start_column_index"]
            }
        }

        gs_service.update_sheet(
            service=service,
            spreadsheet_id=google_sheet_integration.spreadsheet_id,
            requests=requests
        )

    def insert_item_question_in_sheet(self, question, item_):
        """
        Add new item question in google sheet
        """
        google_sheet_integration = GoogleSheetIntegration.objects.get(id=question.poll_id)
        service = gs_service.google_sheet_service(user=google_sheet_integration.user)

        questions = self.get_poll_questions(poll=question.poll)
        positions = self.get_all_questions_position(questions=questions)
        question_position = next(
            item for item in positions if item["order_id"] == question.order_id)

        item_position = next(
            item for item in question_position['items'] if item["order_id"] == item_.order_id)
        point = 1
        if question.question_type == "ManyFromListQuestion":
            point = 2

        requests = {
            "insertDimension": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": item_position["start_column_index"],
                    "endIndex": item_position['start_column_index'] + point,
                },
                "inheritFromBefore": False
            }
        }

        gs_service.update_sheet(
            service=service,
            spreadsheet_id=google_sheet_integration.spreadsheet_id,
            requests=requests
        )

    def delete_item_question_in_sheet(self, question, item):
        """
        Delete item question in google sheet
        """
        google_sheet_integration = GoogleSheetIntegration.objects.get(id=question.poll_id)
        service = gs_service.google_sheet_service(user=google_sheet_integration.user)

        questions = self.get_poll_questions(poll=question.poll)
        questions_positions = self.get_all_questions_position(questions=questions)

        position = next(
            item for item in questions_positions if item["order_id"] == question.order_id)

        item_order_id = item
        del_position = next(
            item for item in position['items'] if item["order_id"] == item_order_id.order_id)

        requests = {
            "deleteDimension": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": del_position["start_column_index"],
                    "endIndex": del_position['end_column_index'],
                },
            }
        }

        gs_service.update_sheet(
            service=service,
            spreadsheet_id=google_sheet_integration.spreadsheet_id,
            requests=requests
        )


sheet_service = SheetService()
