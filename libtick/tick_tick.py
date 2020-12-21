import httpx
import os
import pytz
import re

from datetime import datetime
from helpers.time_zone import convert_local_time_to_utc
from helpers.constants import DATE_FORMAT, VALID_HEX_VALUES


def logged_in(func):
    """
    Serves as a decorator making sure that the instance is still logged in for a function call.
    """

    def call(self, *args, **kwargs):
        if not self.access_token:
            raise RuntimeError('ERROR -> Not Logged In')
        return func(self, *args, **kwargs)

    return call


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
        self._sync()

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

        response = self._post(url, json=user_info, params=parameters)

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
        response = self._get(url, params=parameters)

        self.time_zone = response['timeZone']
        self.profile_id = response['id']

        return response

    @logged_in
    def _sync(self) -> httpx:
        """
        Performs the initial get of the class members from ticktick
        :return:
        """
        response = self._get(self.INITIAL_BATCH_URL, cookies=self.cookies)

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

    def _post(self, url, **kwargs):
        response = self.session.post(url, **kwargs)
        self.check_status_code(response, 'Could Not Complete Request')

        try:
            return response.json()
        except ValueError:
            return response.text

    def _get(self, url, **kwargs):
        response = self.session.get(url, **kwargs)
        self.check_status_code(response, 'Could Not Complete Request')

        try:
            return response.json()
        except ValueError:
            return response.text

    @staticmethod
    def _parse_id(response: httpx) -> str:
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

    #   ---------------------------------------------------------------------------------------------------------------
    #   List (Project) Methods

    @logged_in
    def list_create(self, list_name: str, color_id: str = None, list_type: str = 'TASK', group_id: str = None) -> str:
        """
        Creates a list (project) with the specified parameters.
        :param list_name: Name of the project to be created
        :param color_id: Desired color for the project in hex
        :param list_type: Defaults to normal "TASK" type, or specify 'NOTE' for note type list
        :return: Id of the created list
        """
        # Go through self.state['lists'] and determine if the name already exists
        id_list = self.get_id(search_key='lists', name=list_name)
        if id_list:
            raise ValueError(f"Invalid List Name '{list_name}' -> It Already Exists")

        # Determine if parent list exists
        if group_id is not None:
            parent = self.get_by_id(group_id, search_key='list_folders')
            if not parent:
                raise ValueError(f"Parent Id {group_id} Does Not Exist")

        # Make sure list type is valid
        if list_type != 'TASK' and list_type != 'NOTE':
            raise ValueError(f"Invalid List Type '{list_type}' -> Should be 'TASK' or 'NOTE'")

        if color_id is not None:
            check_color = re.search(VALID_HEX_VALUES, color_id)
            if not check_color:
                raise ValueError('Invalid Hex Color String')

        url = self.BASE_URL + 'batch/project'
        payload = {
            'add': [{'name': list_name,
                     'color': color_id,
                     'kind': list_type,
                     'groupId': group_id
                     }]
        }
        response = self._post(url, json=payload, cookies=self.cookies)
        self._sync()
        return self._parse_id(response)

    @logged_in
    def list_update(self, list_id: str) -> str:
        """
        Updates the list remotely with the passed id
        Make local changes to the list you want to change -> then update
        :param list_id: List id of the list to be updated
        :return: list_id
        """
        # Check if the id exists
        returned_object = self.get_by_id(list_id, search_key='lists')
        if not returned_object:
            raise KeyError(f"List id '{list_id}' Does Not Exist To Update")

        url = self.BASE_URL + 'batch/project'
        payload = {
            'update': [returned_object]
        }
        response = self._post(url, json=payload, cookies=self.cookies)
        self._sync()
        return self._parse_id(response)

    @logged_in
    def list_delete(self, list_id: str) -> str:
        """
        Deletes the list with the passed list_id if it exists
        :param list_id: Id of the list to be deleted
        :return: id of the list that was deleted
        """
        # Check if the id exists
        list_object = self.get_by_id(list_id, search_key='lists')
        if not list_object:
            raise KeyError(f"List id '{list_id}' Does Not Exist To Delete")

        url = self.BASE_URL + 'batch/project'
        payload = {
            'delete': [list_id],
        }
        self._post(url, json=payload, cookies=self.cookies)
        for j in range(len(self.state['lists'])):
            if self.state['lists'][j]['id'] == list_id:
                break
        del self.state['lists'][j]

        return list_id

    @logged_in
    def list_archive(self, list_id: str) -> str:
        """
        Moves the passed list to "Archived Lists" instead of deleting
        :param list_id: Id of the list to be archived
        :return: String specifying the archive was successful
        """
        # Check if the name exists
        obj = self.get_by_id(list_id)
        if not obj:
            raise KeyError(f"List id '{list_id}' Does Not Exist To Archive")

        # Check if the list is already archived
        if obj['closed'] is False or obj['closed'] is None:
            url = self.BASE_URL + 'batch/project'
            obj['closed'] = True
            payload = {
                'update': [obj]
            }
            self._post(url, json=payload, cookies=self.cookies)

        # List still exists so don't delete
        return list_id

    @logged_in
    def list_create_folder(self, folder_name: str) -> httpx:
        """
        Creates a list folder
        :param folder_name: Name of the folder
        :return: httpx response
        """
        # Folder names can be reused
        url = self.BASE_URL + 'batch/projectGroup'
        payload = {
            'add': [{'name': folder_name,
                     'listType': 'group'
                     }]
        }
        response = self._post(url, json=payload, cookies=self.cookies)
        self._sync()
        return self._parse_id(response)

    @logged_in
    def list_update_folder(self, folder_id: str) -> str:
        """
        Updates an already created list remotely
        :param folder_id: Id of the folder to be updated
        :return: Id of the folder updated
        """
        # Check if the id exists
        obj = self.get_by_id(folder_id, search_key='list_folders')
        if not obj:
            raise KeyError(f"Folder id '{folder_id}' Does Not Exist To Update")

        url = self.BASE_URL + 'batch/projectGroup'
        payload = {
            'update': [obj]
        }
        response = self._post(url, json=payload, cookies=self.cookies)
        self._sync()
        return folder_id

    @logged_in
    def list_delete_folder(self, folder_id: str) -> str:
        """
        Deletes the folder and ungroups the lists inside
        :param folder_id:id of the folder
        :return:id of the folder deleted
        """
        # Check if the id exists
        obj = self.get_by_id(folder_id)
        if not obj:
            raise KeyError(f"Folder id '{folder_id}' Does Not Exist To Delete")

        url = self.BASE_URL + 'batch/projectGroup'
        payload = {
            'delete': [folder_id]
        }
        self._post(url, json=payload, cookies=self.cookies)
        for k in range(len(self.state['list_folders'])):
            if self.state['list_folders'][k]['id'] == folder_id:
                break

        del self.state['list_folders'][k]

        return folder_id

    def list_create_smart_list(self):
        pass

    #   ---------------------------------------------------------------------------------------------------------------
    #   Task and Tag Methods
    def task_create(self,
                    task_name: str,
                    date: datetime = None,
                    priority: int = 0,
                    parent_id: str = None,
                    project_id: str = None,
                    tags: list = [],
                    content: str = None
                    ) -> str:
        """
        Creates a Task.
        :param task_name:
        :param date:
        :param priority:
        :param parent_id:
        :param project_id:
        :param tags:
        :param content:
        :return:
        """
        # If a parent id was provided, first check to see if the parent_id exists
        if parent_id is not None:
            parent_obj = self.get_by_id(parent_id)
            if not parent_obj:
                raise ValueError(f"Parent id '{parent_id}' Does Not Exist")
            # The project_id is going to match the parent_id projectId
            project_id = parent_obj['projectId']

        # If the project id is not provided, it will default to the user's inbox string
        if project_id is None:
            project_id = self.state['inbox_id']

        # Check that the priority is 0, 1, 3, or 5
        if priority not in {0, 1, 3, 5}:
            raise ValueError(f"Priority must be 0, 1, 3, or 5")

        url = self.BASE_URL + 'batch/task'
        payload = {
            'add': [{
                'title': task_name,
                #'startDate': date,
                #'priority': priority,
                #'tags': tags,
                #'projectId': project_id,
                #'parentId': parent_id,
                #'content': content,
                #'timeZone': self.time_zone
            }]
        }
        response = self._post(url, json=payload, cookies=self.cookies)
        self._sync()
        self._parse_id(response)

    def task_update(self, task_id: str):
        pass

    def task_complete(self):
        pass

    def task_delete(self, task_id: str) -> str:
        """
        Deletes the task with the passed id remotely if it exists.
        :param task_id: Id of the task to be deleted
        :return: Id of the task deleted
        """
        # Check if the id exists
        obj = self.get_by_id(task_id, search_key='tasks')
        if not obj:
            raise ValueError(f"Task Id '{task_id}' Does Not Exist")

        url = self.BASE_URL + 'batch/task'
        payload = {
            'delete': [{
                'taskId': task_id,
                'projectId': obj['projectId']
            }]
        }
        response = self._post(url, json=payload, cookies=self.cookies)
        for k in range(len(self.state['tasks'])):
            if self.state['tasks'][k]['id'] == task_id:
                break
        del self.state['tasks'][k]
        return task_id

    @logged_in
    def get_summary(self, start_date: datetime, end_date: datetime = None, full_day: bool = True, time_zone: str = None) -> list:
        """
        Obtains all the attributes for all the completed tasks on the date or range of dates passed.

        A full list of valid time_zone strings are in helpers -> timezones.txt
        SINGLE DAY SUMMARY: get_summary(time_zone, start_date)
        MULTI DAY SUMMARY: get_summary(time_zone, start_date, end_date)
        SPECIFIC TIME RANGE: get_summary(time_zone, start_date, end_date, full_day=False)

        :param time_zone: String specifying the local time zone
        :param start_date: Datetime object
        :param end_date: Datetime object
        :param full_day: Boolean specifying whether hours, minutes, and seconds are to be taken into account for the datetime objects
        :return: list containing all the tasks and their attributes
        """
        url = self.BASE_URL + 'project/all/completed'

        if time_zone is None:
            time_zone = self.time_zone

        # Handles case when start_date occurs after end_date
        if end_date is not None and start_date > end_date:
            raise ValueError('Invalid Date Range: Start Date Occurs After End Date')

        # Handles invalid timezone argument
        if time_zone not in pytz.all_timezones_set:
            raise KeyError('Invalid Time Zone')

        # Single Day Entry
        if end_date is None:
            start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            end_date = datetime(start_date.year, start_date.month, start_date.day, 23, 59, 59)

        # Multi DAy -> Full Day Entry
        elif full_day is True and end_date is not None:
            start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)

        # Convert Local Time to UTC time based off the time_zone string specified
        start_date = convert_local_time_to_utc(start_date, time_zone)
        end_date = convert_local_time_to_utc(end_date, time_zone)

        parameters = {
            'from': start_date.strftime(DATE_FORMAT),
            'to': end_date.strftime(DATE_FORMAT),
            'limit': 100
        }
        response = httpx.get(url, params=parameters, cookies=self.cookies)
        self.check_status_code(response, 'Could Not Get Values')
        return response.json()

    #   ---------------------------------------------------------------------------------------------------------------
    #   Tag Methods
    def tag_create(self):
        pass

    def tag_update(self):
        pass

    def tag_delete(self):
        pass

    #   ---------------------------------------------------------------------------------------------------------------
    #   Habit Methods
    def create_habit(self):
        pass

    def update_habit(self):
        pass

    #   ---------------------------------------------------------------------------------------------------------------
    #   Focus Timer and Pomodoro Methods

    def start_focus_timer(self):
        """Starts the focus timer"""
        pass

    def start_pomodoro_timer(self):
        pass

    #   ---------------------------------------------------------------------------------------------------------------
    #   Settings and Misc Methods

    def get_templates(self):
        # https://api.ticktick.com/api/v2/templates
        pass


if __name__ == '__main__':
    usern = os.getenv('TICKTICK_USER')
    passw = os.getenv('TICKTICK_PASS')
    client = TickTickClient(usern, passw)
    name = 'new task'
    response = client.task_create(name)
    print(response)
