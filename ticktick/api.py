import secrets

from ticktick.managers.focus import FocusTimeManager
from ticktick.managers.habits import HabitManager
from ticktick.managers.pomo import PomoManager
from ticktick.managers.projects import ProjectManager
from ticktick.managers.settings import SettingsManager
from ticktick.managers.tags import TagsManager
from ticktick.managers.tasks import TaskManager
from ticktick.oauth2 import OAuth2


class TickTickClient:
    BASE_URL = 'https://api.ticktick.com/api/v2/'

    OPEN_API_BASE_URL = 'https://api.ticktick.com'

    INITIAL_BATCH_URL = BASE_URL + 'batch/check/0'

    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0"
    X_DEVICE_ = '{"platform":"web","os":"OS X","device":"Firefox 95.0","name":"unofficial api!","version":4531,' \
                '"id":"6490' + secrets.token_hex(10) + '","channel":"website","campaign":"","websocket":""}'

    HEADERS = {'User-Agent': USER_AGENT,
               'x-device': X_DEVICE_}

    def __init__(self, username: str, password: str, oauth: OAuth2) -> None:
        """
        Initializes a client session. In order to interact with the API
        a successful login must occur.

        Arguments:
            username: TickTick Username
            password: TickTick Password
            oauth: OAuth2 manager

        Raises:
            RunTimeError: If the login was not successful.
        """
        # Class members

        self.access_token = None
        self.cookies = {}
        self.time_zone = ''
        self.profile_id = ''
        self.inbox_id = ''
        self.state = {}
        self.reset_local_state()
        self.oauth_manager = oauth
        self._session = self.oauth_manager.session

        self._prepare_session(username, password)

        # Mangers for the different operations
        self.focus = FocusTimeManager(self)
        self.habit = HabitManager(self)
        self.project = ProjectManager(self)
        self.pomo = PomoManager(self)
        self.settings = SettingsManager(self)
        self.tag = TagsManager(self)
        self.task = TaskManager(self)

    def _prepare_session(self, username, password):
        """
        Creates all the necessary calls to prepare the session
        """
        self._login(username, password)
        self._settings()
        self.sync()

    def reset_local_state(self):
        """
        Resets the contents of the items in the [`state`](api.md#state) dictionary.

        """
        self.state = {
            'projects': [],
            'project_folders': [],
            'tags': [],
            'tasks': [],
            'user_settings': {},
            'profile': {}
        }

    def _login(self, username: str, password: str) -> None:
        """
        Logs in to TickTick and sets the instance access token.

        Arguments:
            username: TickTick Username
            password: TickTick Password

        """
        url = self.BASE_URL + 'user/signin'
        user_info = {
            'username': username,
            'password': password
        }
        parameters = {
            'wc': True,
            'remember': True
        }

        response = self.http_post(url, json=user_info, params=parameters, headers=self.HEADERS)

        self.access_token = response['token']
        self.cookies['t'] = self.access_token

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

    def _settings(self):
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
        response = self.http_get(url, params=parameters, cookies=self.cookies, headers=self.HEADERS)

        self.time_zone = response['timeZone']
        self.profile_id = response['id']

        return response

    def sync(self):
        """
        Populates the `TickTickClient` [`state`](api.md#state) dictionary with the contents of your account.

        **This method is called when necessary by other methods and does not need to be explicitly called.**

        Returns:
            httpx: The response from the get request.

        Raises:
            RunTimeError: If the request could not be completed.
        """
        response = self.http_get(self.INITIAL_BATCH_URL, cookies=self.cookies, headers=self.HEADERS)

        # Inbox Id
        self.inbox_id = response['inboxId']
        # Set list groups
        self.state['project_folders'] = response['projectGroups']
        # Set lists
        self.state['projects'] = response['projectProfiles']
        # Set Uncompleted Tasks
        self.state['tasks'] = response['syncTaskBean']['update']
        # Set tags
        self.state['tags'] = response['tags']

        return response

    def http_post(self, url, **kwargs):
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
        self.check_status_code(response, 'Could Not Complete Request')

        try:
            return response.json()
        except ValueError:
            return response.text

    def http_get(self, url, **kwargs):
        """
        Sends an http get request with the specified url and keyword arguments.

        Arguments:
            url (str): Url to send the request.
            **kwargs: Arguments to send with the request.

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
        Sends an http delete request with the specified url and keyword arguments.

        Arguments:
            url (str): Url to send the request.
            **kwargs: Arguments to send with the request.

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
        Sends an http put request with the specified url and keyword arguments.

        Arguments:
            url (str): Url to send the request.
            **kwargs: Arguments to send with the request.

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
            We want to obtain '5ff2bcf68f08093e5b745a30' in this example - the id of the object.

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

    def get_by_fields(self, search: str = None, **kwargs):
        """
        Finds and returns the objects in `state` that match the inputted fields.

        If search is specified, it will only search the specific [`state`](api.md#state) list,
        else the entire [`state`](api.md#state) dictionary will be searched.

        !!! example
            Since each TickTick object like tasks, projects, and tags are just dictionaries of fields,
            we can find an object by
            comparing any fields contained in those objects.

            For example: Lets say we have 3 task objects that are titled 'Hello', and we want to obtain all of them.

            The call to the function would look like this:

            ```python
            # Assumes that `client` is the name referencing the TickTickClient instance.

            found_objs = client.get_by_fields(title='Hello')
            ```
            `found_objs` would now reference a list containing the 3 objects with titles 'Hello'.

            Furthermore if we know the type of object we are looking for, we can make the search more efficient by
            specifying the key its located under in the [`state`](#state) dictionary.

            ```python
            # Assumes that `client` is the name referencing the TickTickClient instance.

            found_obj = client.get_by_fields(title='Hello', search='tasks')
            ```

            The search will now only look through `tasks` in [`state`](api.md#state).


        Arguments:
            search: Key in [`state`](api.md#state) that the search should take place in. If empty the
            entire [`state`](api.md#state) dictionary will be searched.
            **kwargs: Matching fields in the object to look for.

        Returns:
            dict or list:
            **Single Object (dict)**: The dictionary of the object.

            **Multiple Objects (list)**: A list of dictionary objects.

            **Nothing Found (list)**: Empty List

        Raises:
            ValueError: If no key word arguments are provided.
            KeyError: If the search key provided is not a key in `state`.
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

        if len(objects) == 1:
            return objects[0]
        else:
            return objects

    def get_by_id(self, obj_id: str, search: str = None) -> dict:
        """
        Returns the dictionary of the object corresponding to the passed id.

        If search is specified, it will only search the specific [`state`](api.md#state) list, else the
        entire [`state`](api.md#state) dictionary will be searched.


        !!! example
            Since each TickTick object like tasks, projects, and tags are just dictionaries of fields,
            we can find an object by
            comparing the id fields.

            For example: Lets get the object that corresponds to an id referenced by `my_id`.

            The call to the function would look like this:

            ```python
            # Assumes that `client` is the name referencing the TickTickClient instance.

            found_obj = client.get_by_id(my_id)
            ```
            `found_obj` would now reference the object if it was found, else it would reference an empty dictionary.

            Furthermore if we know the type of object we are looking for, we can make the search more efficient by
            specifying the key its located under in the [`state`](api.md#state) dictionary.

            ```python
            # Assumes that `client` is the name referencing the TickTickClient instance.

            found_obj = client.get_by_id(my_id, search='projects')
            ```

            The search will now only look through `projects` in [`state`](api.md#state).

        Arguments:
            obj_id: Id of the item.
            search: Key in [`state`](api.md#state) that the search should take place in. If empty the
            entire [`state`](api.md#state) dictionary will be searched.

        Returns:
            The dictionary object of the item if found, or an empty dictionary if not found.

        Raises:
            KeyError: If the search key provided is not a key in [`state`](api.md#state).
        """
        if search is not None and search not in self.state:
            raise KeyError(f"'{search}' Is Not Present In self.state Dictionary")

        # Search just in the desired list
        if search is not None:
            for index in self.state[search]:
                if index['id'] == obj_id:
                    return index

        else:
            # Search all items in self.state
            for prim_key in self.state:
                for our_object in self.state[prim_key]:
                    if 'id' not in our_object:
                        break
                    if our_object['id'] == obj_id:
                        return our_object
        # Return empty dictionary if not found
        return {}

    def get_by_etag(self, etag: str, search: str = None) -> dict:
        """
        Returns the dictionary object of the item with the matching etag.

        If search is specified, it will only search the specific [`state`](api.md#state) list, else the
        entire [`state`](api.md#state) dictionary will be searched.

        !!! example
            Since each TickTick object like tasks, projects, and tags are just dictionaries of fields,
            we can find an object by
            comparing the etag fields.

            For example: Lets get the object that corresponds to an etag referenced by `my_etag`.

            The call to the function would look like this:

            ```python
            # Assumes that `client` is the name referencing the TickTickClient instance.

            found_obj = client.get_by_etag(my_etag)
            ```
            `found_obj` would now reference the object if it was found, else it would reference an empty dictionary.

            Furthermore if we know the type of object we are looking for, we can make the search more efficient by
            specifying the key its located under in the [`state`](api.md#state) dictionary.

            ```python
            # Assumes that `client` is the name referencing the TickTickClient instance.

            found_obj = client.get_by_etag(my_etag, search='projects')
            ```

            The search will now only look through `projects` in [`state`](api.md#state).

        Arguments:
            etag: The etag of the object that you are looking for.
            search: Key in [`state`](#state) that the search should take place in. If empty the
            entire [`state`](api.md#state) dictionary will be searched.

        Returns:
            The dictionary object of the item if found, or an empty dictionary if not found.

        Raises:
            KeyError: If the search key provided is not a key in [`state`](api.md#state).

        """
        if search is not None and search not in self.state:
            raise KeyError(f"'{search}' Is Not Present In self.state Dictionary")

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
        Deletes a single object from the local `state` dictionary. **Does not delete any items remotely.**

        If search is specified, it will only search the specific [`state`](api.md#state) list,
        else the entire [`state`](api.md#state) dictionary will be searched.

        !!! example
            Since each TickTick object like tasks, lists, and tags are just dictionaries of fields,
            we can find an object by
            comparing the fields.

            For example: Lets say that we wanted to find and delete an existing task object from our local state
            with the name 'Get Groceries'. To do this, we can specify the field(s) that we want to compare for in
            the task objects -> in this case the `title` 'Get Groceries'.

            The call to the function would look like this:

            ```python
            # Assumes that `client` is the name referencing the TickTickClient instance.

            deleted_task = client.delete_from_local_state(title='Get Groceries')
            ```
            `deleted_task` would now hold the object that was deleted from the [`state`](api.md#state)
            dictionary if it was found.

            Furthermore if we know the type of object we are looking for, we can make the search more efficient by
            specifying the key its located under in the [`state`](api.md#state) dictionary.

            ```python
            # Assumes that `client` is the name referencing the TickTickClient instance.

            deleted_task = client.delete_from_local_state(title='Get Groceries', search='tasks')
            ```

            The search will now only look through `tasks` in `state`.


        Arguments:
            search: A specific item to look through in the [`state`](api.md#state) dictionary. When not specified the
            entire [`state`](api.md#state) dictionary will be searched.
            **kwargs: Matching fields in the object to look for.

        Returns:
            The dictionary of the object that was deleted.

        Raises:
            ValueError: If no key word arguments are provided.
            KeyError: If the search key provided is not a key in [`state`](api.md#state).

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
