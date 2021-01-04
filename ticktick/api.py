import httpx

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
    The `TickTickClient` class is the origin for interactions with the API.
    It is important to understand how the local data for your profile is stored and
    the names that you will interact with in order to access the different features.

    ## Logging In

    !!! info
        A successful login is required.

    !!! success "Initializing Your Session"

        ``` python
        from ticktick import api
        client = api.TickTickClient('username', 'password')  # Enter correct username and password
        ```

        Once you have initialized your session, all interactions will occur through the reference, in this case: ```client```

    ##State

    The `state` public member is a dictionary that contains objects linked to your TickTick profile. The dictionary is
    automatically updated and synced when changes are made through the API.

    !!! example "`state`"

        === "Members"

            The lists are comprised of dictionaries that contain all the fields for each type of object: tasks, tags, etc.

            | Member        | Type |   Contains                          |
            | -----------   | -----|------------------------------------  |
            | `tasks`       | `list` |     All uncompleted task objects |
            | `tags`        | `list` |     All tag objects |
            | `lists`       | `list` |     All list objects |
            | `list_folders`| `list` |     All list folder objects|
            | `inbox_id`    | `str` |      The inbox id for your profile |

        === "Accessing"

            Members can be accessed by normal dictionary indexing using the member strings.

            ```python
            # Assumes that 'client' is the name that references the TickTickClient class.

            uncompleted_tasks = client.state['lists']
            all_tags = client.state['tags']
            ```

        === "Example Task Object"

            ```python
            {'id': '5ff24e4b8f08904035b304d9', 'projectId': 'inbox416323287', 'sortOrder': -1099511627776, 'title': 'Get Groceries', 'content': '', 'startDate': '2021-05-06T21:30:00.000+0000', 'dueDate': '2021-05-06T21:30:00.000+0000', 'timeZone': 'America/Los_Angeles', 'isFloating': False, 'isAllDay': False, 'reminders': [], 'priority': 0, 'status': 0, 'items': [], 'modifiedTime': '2021-01-03T23:07:55.004+0000', 'etag': 'ol2zesef', 'deleted': 0, 'createdTime': '2021-01-03T23:07:55.011+0000', 'creator': 359368200, 'kind': 'TEXT'}
            ```

    ##Functionality

    Different functionality can be accessed through different public members of the `TickTickClient` class:

    !!! info "Method Managers"


        | Member   | Functionality         |
        | ----------- | -------------------|
        | `task`      |       Task Methods |
        | `tag`       |       List Methods |
        | `list`      |       List Methods |
        | `habit`     |      Habit Methods |
        | `pomo`      |       Pomo Methods |
        | `focus`     |      Focus Methods |

    !!! info "Other Public Members"

        | Member   |     Type   |Description                          |
        | ----------- | --------|---------------------------- |
        | `profile_id`| `str`         | Id assigned to your profile |
        | `state` |      `dict`       | Holds all the item objects in your profile (described above)|

    ## Useful Methods

    `TickTickClient` has a lot of helper functions in its documentation...however these should be the only of use methods to you:

    - [`delete_from_local_state`][api.TickTickClient.delete_from_local_state]
    - [`get_by_fields`][api.TickTickClient.get_by_fields]
    - [`get_by_id`][api.TickTickClient.get_by_id]

    ---

    ## `TickTickClient` Class Documentation
    """
    BASE_URL = 'https://api.ticktick.com/api/v2/'
    INITIAL_BATCH_URL = BASE_URL + 'batch/check/0'

    #   ---------------------------------------------------------------------------------------------------------------
    #   Client Initialization

    def __init__(self, username: str, password: str) -> None:
        """
        Initializes a client session. In order to interact with the API
        a successful login must occur. See how to login above.

        Arguments:
            username: TickTick Username
            password: TickTick Password

        Raises:
            RunTimeError: If the login was not successful.
        """
        # Class members

        self._access_token = ''
        self._cookies = {}
        self._session = httpx.Client()
        self._time_zone = ''
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
        """
        Resets the contents of the items in the `state` dictionary.

        """
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

        self._access_token = response['token']
        self._cookies['t'] = self._access_token

    @staticmethod
    def check_status_code(response, error_message: str) -> None:
        """
        Verifies the http response was status code 200.

        Arguments:
            response (httpx): Httpx response
            error_message: Error message to be included with the exception

        Raises:
            RuntimeError: If the status code of the response was not 200.
        """
        if response.status_code != 200:
            raise RuntimeError(error_message)

    @logged_in
    def _settings(self) -> httpx:
        """
        Sets the time_zone and profile_id.

        Returns:
            The httpx response object.
        :return: httpx object containing the response from the get request
        """
        url = self.BASE_URL + 'user/preferences/settings'
        parameters = {
            'includeWeb': True
        }
        response = self.http_get(url, params=parameters)

        self._time_zone = response['timeZone']
        self.profile_id = response['id']

        return response

    @logged_in
    def sync(self):
        """
        Populates the TickTickClient 'state' dictionary with the contents of your account.

        **This method is called when necessary by other methods and does not need to be explicitly called.**

        Returns:
            httpx: The response from the get request.

        Raises:
            RunTimeError: If the request could not be completed.
        """
        response = self.http_get(self.INITIAL_BATCH_URL, cookies=self._cookies)

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
        """
        Sends an http post request to the specified url and keyword arguments.

        Arguments:
            url (str): Url to send the request.
            kwargs: Arguments to send with the request.

        Returns:
            dict: The json parsed response if possible or just a string of the response text if not.

        Raises:
            RunTimeError: If the request could not be completed.
        """
        response = self._session.post(url, **kwargs)
        self.check_status_code(response, 'Could Not Complete Request')

        try:
            return response.json()
        except ValueError:
            return response.text

    def http_get(self, url, **kwargs):
        """
        Sends an http get request to the specified url and keyword arguments.

        Arguments:
            url (str): Url to send the request
            kwargs: Arguments to send with the request

        Returns:
            dict: The json parsed response if possible or just a string of the response text if not.

        Raises:
            RunTimeError: If the request could not be completed.
        """
        response = self._session.get(url, **kwargs)
        self.check_status_code(response, 'Could Not Complete Request')

        try:
            return response.json()
        except ValueError:
            return response.text

    def http_delete(self, url, **kwargs):
        """
        Sends an http delete request to the specified url and keyword arguments.

        Arguments:
            url (str): Url to send the request
            kwargs: Arguments to send with the request

        Returns:
            dict: The json parsed response if possible or just a string of the response text if not.

        Raises:
            RunTimeError: If the request could not be completed.
        """
        response = self._session.delete(url, **kwargs)
        self.check_status_code(response, 'Could Not Complete Request')

        try:
            return response.json()
        except ValueError:
            return response.text

    def http_put(self, url, **kwargs):
        """
        Sends an http put request to the specified url and keyword arguments.

        Arguments:
            url (str): Url to send the request
            kwargs: Arguments to send with the request

        Returns:
            dict: The json parsed response if possible or just a string of the response text if not.

        Raises:
            RunTimeError: If the request could not be completed.
        """
        response = self._session.put(url, **kwargs)
        self.check_status_code(response, 'Could Not Complete Request')

        try:
            return response.json()
        except ValueError:
            return response.text

    @staticmethod
    def parse_id(response: dict) -> str:
        """
        Parses the Id of a successful creation of a TickTick object.
        !!! info
            The response from the TickTick servers is in this form:

            ```md
            {'id2etag': {'5ff2bcf68f08093e5b745a30': '3okkc2xm'}, 'id2error': {}}
            ```
            We want to obtain '5ff2bcf68f08093e5b745a30' in this example - the Id of the object.

        Arguments:
            response: Dictionary containing the Dd from the TickTick servers.

        Returns:
            Id string of the object.
        """
        id_tag = response['id2etag']
        id_tag = list(id_tag.keys())
        return id_tag[0]

    @staticmethod
    def parse_etag(response: dict, multiple: bool = False) -> str:
        """
        Parses the etag of a successful creation of a tag object.

        !!! info
            The response from TickTick upon a successful tag creation is in this form:

            ```md
            {"id2etag":{"MyTag":"vxzpwo38"},"id2error":{}}
            ```
            We want to obtain "vxzpwo38" in this example - the etag of the object.

        Arguments:
            response: Dictionary from the successful creation of a tag object
            multiple: Specifies whether there are multiple etags to return.

        Return:
            A single etag string if not multiple, or a list of etag strings if multiple.
        """
        etag = response['id2etag']
        etag2 = list(etag.keys())
        if not multiple:
            return etag[etag2[0]]
        else:
            etags = []
            for key in range(len(etag2)):
                etags.append(etag[etag2[key]])
            return etags

    def get_by_fields(self, search: str = None, **kwargs) -> list:
        """
        Finds the objects that match the inputted fields.
        If search is specified, it will only search the specific state list.
        :param search: object in self.state
        :param kwargs: fields to look for
        :return: List containing the objects
        """
        if kwargs == {}:
            raise ValueError('Must Include Field(s) To Be Searched For')

        if search is not None and search not in self.state:
            raise KeyError(f"'{search}' Is Not Present In self.state Dictionary")

        objects = []
        if search is not None:
            # If a specific key was passed for self.state
            # Go through self.state[key_name] and see if all the fields in kwargs match
            # If all don't match return empty list
            for index in self.state[search]:
                all_match = True
                for field in kwargs:
                    if kwargs[field] != index[field]:
                        all_match = False
                        break
                if all_match:
                    objects.append(index)

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
                        objects.append(self.state[primarykey][middle_key])

        return objects

    def get_by_id(self, id: str, search: str = None) -> dict:
        """
        Returns the dictionary object of the item corresponding to the passed id
        :param id: Id of the item to be returned
        :param search: Top level key of self.state which makes the search quicker
        :return: Dictionary object containing the item (or empty dictionary)
        """
        # Search just in the desired list
        if search is not None:
            for index in self.state[search]:
                if index['id'] == id:
                    return index

        else:
            # Search all items in self.state
            for prim_key in self.state:
                for our_object in self.state[prim_key]:
                    if 'id' not in our_object:
                        break
                    if our_object['id'] == id:
                        return our_object
        # Return empty dictionary if not found
        return {}

    def get_by_etag(self, etag: str, search: str = None) -> dict:
        if etag is None:
            raise ValueError("Must Pass Etag")

        # Search just in the desired list
        if search is not None:
            for index in self.state[search]:
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

    def delete_from_local_state(self, search: str = None, **kwargs) -> dict:
        """
        Deletes the object that match the fields in the search list from the local state.

        **Does not delete objects remotely, and only deletes a single object.**

        Arguments:
            search: A specific item to look through in the state dictionary. When not specified the entire state dictionary will be searched.
            kwargs: Matching fields in the object to look for.

        Returns:
            The dictionary of the object that was deleted.

        Raises:
            ValueError
        """
        # Check that kwargs is not empty
        if kwargs == {}:
            raise ValueError('Must Include Field(s) To Be Searched For')

        if search is not None and search not in self.state:
            raise KeyError(f"'{search}' Is Not Present In self.state Dictionary")

        # Search just in the desired list
        if search is not None:
            # Go through the state dictionary list and delete the object that matches the fields
            for item in range(len(self.state[search])):
                all_match = True
                for field in kwargs:
                    if kwargs[field] != self.state[search][item][field]:
                        all_match = False
                        break
                if all_match:
                    deleted = self.state[search][item]
                    # Delete the item
                    del self.state[search][item]
                    return deleted

        else:
            # No key passed, search entire self.state dictionary
            # Search the first level of the state dictionary
            for primary_key in self.state:
                skip_primary_key = False
                all_match = True
                middle_key = 0
                # Search the individual lists of the dictionary
                for middle_key in range(len(self.state[primary_key])):
                    if skip_primary_key:
                        break
                    # Match the fields in the kwargs dictionary to the specific object -> if all match add index
                    for fields in kwargs:
                        # if the field doesn't exist, we can assume every other item in the list doesn't have the
                        # field either -> so skip this primary_key entirely
                        if fields not in self.state[primary_key][middle_key]:
                            all_match = False
                            skip_primary_key = True
                            break
                        if kwargs[fields] == self.state[primary_key][middle_key][fields]:
                            all_match = True
                        else:
                            all_match = False
                    if all_match:
                        deleted = self.state[primary_key][middle_key]
                        del self.state[primary_key][middle_key]
                        return deleted
