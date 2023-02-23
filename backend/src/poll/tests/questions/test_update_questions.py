import json
import pytest
from django.forms.models import model_to_dict

from poll.models.questions import DivisionQuestion, YesNoQuestion, ManyFromListQuestion, TextQuestion, RatingQuestion, \
    MediaQuestion, HeadingQuestion, FinalQuestion, FreeAnswer


def update_question_test(client, question, question_data, model):
    question_type = question.question_type
    response = client.put(
        f'/v1/polls/questions/{question.pk}/{question_type}/',
        json.dumps(question_data),
        content_type='application/json'
    )
    question_data.pop('items', None)
    question_data.pop('attached_type', None)
    question_data.pop('yes_no_answers', None)

    obtained_data = model_to_dict(
        model.objects.get(pk=question.pk),
        fields=question_data.keys()
    )
    return obtained_data, response.status_code


def update_question_test_with_relations(client, question, question_data, model, item_keys, attached_type_keys=None):
    question_type = question.question_type
    question_data = question_data.copy()
    response = client.put(
        f'/v1/polls/questions/{question.pk}/{question_type}/',
        json.dumps(question_data),
        content_type='application/json'
    )

    question_object = model.objects.get(pk=question.pk)
    obtained_data = model_to_dict(
        question_object,
        fields=question_data.keys()
    )

    obtained_data['items'] = []
    for item in question_object.items.all():
        obtained_data['items'].append(
            model_to_dict(
                item,
                fields=item_keys
            )
        )
    if attached_type_keys is not None:
        obtained_data['attached_type'] = []
        for item in question_object.attached_type.all():
            obtained_data['attached_type'].append(
                model_to_dict(
                    item,
                    fields=attached_type_keys
                )
            )
    return obtained_data, response.status_code


