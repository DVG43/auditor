import pytest
from model_bakery import baker

from poll.models.poll import Poll
from user.models import User


@pytest.fixture()
def test_create_theme():
    theme = {
        'background_color': 'CFAHZfS',
        'background_image': '',
        'background_opacity': 1,
        'button_opacity': 1,
        'control_color': 'RJSMNcP',
        'font': 'LjHkvtNxVgPBogmDpIoFEcBKnELmipiC',
        'is_standard': False,
        'logo': '',
        'name': 'ykFIIrWqjMVmWxBVYhPUPRxUTAVITJwVn',
        'substrate_color': 'EUffsJr',
        'substrate_enabled': True,
        'text_color': 'PeWmyhe',
    }
    return theme
