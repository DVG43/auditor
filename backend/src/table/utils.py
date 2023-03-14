from common.models import UserChoice
from common.serializers import UserColumnSerializer
from table.models import DefaultTableUsercell, DefaultTableFrame


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
        table.col_order.append(usercolumn.id)
        table.save()
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


def add_userfields(user, host_obj, new_obj):
    """
    Добавление юзер.колонок к строкам документа
    """
    columns = host_obj.frame_columns.all()
    for usercolumn in columns:
        usercell = DefaultTableUsercell.objects.create(
            host_usercolumn=usercolumn, owner=user)
        new_obj.userfields.add(usercell)


def organize_data_row_sort_arrays(instance):
    instance_has_userfields = False
    instance_data_row_attribute = None
    for attr in dir(instance):
        if attr.endswith('frames') or attr == 'locations':
            instance_data_row_attribute = getattr(instance, attr)
        if attr == 'userfields':
            instance_has_userfields = True
    instance_data_row = list(instance_data_row_attribute.values('id'))
    instance_data_row_ids = [data_row['id'] for data_row in instance_data_row]
    if set(instance_data_row_ids) != set(instance.data_row_order):
        diff = list(set(instance_data_row_ids)
                    .difference(set(instance.data_row_order)))
        instance.data_row_order += diff

    if instance.data_row_order:
        for idx in reversed(instance.data_row_order):
            if idx not in instance_data_row_ids:
                instance.data_row_order.remove(idx)
    else:
        for ident in instance_data_row_ids:
            instance.data_row_order.append(ident)

    if instance_has_userfields:
        if DefaultTableFrame.objects.first():
            frame = instance_data_row_attribute.first()
            column_ids = list(frame.userfields.values('field_id'))
            for idx in reversed(instance.col_order):
                if {'field_id': idx} not in column_ids:
                    instance.col_order.remove(idx)
        else:
            instance.col_order = []

    # отключаем изменение last_modified_date
    for field in instance._meta.local_fields:
        if field.name == "last_modified_date":
            field.auto_now = False

    instance.save()

    # включаем изменение last_modified_date
    for field in instance._meta.local_fields:
        if field.name == "last_modified_date":
            field.auto_now = True
