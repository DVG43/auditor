import pytest
from poll.models.poll import Poll, PollTags


@pytest.fixture
def create_poll():
    def make_poll(user):
        return Poll.objects.create(
            user=user,
            title='test_title',
            image='test_image',
            test_mode_global=True,
        )
    return make_poll

# default poll
@pytest.fixture
def poll(admin):
    return Poll.objects.create(
            user=admin,
            title='test_title',
            image='test_image',
            test_mode_global=True,
        )


@pytest.fixture
def create_poll_tags():
    def make_poll_tags(tag_name):
        return PollTags.objects.create(
            name=tag_name
        )
    return make_poll_tags
