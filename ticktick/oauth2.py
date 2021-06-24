import requests
import webbrowser
import time
import logging
import ast
import os

from urllib.parse import urlparse, urlencode, parse_qsl
from ticktick.cache import CacheHandler
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger(__name__)


def requests_retry_session(retries=3,
                           backoff_factor=1,
                           status_forcelist=(405, 500, 502, 504),
                           session=None,
                           allowed_methods=frozenset(['GET', 'POST', 'PUT', 'DELETE'])):
    """
    Method for http retries
    """
    session = session or requests.session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class OAuth2:
    """
    Implements the Authorization flow for TickTick's Open API
    """
    OAUTH_AUTHORIZE_URL = "https://ticktick.com/oauth/authorize"
    OBTAIN_TOKEN_URL = "https://ticktick.com/oauth/token"

    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 redirect_uri: str,
                 scope: str = "tasks:write tasks:read",  # only available options right now
                 state: str = None,
                 session=None,
                 env_key: str = None,
                 cache_path: str = '.token-oauth',
                 check_cache: bool = True
                 ):
        """
        Initialize the object.

        Arguments:
            client_id: Client ID string
            client_secret: Client secret string
            redirect_uri: Redirect uri
            scope: Scope for the permissions. Current options are only the default.
            state (str): State parameter
            session (requests session): Requests session
            env_key: The environment variable name where the access token dictionary is stored as a string literal.
            cache_path: The desired path of the file where the access token information will be stored.
            check_cache: Whether to check the cache file for the access token information

        !!! examples

            === "Standard Method"

                This way would instantiate the steps to get a new access token, or just retrieve the cached one.

                ```python
                oauth = OAuth2(client_id=cliend_id,
                               client_secret=client_secret,
                               redirect_uri=redirect_uri)
                ```

            === "Check Environment Method"

                If you are in a situation where you don't want to keep the cached token file, you can save the
                access token dictionary as a string literal in your environment, and pass the name of the variable to
                prevent having to request a new access token.

                ``` python
                auth_client = OAuth2(client_id=client_id,
                                client_secret=client_secret,
                                redirect_uri=redirect_uri,
                                env_key='ACCESS_TOKEN_DICT')
                ```

                Where in the environment you have declared `ACCESS_TOKEN_DICT` to be
                the string literal of the token dictionary:

                ```
                '{'access_token': '628ff081-5331-4a37-8ddk-021974c9f43g',
                'token_type': 'bearer', 'expires_in': 14772375,
                'scope': 'tasks:read tasks:write',
                'expire_time': 1637192935,
                'readable_expire_time':
                'Wed Nov 17 15:48:55 2021'}'
                ```
        """
        # If a proper session is passed then we will just use the existing session
        self.session = session or requests_retry_session()

        # Set the client_id
        self._client_id = client_id

        # Set the client_secret
        self._client_secret = client_secret

        # Set the redirect_uri
        self._redirect_uri = redirect_uri

        # Set the scope
        self._scope = scope

        # Set the state
        self._state = state

        # Initialize code parameter
        self._code = None

        # Set the cache handler
        self.cache = CacheHandler(cache_path)

        # Set the access token
        self.access_token_info = None

        # get access token
        self.get_access_token(check_cache=check_cache, check_env=env_key)

    def _get_auth_url(self):
        """
        Returns the url for authentication
        """
        payload = {
            "client_id": self._client_id,
            "scope": self._scope,
            "response_type": "code",
            "redirect_uri": self._redirect_uri,
            "state": self._state,
        }

        parameters = urlencode(payload)

        return "%s?%s" % (self.OAUTH_AUTHORIZE_URL, parameters)

    def _open_auth_url_in_browser(self):
        """
        Opens the authorization url in the browser

        Docs link: https://developer.ticktick.com/api#/openapi?id=first-step
        """
        log.info("Providing authentication requires interacting with the web browser. Once you accept the "
                 "authorization you will be redirected to the redirect url that you provided with extra parameters "
                 "provided in the url. Paste the url that you "
                 "were redirected to into the console")
        url = self._get_auth_url()
        webbrowser.open(url)

    def _get_redirected_url(self):
        """
        Prompts the user for the redirected url to parse the token and state
        """
        prompt = "Enter the URL you were redirected to: "
        url = self._get_user_input(prompt)

        # get the parsed parameters from the url
        self._code, self._state = self._get_auth_response_parameters(url)

    @staticmethod
    def _get_user_input(prompt: str = ''):
        """
        Prompts the user for input from the console based on the prompt
        """
        return input(prompt)

    @staticmethod
    def _get_auth_response_parameters(url):
        """
        Gets the code and state members contained in the redirected url.

        Docs link: https://developer.ticktick.com/api#/openapi?id=second-step
        :param url:
        :return:
        """
        # isolates "code" and "state" parameters in a string
        parsed = urlparse(url).query

        # creates a dictionary containing the "code" and "state" parameters returned from the url
        isolated = dict(parse_qsl(parsed))

        # return the parameters
        return isolated["code"], isolated["state"]

    def _request_access_token(self):
        """
        Makes the POST request to get the token and returns the token info dictionary

        Docs link: https://developer.ticktick.com/api#/openapi?id=third-step
        :return:
        """

        # Get the manual authentication from the user, and prompt for the redirected url
        self._open_auth_url_in_browser()
        self._get_redirected_url()

        # create the payload
        payload = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": self._code,
            "grant_type": "authorization_code",  # currently only option
            "scope": self._scope,
            "redirect_uri": self._redirect_uri
        }

        # make the request
        token_info = self._post(self.OBTAIN_TOKEN_URL, params=payload)

        token_info = self._set_expire_time(token_info)
        self.cache.write_token_to_cache(token_info)

        return token_info

    def _post(self, url, **kwargs):
        """
        Sends an http post request with the specified url and keyword arguments.

        Arguments:
            url (str): Url to send the request.
            **kwargs: Arguments to send with the request.

        Returns:
            dict: The json parsed response if possible or just a string of the response text if not.

        Raises:
            RunTimeError: If the request could not be completed.
        """

        response = self.session.post(url, **kwargs)
        if response.status_code != 200:
            raise RuntimeError("POST request could not be completed")

        try:
            return response.json()
        except ValueError:
            return response.text

    def get_access_token(self, check_cache: bool = True, check_env: str = None):
        """
        Retrieves the authorization token from cache or makes a new request for it.


        !!! note
            This method does not need to be called explicitly.

        Arguments:
            check_cache (bool): Boolean on whether to check if the access token is in a cache file.
            check_env (str): The environment variable name where the token dictionary is saved as a string literal.

        Priority order for getting the access token:

        1) From an already set class member in the current running instance

        2) From an environment variable where the token dictionary is in a string literal form,
        and the name of the environment variable name is the value passed to the "check_env" parameter

        3) From a cache file that contains the access token dictionary (normal case)

        4) From a new token request (which will create a new cache file that contains the access
        token dictionary) (initial case if never setup)
        """
        # check the local state for if the access token exists
        if self.access_token_info is not None:
            token_info = self.validate_token(self.access_token_info)
            if token_info is not None:
                self.access_token_info = token_info
                return token_info["access_token"]

        # check if in the environment the access token is set
        if check_env is not None:
            # get the access token string
            token_dict_string = os.getenv(check_env)
            try:
                converted_token_dict = ast.literal_eval(token_dict_string)
            except:
                raise ValueError("Access token in the environment must be a python dictionary contained"
                                 " in a string literal")
            token_info = self.validate_token(converted_token_dict)
            if token_info is not None:
                self.cache.write_token_to_cache(token_info)
                self.access_token_info = token_info
                return token_info["access_token"]

        # check if the cache file exists with the token
        if check_cache:
            token_info = self.validate_token(self.cache.get_cached_token())
            # validate token will always return a valid token
            if token_info is not None:
                self.access_token_info = token_info
                return token_info["access_token"]

        # access token is not stored anywhere, request a new token
        token_info = self._request_access_token()
        self.access_token_info = token_info
        return token_info["access_token"]

    @staticmethod
    def _set_expire_time(token_dict):
        """
        Adds two members to the access_token_info dictionary containing the expire time of the token

        self._access_token_info["expire_time"]: The integer representation of the token expiration
        self._access_token_info["readable_expire_time"]: The readable date in the form like 'Wed Nov 17 15:48:57 2021'
        :return:
        """
        token_dict["expire_time"] = int(time.time()) + token_dict["expires_in"]
        token_dict["readable_expire_time"] = time.asctime(time.localtime(time.time() +
                                                                         token_dict["expires_in"]))
        return token_dict

    @staticmethod
    def is_token_expired(token_dict):
        """
        Returns a boolean for if the access token is expired

        Arguments:
            token_dict (dict): Access token dictionary

        Returns:
            bool: Whether the access token is expired
        """
        current_time = int(time.time())
        return token_dict["expire_time"] - current_time < 60

    def validate_token(self, token_dict):
        """
        Validates whether the access token is valid

        Arguments:
            token_dict (dict): Access token dictionary

        Returns:
            None or dict: None if the token_dict is not valid, else token_dict
        """
        # if the token info dictionary does not exist then bounce
        if token_dict is None:
            return None

        # check if the token is expired
        if self.is_token_expired(token_dict):
            # make a new request for a valid token since there is currently no refresh token
            new_token_dict = self._request_access_token()
            return new_token_dict

        return token_dict  # original token_dict is valid
