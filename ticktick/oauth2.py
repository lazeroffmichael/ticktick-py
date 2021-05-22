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

        # Set the access token
        self._access_token_info = None

        # Get the authorization
        self.authorize()

    def authorize(self):
        self._open_auth_url_in_browser()
        self._get_redirected_url()
        self._access_token_info = self.request_authorization_token()
        self._set_expire_time()

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
            "show_dialog": True
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
        webbrowser.open(url)

    def _get_redirected_url(self):
        """
        Prompts the user for the redirected url to parse the token and state
        """
        prompt = "Enter the URL you were redirected to: "
        response = input(prompt)

        # get the parsed parameters from the url
        self._code, self._state = self.get_auth_response_parameters(response)

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

    def request_authorization_token(self):
        """
        Makes the POST request to get the token and returns the token info dictionary

        Docs link: https://developer.ticktick.com/api#/openapi?id=third-step
        :return:
        """
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
        response = self._session.post(self.OBTAIN_TOKEN_URL, params=payload)

        if response.status_code != 200:
            raise RuntimeError("The request for the token could not be completed")

        return response.json()

    def _set_expire_time(self):
        """
        Adds two members to the access_token_info dictionary containing the expire time of the token

        self._access_token_info["expire_time"]: The integer representation of the token expiration
        self._access_token_info["readable_expire_time"]: The readable date in the form like 'Wed Nov 17 15:48:57 2021'
        :return:
        """
        self._access_token_info["expire_time"] = int(time.time()) + self._access_token_info["expires_in"]
        self._access_token_info["readable_expire_time"] = time.asctime(time.localtime(time.time() +
                                                                                      self._access_token_info[
                                                                                          "expires_in"]))

    @staticmethod
    def is_token_expired(token_dict):
        """
        Returns a boolean for if the access token is expired
        :param token_dict:
        :return:
        """
        current_time = int(time.time())
        return token_dict["expires_at"] - current_time < 60

    # TODO: Implement these methods
    def get_token_from_cache(self):
        pass

    def _save_token_info_to_cache(self):
        pass
