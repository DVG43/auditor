import json
from django.db.models import TextField


class SimpleJsonField(TextField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        try:
            return json.loads(value)
        except:
            string_list = value[1:-1].split(',')
            for i, v in enumerate(string_list):
                if v == 'NULL':
                    string_list[i] = None
            return string_list

    def get_prep_value(self, value):
        return json.dumps(value)
