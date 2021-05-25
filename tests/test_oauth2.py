"""
Tests the oauth2 module
"""
import httpx
import pytest
import os
import uuid


from ticktick.oauth2 import OAuth2
from ticktick.cache import CacheHandler
from unittest import mock


@pytest.yield_fixture(scope="module")
def oauth_client_fake():
    client_id = "aPzhUPvXPaDgAXwznM"
    client_secret = "hyE^TaeRiM^EirOicoC~oNNusWu5fLlA"
    redirect_uri = "http://127.0.0.1:8080"
    auth_client = OAuth2(client_id=client_id,
                         client_secret=client_secret,
                         redirect_uri=redirect_uri)
    yield auth_client


@pytest.yield_fixture(scope="module")
def oauth_client_real():
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("URI")
    auth_client = OAuth2(client_id=client_id,
                         client_secret=client_secret,
                         redirect_uri=redirect_uri)
    yield auth_client


def test_members_set_properly():
    """
    Tests that the class members are set properly
    """
    client_id = str(uuid.uuid4())
    client_secret = str(uuid.uuid4())
    redirect_uri = str(uuid.uuid4())
    auth = OAuth2(client_id=client_id,
                  client_secret=client_secret,
                  redirect_uri=redirect_uri)

    # assert the members match
    assert isinstance(auth._session, httpx.Client)
    assert auth._client_id == client_id
    assert auth._client_secret == client_secret
    assert auth._redirect_uri == redirect_uri
    assert auth._scope == "tasks:write tasks:read"
    assert auth._state is None
    assert auth._code is None
    assert isinstance(auth._cache, CacheHandler)
    assert auth._access_token_info is None


def test_session_passing():
    """
    Tests initializing with a previous session passes
    """
    session = httpx.Client()
    client_id = str(uuid.uuid4())
    client_secret = str(uuid.uuid4())
    redirect_uri = str(uuid.uuid4())
    auth = OAuth2(client_id=client_id,
                  client_secret=client_secret,
                  redirect_uri=redirect_uri,
                  session=session)
    assert auth._session == session


def test_session_passing_fail():
    """
    Tests passing an invalid session creates a valid session
    """
    session = "Not valid"
    client_id = str(uuid.uuid4())
    client_secret = str(uuid.uuid4())
    redirect_uri = str(uuid.uuid4())
    auth = OAuth2(client_id=client_id,
                  client_secret=client_secret,
                  redirect_uri=redirect_uri,
                  session=session)
    assert auth._session != session
    assert isinstance(auth._session, httpx.Client)


def test_get_auth_url(oauth_client_fake):
    """
    Tests creating the auth url
    """
    expected = "https://ticktick.com/oauth/authorize?client_id=aPzhUPvXPaDgAXwznM&scope=tasks%3Awrite+tasks%3Aread&res" \
               "ponse_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A8080&state=None"
    assert expected == oauth_client_fake.get_auth_url()


def test_get_auth_response_parameters(oauth_client_fake):
    """
    Tests parsing the state and code parameters from a url
    """
    url = "http://127.0.0.1:8080/?code=qlh8WV&state=None"
    code = "qlh8WV"
    state = "None"
    returned_code, returned_state = oauth_client_fake.get_auth_response_parameters(url)
    assert returned_code == code
    assert returned_state == state


def test_get_redirected_url(oauth_client_fake):
    """
    Tests prompting the user for the redirected url
    """
    url = "http://127.0.0.1:8080/?code=quhwV8&state=None"
    code = "quhwV8"
    state = "None"

    # mock _get_user_input to return the value of the url for testing
    with mock.patch('ticktick.oauth2.OAuth2._get_user_input', return_value=url):
        oauth_client_fake._get_redirected_url()

    assert oauth_client_fake._code == code
    assert oauth_client_fake._state == state


def test_get_user_input(oauth_client_fake):
    with pytest.raises(OSError):
        oauth_client_fake._get_user_input()

