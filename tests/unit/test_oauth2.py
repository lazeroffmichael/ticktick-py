"""
Tests the oauth2 module
"""
import pytest
import os
import uuid
import time

from ticktick.oauth2 import OAuth2, requests_retry_session
from ticktick.cache import CacheHandler
from unittest.mock import patch


@pytest.fixture(scope="module")
def oauth_client_fake():
    client_id = "aPzhUPvXPaDgAXwznM"
    client_secret = "hyE^TaeRiM^EirOicoC~oNNusWu5fLlA"
    redirect_uri = "http://127.0.0.1:8080"
    with patch('ticktick.oauth2.OAuth2.get_access_token'):
        auth_client = OAuth2(client_id=client_id,
                             client_secret=client_secret,
                             redirect_uri=redirect_uri)
    yield auth_client


class TestInitMethod:

    def test_members_set_properly(self):
        """
        Tests that the class members are set properly
        """
        client_id = str(uuid.uuid4())
        client_secret = str(uuid.uuid4())
        redirect_uri = str(uuid.uuid4())
        with patch('ticktick.oauth2.OAuth2.get_access_token'):
            auth = OAuth2(client_id=client_id,
                          client_secret=client_secret,
                          redirect_uri=redirect_uri)

        # assert the members match
        assert auth._client_id == client_id
        assert auth._client_secret == client_secret
        assert auth._redirect_uri == redirect_uri
        assert auth._scope == "tasks:write tasks:read"
        assert auth._state is None
        assert auth._code is None
        assert isinstance(auth.cache, CacheHandler)
        assert auth.access_token_info is None


class TestURLMethods:

    def test_get_auth_url(self, oauth_client_fake):
        """
        Tests creating the auth url
        """
        expected = "https://ticktick.com/oauth/authorize?client_id=aPzhUPvXPaDgAXwznM&scope=tasks%3Awrite+tasks%3Aread&res" \
                   "ponse_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A8080&state=None"
        assert expected == oauth_client_fake._get_auth_url()

    def test_get_redirected_url(self, oauth_client_fake):
        """
        Tests prompting the user for the redirected url
        """
        url = "http://127.0.0.1:8080/?code=quhwV8&state=None"
        code = "quhwV8"
        state = "None"

        # mock _get_user_input to return the value of the url for testing
        with patch('ticktick.oauth2.OAuth2._get_user_input', return_value=url):
            oauth_client_fake._get_redirected_url()

        assert oauth_client_fake._code == code
        assert oauth_client_fake._state == state

    def test_get_auth_response_parameters(self, oauth_client_fake):
        """
        Tests parsing the state and code parameters from a url
        """
        url = "http://127.0.0.1:8080/?code=qlh8WV&state=None"
        code = "qlh8WV"
        state = "None"
        returned_code, returned_state = oauth_client_fake._get_auth_response_parameters(url)
        assert returned_code == code
        assert returned_state == state


class TestRequestAccessToken:

    @patch('ticktick.oauth2.OAuth2._open_auth_url_in_browser')
    @patch('ticktick.oauth2.OAuth2._get_redirected_url')
    def test_request_access_token_success(self,
                                          mock1,
                                          mock2,
                                          oauth_client_fake):
        """
        Tests proper setting of the token info upon a successful post request
        """

        # manually set code and state
        oauth_client_fake._code = "qlh8WV"

        mock1.return_value = None
        mock2.return_value = None

        new_token_info = {'access_token': '123fd691-5541-4af7-9H4f-L038e0c9f5W4a',
                          'token_type': 'bearer',
                          'expires_in': 15044529,
                          'scope': 'tasks:read tasks:write'
                          }

        with patch('ticktick.oauth2.OAuth2._post', return_value=new_token_info):
            returned_token = oauth_client_fake._request_access_token()

        assert returned_token["access_token"] == new_token_info["access_token"]

        # make sure token expire time was set
        assert returned_token["expire_time"] and returned_token["readable_expire_time"]

        # make sure token was written to cache
        cached = oauth_client_fake.cache.get_cached_token()
        assert cached is not None
        assert new_token_info["access_token"] == cached["access_token"]

        # reset code
        oauth_client_fake.access_token_info = None
        oauth_client_fake._code = None
        oauth_client_fake._state = None

        os.remove(oauth_client_fake.cache.path)


