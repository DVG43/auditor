from common.models import UserChoice
from common.serializers import UserColumnSerializer


def create_default_table_frame_columns(table, context):
    column_data = [
        {'column_name': 'Одиночный выбор', 'column_type': 'select'},
        {'column_name': 'Текст', 'column_type': 'text'},
        {'column_name': 'Множественный выбор', 'column_type': 'multiselect'},
        {'column_name': 'Электонная почта', 'column_type': 'email'},
        {'column_name': 'Телефон', 'column_type': 'phone'},
        {'column_name': 'Картинка', 'column_type': 'image'},
        {'column_name': 'Время', 'column_type': 'time'},
        {'column_name': 'Числа', 'column_type': 'numbers'},
        {'column_name': 'Контакт', 'column_type': 'contact'},
        {'column_name': 'Ссылка на таблицу', 'column_type': 'tablelink'},
    ]
    serializer = UserColumnSerializer(
        data=column_data, many=True, context={'user': context})
    serializer.is_valid(raise_exception=True)
    usercolumns = serializer.create(serializer.validated_data)
    for usercolumn in usercolumns:
        table.frame_columns.add(usercolumn)
        if usercolumn.column_type == 'select':
            choices = [
                {'choice': 'Выбор', 'color': 'blue'},
                {'choice': 'Выбор 1', 'color': 'red'}
            ]
            for choice in choices:
                UserChoice.objects.create(
                    **choice, host_usercolumn=usercolumn, owner=context.user)

        elif usercolumn.column_type == 'multiselect':
            choices = [
                    {'choice': 'Выбор', 'color': 'blue'},
                    {'choice': 'Выбор 1', 'color': 'red'}
                ]
            for choice in choices:
                UserChoice.objects.create(
                    **choice, host_usercolumn=usercolumn, owner=context.user)
