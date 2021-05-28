import httpx
import webbrowser
import time
import logging

from urllib.parse import urlparse, urlencode, parse_qsl
from ticktick.cache import CacheHandler

log = logging.getLogger(__name__)


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
                 state=None,
                 session=None):
        # If a proper session is passed then we will just use the existing session
        if isinstance(session, httpx.Client):
            self._session = session
        else:
            # build a new session
            self._session = httpx.Client()

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
        self._cache = CacheHandler()

        # Set the access token
        self._access_token_info = None

    def get_auth_url(self):
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
        url = self.get_auth_url()
        response = webbrowser.open(url)

    def _get_redirected_url(self):
        """
        Prompts the user for the redirected url to parse the token and state
        """
        prompt = "Enter the URL you were redirected to: "
        url = self._get_user_input(prompt)

        # get the parsed parameters from the url
        self._code, self._state = self.get_auth_response_parameters(url)

    @staticmethod
    def _get_user_input(prompt: str = ''):
        """
        Prompts the user for input from the console based on the prompt
        """
        return input(prompt)

    @staticmethod
    def get_auth_response_parameters(url):
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
        self._cache.write_token_to_cache(token_info)

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

        response = self._session.post(url, **kwargs)
        if response.status_code != 200:
            raise RuntimeError("POST request could not be completed")

        try:
            return response.json()
        except ValueError:
            return response.text

    def get_access_token(self, check_cache=True):
        """
        Retrieves the authorization token from cache or makes a new request for it.
        """
        if check_cache:
            token_info = self.validate_token(self._cache.get_cached_token())
            # validate token will always return a valid token
            if token_info is not None:
                self._access_token_info = token_info
                return token_info["access_token"]

        token_info = self._request_access_token()
        self._access_token_info = token_info
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
                                                                            token_dict[ "expires_in"]))
        return token_dict

    @staticmethod
    def is_token_expired(token_dict):
        """
        Returns a boolean for if the access token is expired
        :param token_dict:  p;;
        :return:
        """
        current_time = int(time.time())
        return token_dict["expire_time"] - current_time < 60

    def validate_token(self, token_dict):
        """
        Validates whether the access token is valid
        """
        # if the token info dictionary does not exist then bounce
        if token_dict is None:
            return None

        # check if the token is expired
        if self.is_token_expired(token_dict):
            # make a new request for a valid token since there is currently no refresh token
            new_token_dict = self._request_access_token()
            return new_token_dict

        return token_dict   # original token_dict is valid
