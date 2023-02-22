from .models import Document, Element
import openai

def organize_data_row_sort_arrays(instance):
    # чистка и сортировка массивов сортировки
    instance_data_row_attribute = None
    for attr in dir(instance):
        if attr.endswith('element') or attr == 'locations':
            instance_data_row_attribute = getattr(instance, attr)
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

    # отключаем изменение last_modified_date
    for field in instance._meta.local_fields:
        if field.name == "last_modified_date":
            field.auto_now = False

    instance.save()

    # включаем изменение last_modified_date
    for field in instance._meta.local_fields:
        if field.name == "last_modified_date":
            field.auto_now = True

    return instance


class OpenaiMixin():
    def text_generator(self, prompt, model, max_tokens):
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=0.7,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response