@pytest.mark.django_db
class TestUpdateQuestion:
    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data')
    def test_put_many_from_list_question(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        question = create_question(
            poll=poll,
            question_data=create_question_data.many_from_list_question,
            question_model=ManyFromListQuestion
        )
        obtained_data, status_code = update_question_test(
            client=client,
            question=question,
            question_data=update_question_data.many_from_list_question,
            model=ManyFromListQuestion
        )
        valid_data = update_question_data.many_from_list_question
        assert valid_data == obtained_data

    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data')
    def test_put_division_question(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        question = create_question(
            poll=poll,
            question_data=create_question_data.division_question,
            question_model=DivisionQuestion
        )

        obtained_data, status_code = update_question_test(
            client=client,
            question=question,
            question_data=update_question_data.division_question,
            model=DivisionQuestion
        )
        valid_data = update_question_data.division_question
        assert valid_data == obtained_data

    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data')
    def test_put_update_yes_no_question(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        question = create_question(
            poll=poll,
            question_data=create_question_data.yes_no_question,
            question_model=YesNoQuestion
        )

        obtained_data, status_code = update_question_test(
            client=client,
            question=question,
            question_data=update_question_data.yes_no_question,
            model=YesNoQuestion
        )
        valid_data = update_question_data.yes_no_question
        assert valid_data == obtained_data

    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data')
    def test_put_text_question(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        question = create_question(
            poll=poll,
            question_data=create_question_data.text_question,
            question_model=TextQuestion
        )
        obtained_data, status_code = update_question_test(
            client=client,
            question=question,
            question_data=update_question_data.text_question,
            model=TextQuestion
        )
        valid_data = update_question_data.text_question
        assert valid_data == obtained_data

    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data')
    def test_put_final_question(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        question = create_question(
            poll=poll,
            question_data=create_question_data.final_question,
            question_model=FinalQuestion
        )
        obtained_data, status_code = update_question_test(
            client=client,
            question=question,
            question_data=update_question_data.final_question,
            model=FinalQuestion
        )
        valid_data = update_question_data.final_question
        assert valid_data == obtained_data

    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data')
    def test_put_media_question(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        question = create_question(
            poll=poll,
            question_data=create_question_data.media_question,
            question_model=MediaQuestion
        )
        obtained_data, status_code = update_question_test(
            client=client,
            question=question,
            question_data=update_question_data.media_question,
            model=MediaQuestion
        )
        valid_data = update_question_data.media_question
        assert valid_data == obtained_data


    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data')
    def test_put_rating_question(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        question = create_question(
            poll=poll,
            question_data=create_question_data.rating_question,
            question_model=RatingQuestion
        )
        obtained_data, status_code = update_question_test(
            client=client,
            question=question,
            question_data=update_question_data.rating_question,
            model=RatingQuestion
        )
        valid_data = update_question_data.rating_question
        assert valid_data == obtained_data

    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data')
    def test_put_free_answer(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)

        question = create_question(
            poll=poll,
            question_data=create_question_data.free_answer,
            question_model=FreeAnswer
        )
        obtained_data, status_code = update_question_test(
            client=client,
            question=question,
            question_data=update_question_data.free_answer,
            model=FreeAnswer
        )
        valid_data = update_question_data.free_answer
        assert valid_data == obtained_data

class TestUpdateQuestioWithRelations:
    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data',
        'create_item_data',
        'update_item_data',
    )
    def test_put_free_answer_with_relations(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data,
            create_item_data,
            update_item_data
    ):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        model = FreeAnswer
        update_items = update_item_data.items_free_answer
        create_items = create_item_data.items_free_answer
        item_keys = update_items.keys()

        _create_question_data = create_question_data.free_answer
        _create_question_data['items'] = [create_items]
        _update_question_data = update_question_data.free_answer
        _update_question_data['items'] = [update_items]

        question = create_question(
            poll=poll,
            question_data=_create_question_data,
            question_model=model
        )
        obtained_data, status_code = update_question_test_with_relations(
            client=client,
            question=question,
            question_data=_update_question_data,
            model=model,
            item_keys=item_keys
        )
        valid_data = _update_question_data
        assert valid_data == obtained_data


    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data',
        'create_item_data',
        'update_item_data',
    )
    def test_put_manyfromlistquestion_reletions(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data,
            create_item_data,
            update_item_data
    ):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        model = ManyFromListQuestion
        update_items = update_item_data.item_question
        create_items = create_item_data.item_question

        item_keys = create_items.keys()

        _create_question_data = create_question_data.many_from_list_question
        _create_question_data['items'] = [create_items]

        _update_question_data = update_question_data.many_from_list_question
        _update_question_data['items'] = [update_items]

        question = create_question(
            poll=poll,
            question_data=_create_question_data,
            question_model=model
        )
        obtained_data, status_code = update_question_test_with_relations(
            client=client,
            question=question,
            question_data=_update_question_data,
            model=model,
            item_keys=item_keys
        )
        valid_data = _update_question_data
        assert valid_data == obtained_data

    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data',
        'create_item_data',
        'update_item_data',
    )
    def test_put_final_question_reletions(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data,
            create_item_data,
            update_item_data
    ):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        model = FinalQuestion
        update_items = update_item_data.item_question
        create_items = create_item_data.item_question

        item_keys = create_items.keys()

        _create_question_data = create_question_data.final_question
        _create_question_data['items'] = [create_items]

        _update_question_data = update_question_data.final_question
        _update_question_data['items'] = [update_items]

        question = create_question(
            poll=poll,
            question_data=_create_question_data,
            question_model=model
        )
        obtained_data, status_code = update_question_test_with_relations(
            client=client,
            question=question,
            question_data=_update_question_data,
            model=model,
            item_keys=item_keys
        )
        valid_data = _update_question_data
        assert valid_data == obtained_data

    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data',
        'create_item_data',
        'update_item_data',
    )
    def test_put_media_question_reletions(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data,
            create_item_data,
            update_item_data
    ):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        model = MediaQuestion
        update_items = update_item_data.media_item_question
        create_items = create_item_data.media_item_question

        item_keys = create_items.keys()

        _create_question_data = create_question_data.media_question
        _create_question_data['items'] = [create_items]

        _update_question_data = update_question_data.media_question
        _update_question_data['items'] = [update_items]

        question = create_question(
            poll=poll,
            question_data=_create_question_data,
            question_model=model
        )
        obtained_data, status_code = update_question_test_with_relations(
            client=client,
            question=question,
            question_data=_update_question_data,
            model=model,
            item_keys=item_keys
        )
        valid_data = _update_question_data
        assert valid_data == obtained_data

    @pytest.mark.usefixtures(
        'create_user',
        'get_user_client',
        'create_poll',
        'create_question',
        'create_question_data',
        'update_question_data',
        'create_item_data',
        'update_item_data',
    )
    @pytest.mark.django_db(transaction=True)
    def test_put_yesno_question_reletions(
            self,
            create_user,
            get_user_client,
            create_poll,
            create_question,
            create_question_data,
            update_question_data,
            create_item_data,
            update_item_data
    ):
        user = create_user(email='test@test.com')
        client = get_user_client(user)
        poll = create_poll(user)
        model = YesNoQuestion
        update_items = update_item_data.item_question
        create_items = create_item_data.item_question

        item_keys = create_items.keys()

        _create_question_data = create_question_data.yes_no_question

        _update_question_data = update_question_data.yes_no_question
        _update_question_data['items'] = [update_items]
        _update_question_data['attached_type'] = []
        _update_question_data['yes_no_answers'] = []

        question = create_question(
            poll=poll,
            question_data=_create_question_data,
            question_model=model
        )
        obtained_data, status_code = update_question_test_with_relations(
            client=client,
            question=question,
            question_data=_update_question_data,
            model=model,
            item_keys=item_keys
        )
        valid_data = _update_question_data
        obtained_data['attached_type'] = []
        obtained_data['yes_no_answers'] = []
        assert valid_data == obtained_data