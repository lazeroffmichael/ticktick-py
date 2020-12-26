import httpx
import os

from ticktick.managers.check_logged_in import logged_in
from ticktick.managers.lists import ListManager
from ticktick.managers.tasks import TaskManager
from ticktick.managers.focus import FocusTimeManager
from ticktick.managers.habits import HabitManager
from ticktick.managers.pomo import PomoManager
from ticktick.managers.settings import SettingsManager
from ticktick.managers.tags import TagsManager


class TickTickClient:
    """
    Class that all api interactions will originate through.
    """
    BASE_URL = 'https://api.ticktick.com/api/v2/'
    INITIAL_BATCH_URL = BASE_URL + 'batch/check/0'

    #   ---------------------------------------------------------------------------------------------------------------
    #   Client Initialization

    def __init__(self, username: str, password: str) -> None:
        """
        Initializes a client session.
        :param username: TickTick Username
        :param password: TickTick Password
        """
        # Class members

        self.access_token = ''
        self.cookies = {}
        self.session = httpx.Client()
        self.time_zone = ''
        self.profile_id = ''
        self.state = {}
        self.reset_local_state()

        self._login(username, password)
        self._settings()
        self.sync()

        # Mangers for the different operations
        self.focus = FocusTimeManager(self)
        self.habit = HabitManager(self)
        self.list = ListManager(self)
        self.pomo = PomoManager(self)
        self.settings = SettingsManager(self)
        self.tag = TagsManager(self)
        self.task = TaskManager(self)

    def reset_local_state(self):
        self.state = {
            'lists': [],
            'list_folders': [],
            'tags': [],
            'tasks': [],
            'user_settings': {},
            'inbox_id': '',
            'profile': {}
        }

    def _login(self, username: str, password: str) -> None:
        """
        Logs in to TickTick and sets the instance access token.
        :param username: TickTick Username
        :param password: TickTick Password
        """
        url = self.BASE_URL + 'user/signon'
        user_info = {
            'username': username,
            'password': password
        }
        parameters = {
            'wc': True,
            'remember': True
        }

        response = self.http_post(url, json=user_info, params=parameters)

        self.access_token = response['token']
        self.cookies['t'] = self.access_token

    @staticmethod
    def check_status_code(response, error_message: str) -> None:
        """
        Makes sure the httpx response was status 200 (ok)
        :param response: httpx request
        :param error_message: Error message to be included with the exception
        :return: None
        """
        if response.status_code != 200:
            raise RuntimeError(error_message)

    @logged_in
    def _settings(self) -> httpx:
        """
        Sets the time_zone and profile_id
        :return: httpx object containing the response from the get request
        """
        url = self.BASE_URL + 'user/preferences/settings'
        parameters = {
            'includeWeb': True
        }
        response = self.http_get(url, params=parameters)

        self.time_zone = response['timeZone']
        self.profile_id = response['id']

        return response

    @logged_in
    def sync(self) -> httpx:
        """
        Performs the initial get of the class members from ticktick
        :return:
        """
        response = self.http_get(self.INITIAL_BATCH_URL, cookies=self.cookies)

        # Inbox Id
        self.state['inbox_id'] = response['inboxId']
        # Set list groups
        self.state['list_folders'] = response['projectGroups']
        # Set lists
        self.state['lists'] = response['projectProfiles']
        # Set Uncompleted Tasks
        self.state['tasks'] = response['syncTaskBean']['update']
        # Set tags
        self.state['tags'] = response['tags']

        return response

    def http_post(self, url, **kwargs):
        response = self.session.post(url, **kwargs)
        self.check_status_code(response, 'Could Not Complete Request')

        try:
            return response.json()
        except ValueError:
            return response.text

    def http_get(self, url, **kwargs):
        response = self.session.get(url, **kwargs)
        self.check_status_code(response, 'Could Not Complete Request')

        try:
            return response.json()
        except ValueError:
            return response.text

    def http_delete(self, url, **kwargs):
        response = self.session.delete(url, **kwargs)
        self.check_status_code(response, 'Could Not Complete Request')

        try:
            return response.json()
        except ValueError:
            return response.text

    @staticmethod
    def parse_id(response: httpx) -> str:
        id_tag = response['id2etag']
        id_tag = list(id_tag.keys())
        return id_tag[0]

    def get_id(self, search_key: str = None, **kwargs) -> list:
        """
        Gets the id of the object with the matching fields. If serach_key is specified, it
        will only search that key in self.state
        :param search_key: object in self.state
        :param kwargs: fields to look for
        :return: list containing the ids
        """
        if kwargs == {}:
            raise ValueError('Must Include Field(s) To Be Searched For')

        if search_key is not None and search_key not in self.state:
            raise KeyError(f"'{search_key}' Is Not Present In self.state Dictionary")

        id_list = []
        if search_key is not None:
            # If a specific key was passed for self.state
            # Go through self.state[key_name] and see if all the fields in kwargs match
            # If all don't match return empty list
            for index in self.state[search_key]:
                all_match = True
                for field in kwargs:
                    if kwargs[field] != index[field]:
                        all_match = False
                        break
                if all_match:
                    id_list.append(index['id'])

        else:
            # No key passed, search entire self.state dictionary
            # Search the first level of the state dictionary
            for primarykey in self.state:
                skip_primary_key = False
                all_match = True
                middle_key = 0
                # Search the individual lists of the dictionary
                for middle_key in range(len(self.state[primarykey])):
                    if skip_primary_key:
                        break
                    # Match the fields in the kwargs dictionary to the specific object -> if all match add index
                    for fields in kwargs:
                        # if the field doesn't exist, we can assume every other item in the list doesn't have the
                        # field either -> so skip this primary_key entirely
                        if fields not in self.state[primarykey][middle_key]:
                            all_match = False
                            skip_primary_key = True
                            break
                        if kwargs[fields] == self.state[primarykey][middle_key][fields]:
                            all_match = True
                        else:
                            all_match = False
                    if all_match:
                        id_list.append(self.state[primarykey][middle_key]['id'])

        return id_list

    def get_by_id(self, id_number: str, search_key: str = None) -> dict:
        """
        Returns the dictionary object of the item corresponding to the passed id
        :param id_number: Id of the item to be returned
        :param search_key: Top level key of self.state which makes the search quicker
        :return: Dictionary object containing the item (or empty dictionary)
        """
        # Search just in the desired list
        if search_key is not None:
            for index in self.state[search_key]:
                if index['id'] == id_number:
                    return index

        else:
            # Search all items in self.state
            for prim_key in self.state:
                for our_object in self.state[prim_key]:
                    if 'id' not in our_object:
                        break
                    if our_object['id'] == id_number:
                        return our_object
        # Return empty dictionary if not found
        return {}

    def get_etag(self, search_key=None, **kwargs) -> list:
        """
        Gets the etag based on the past fields
        :param search_key: Specific state list to look into
        :param kwargs: Fields to compare for
        :return: List of the etags found corresponding to the fields
        """
        if kwargs == {}:
            raise ValueError('Must Include Field(s) To Be Searched For')

        if search_key is not None and search_key not in self.state:
            raise KeyError(f"'{search_key}' Is Not Present In self.state Dictionary")

        id_list = []
        if search_key is not None:
            # If a specific key was passed for self.state
            # Go through self.state[key_name] and see if all the fields in kwargs match
            # If all don't match return empty list
            for index in self.state[search_key]:
                all_match = True
                for field in kwargs:
                    if kwargs[field] != index[field]:
                        all_match = False
                        break
                if all_match:
                    id_list.append(index['etag'])

        else:
            # No key passed, search entire self.state dictionary
            # Search the first level of the state dictionary
            for primarykey in self.state:
                skip_primary_key = False
                all_match = True
                middle_key = 0
                # Search the individual lists of the dictionary
                for middle_key in range(len(self.state[primarykey])):
                    if skip_primary_key:
                        break
                    # Match the fields in the kwargs dictionary to the specific object -> if all match add index
                    for fields in kwargs:
                        # if the field doesn't exist, we can assume every other item in the list doesn't have the
                        # field either -> so skip this primary_key entirely
                        if fields not in self.state[primarykey][middle_key]:
                            all_match = False
                            skip_primary_key = True
                            break
                        if kwargs[fields] == self.state[primarykey][middle_key][fields]:
                            all_match = True
                        else:
                            all_match = False
                    if all_match:
                        id_list.append(self.state[primarykey][middle_key]['etag'])

        return id_list

    def get_by_etag(self, etag: str, search_key: str = None):
        if etag is None:
            raise ValueError("Must Pass Etag")

        # Search just in the desired list
        if search_key is not None:
            for index in self.state[search_key]:
                if index['etag'] == etag:
                    return index

        else:
            # Search all items in self.state
            for prim_key in self.state:
                for our_object in self.state[prim_key]:
                    if 'etag' not in our_object:
                        break
                    if our_object['etag'] == etag:
                        return our_object
        # Return empty dictionary if not found
        return {}

if __name__ == '__main__':
    usern = os.getenv('TICKTICK_USER')
    passw = os.getenv('TICKTICK_PASS')
    client = TickTickClient(usern, passw)


