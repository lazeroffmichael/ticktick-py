import pytest
import os
from libtick.tick_tick import TickTickClient


@pytest.fixture(scope='session')
def client():
    user = os.getenv('TICKTICK_USER')
    passw = os.getenv('TICKTICK_PASS')
    return_client = TickTickClient(user, passw)
    yield return_client