class TestGetAccessToken:

    def test_get_access_token_from_state(self, oauth_client_fake):
        """
        Tests returning an access token that is in the current running state
        """
        token_info = {"access_token": 48573490857892, "expire_time": int(time.time()) + 1000}
        oauth_client_fake.access_token_info = token_info
        returned_token = oauth_client_fake.get_access_token()
        assert token_info["access_token"] == returned_token
        oauth_client_fake.access_token_info = None

    def test_get_access_token_from_environment_error(self, oauth_client_fake):
        """
        Tests an exception is raised when the access token cannot be properly converted from an environment variable
        """
        with pytest.raises(ValueError):
            oauth_client_fake.get_access_token(check_env="ACCESS_TOKEN")

    def test_get_access_token_from_environment(self, oauth_client_fake):
        """
        Tests getting a successful
        """
        token_info = {"access_token": 48573490857892, "expire_time": int(time.time()) + 1000}
        # write token to environment
        os.environ["ACCESS_TOKEN"] = str(token_info)
        # method call -> this should return the string for the access token
        returned_token = oauth_client_fake.get_access_token(check_env="ACCESS_TOKEN")
        assert returned_token == token_info["access_token"]

        # delete token from environment
        os.environ.pop("ACCESS_TOKEN")
        oauth_client_fake.access_token_info = None

        # delete cache file
        os.remove(".token-oauth")

    def test_get_access_token_from_cache(self, oauth_client_fake):
        """
        Tests the access token is retrieved from cache if it exists and when it's not expired
        """
        # make a new cache file
        path = '.token-read'
        token_info = {"access_token": 48573490857892, "expire_time": int(time.time()) + 1000}
        cache = CacheHandler(path)
        oauth_client_fake.cache = cache
        oauth_client_fake.cache.write_token_to_cache(token_info)

        returned_token = oauth_client_fake.get_access_token()

        assert returned_token == token_info["access_token"]

        # remove cache file
        os.remove(path)

        oauth_client_fake.access_token_info = None

    def test_get_access_token_from_cache_expired(self, oauth_client_fake):
        """
        Tests that a new access token is requested when the token in cache is expired
        """

        expired_token_info = {'access_token': '123fd681-5541-4af7-9H7f-J038f0c9f5s4a',
                              'token_type': 'bearer',
                              'expires_in': 15044529,
                              'scope': 'tasks:read tasks:write',
                              'expire_time': 1622080846,
                              'readable_expire_time': ''}  # Not actual expire time

        new_token_info = {'access_token': '123fd691-5541-4af7-9H4f-L038e0c9f5W4a',
                          'token_type': 'bearer',
                          'expires_in': 15044529,
                          'scope': 'tasks:read tasks:write',
                          'expire_time': int(time.time()) + 1000,
                          'readable_expire_time': ''}

        path = '.token-read-expired'
        cache = CacheHandler(path)
        oauth_client_fake.cache = cache
        oauth_client_fake.cache.write_token_to_cache(expired_token_info)

        with patch('ticktick.oauth2.OAuth2._request_access_token', return_value=new_token_info):
            returned_token = oauth_client_fake.get_access_token()

        os.remove(path)

        assert returned_token == new_token_info["access_token"]
        assert oauth_client_fake.access_token_info == new_token_info

        oauth_client_fake.access_token_info = None

    def test_get_access_token_from_cache_doesnt_exist(self, oauth_client_fake):
        """
        Tests requesting a new access token when a cached access token doesn't exist
        """
        new_token_info = {'access_token': '123fd691-5541-4af7-9H4f-L038e0c9f5W4a',
                          'token_type': 'bearer',
                          'expires_in': 15044529,
                          'scope': 'tasks:read tasks:write',
                          'expire_time': int(time.time()) + 1000,
                          'readable_expire_time': ''}

        with patch('ticktick.oauth2.OAuth2._request_access_token', return_value=new_token_info):
            returned_token = oauth_client_fake.get_access_token()

        assert returned_token == new_token_info["access_token"]
        assert oauth_client_fake.access_token_info == new_token_info

        oauth_client_fake.access_token_info = None

    def test_get_access_token_check_cache_false(self, oauth_client_fake):
        """
        Tests requesting a new access token when check_cache is false
        """
        new_token_info = {'access_token': '123fd691-5541-4af7-9H4f-L038e0c9f5W4a',
                          'token_type': 'bearer',
                          'expires_in': 15044529,
                          'scope': 'tasks:read tasks:write',
                          'expire_time': int(time.time()) + 1000,
                          'readable_expire_time': ''}

        with patch('ticktick.oauth2.OAuth2._request_access_token', return_value=new_token_info):
            returned_token = oauth_client_fake.get_access_token(check_cache=False)

        assert returned_token == new_token_info["access_token"]
        assert oauth_client_fake.access_token_info == new_token_info

        oauth_client_fake.access_token_info = None


class TestSetExpireTime:

    def test_set_expire_time(self, oauth_client_fake):
        """
        Tests proper setting of expire time token
        """
        # example return value when calling time.time()
        time_example = 1622080846.2064953
        expires_in = 12343254  # random expire time
        token_dict = {
            "expires_in": expires_in
        }
        token_dict = oauth_client_fake._set_expire_time(token_dict)
        # assert "expire_time", "readable_expire_time", and "expires_in" in
        assert len(token_dict) == 3
        assert token_dict["expire_time"]
        assert isinstance(token_dict["readable_expire_time"], str)
        assert token_dict["expires_in"] == expires_in


class TestIsTokenExpired:

    def test_is_token_expired(self, oauth_client_fake):
        """
        Checks if the token is expired
        """
        # already passed expire time
        token_dict = {"expire_time": 1622080846.2064953}

        # should return that the token is expired or true
        assert oauth_client_fake.is_token_expired(token_dict)

    def test_is_token_expired_false(self, oauth_client_fake):
        """
        Checks that a False is returned when the expire time has not passed
        """
        token_dict = {"expire_time": int(time.time()) + 1000}

        # should return false
        assert not oauth_client_fake.is_token_expired(token_dict)


class TestValidateToken:

    def test_validate_token(self, oauth_client_fake):
        """
        Tests returning none if the token cannot be validated
        """
        assert oauth_client_fake.validate_token(None) is None

    def test_validate_token_valid(self, oauth_client_fake):
        """
        Tests returning the valid dictionary if token_dict is valid
        """
        # expire time is after the current moment
        token_dict = {"expire_time": int(time.time()) + 1000}

        # asserts the original dictionary is returned if the token dict is not expired
        assert oauth_client_fake.validate_token(token_dict) == token_dict
