import pytest
import os
import uuid
from ticktick.api import TickTickClient
from ticktick.oauth2 import OAuth2
from unittest.mock import patch


@pytest.fixture(scope='session')
def client():
    user = os.getenv('TICKTICK_USER')
    passw = os.getenv('TICKTICK_PASS')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    redirect_uri = os.getenv('URI')

    auth_client = OAuth2(client_id=client_id,
                         client_secret=client_secret,
                         redirect_uri=redirect_uri,
                         env_key="ACCESS_TOKEN_DICT")

    return_client = TickTickClient(user, passw, oauth=auth_client)
    yield return_client


@pytest.fixture(scope='session')
def fake_client():
    user = str(uuid.uuid4())
    passw = str(uuid.uuid4())
    client_id = str(uuid.uuid4())
    client_secret = str(uuid.uuid4())
    redirect = str(uuid.uuid4())
    with patch('ticktick.oauth2.OAuth2.get_access_token'):
        oauth = OAuth2(client_id=client_id, client_secret=client_secret, redirect_uri=redirect)

    oauth.access_token_info = {'access_token': 'fake'}

    with patch('ticktick.api.TickTickClient._prepare_session'):
        client = TickTickClient(user, passw, oauth)

    yield client
