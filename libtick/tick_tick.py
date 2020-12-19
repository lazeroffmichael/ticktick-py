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

    #   ---------------------------------------------------------------------------------------------------------------
    #   List (Project) Methods

    @logged_in
    def list_create(self, list_name: str, color_id: str = None, list_type: str = 'TASK',) -> str:
        """
        Creates a list (project) with the specified parameters.
        :param list_name: Name of the project to be created
        :param color_id: Desired color for the project in hex
        :param list_type: Defaults to normal "TASK" type, or specify 'NOTE' for note type list
        :return: Id of the created list
        """
        # Go through self.state['lists'] and determine if the name already exists
        for name in self.state['lists']:
            if name['name'] == list_name:
                raise ValueError(f"Invalid List Name '{list_name}' -> It Already Exists")

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
                     }]
        }
        response = self._post(url, json=payload, cookies=self.cookies)
        self._sync()
        return self._parse_id(response)

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
    def list_update(self):
        pass

    @logged_in
    def list_delete(self, list_id: str) -> str:
        """
        Deletes the list with the passed list_id if it exists
        :param list_id: Id of the list to be deleted
        :return: id of the list that was deleted
        """
        # Check if the id exists
        exists = False
        for ids in range(len(self.state['lists'])):
            if self.state['lists'][ids]['id'] == list_id:
                exists = True
                break

        if not exists:
            raise KeyError(f"List id '{list_id}' Does Not Exist To Delete")

        url = self.BASE_URL + 'batch/project'
        payload = {
            'delete': [list_id],
        }
        response = self._post(url, json=payload, cookies=self.cookies)
        del self.state['lists'][ids]

        return list_id

    @logged_in
    def list_delete_folder(self, folder_id: str) -> str:
        """
        Deletes the folder and ungroups the tasks inside
        :param folder_id:id of the folder
        :return:id of the folder deleted
        """
        # Check if the id exists
        exists = False
        for ids in range(len(self.state['list_folders'])):
            if self.state['list_folders'][ids]['id'] == folder_id:
                exists = True
                break

        if not exists:
            raise KeyError(f"Folder id '{folder_id}' Does Not Exist To Delete")
        url = self.BASE_URL + 'batch/projectGroup'
        payload = {
            'update': [self.state['list_folders'][ids]]
        }
        response = self._post(url, json=payload, cookies=self.cookies)
        self._sync()
        return folder_id

    @logged_in
    def list_archive(self, list_id: str) -> str:
        """
        Moves the passed list to "Archived Lists" instead of deleting
        :param list_id: Id of the list to be archived
        :return: String specifying the archive was successful
        """
        # Check if the name exists
        exists = False
        for ids in range(len(self.state['lists'])):
            if self.state['lists'][ids]['id'] == list_id:
                exists = True
                break
        if not exists:
            raise KeyError(f"List id '{list_id}' Does Not Exist To Archive")

        # Check if the list is already archived
        if self.state['lists'][ids]['closed'] is False or self.state['lists'][ids]['closed'] is None:
            url = self.BASE_URL + 'batch/project'
            self.state['lists'][ids]['closed'] = True
            payload = {
                'update': [self.state['lists'][ids]]
            }
            response = self._post(url, json=payload, cookies=self.cookies)

        # List still exists so don't delete
        return list_id

    def list_create_smart_list(self):
        pass

    #   ---------------------------------------------------------------------------------------------------------------
    #   Task and Tag Methods
    def create_task(self, task_name: str):
        pass

    def complete_task(self):
        pass

    def delete_task(self):
        pass

    def create_tag(self):
        pass

    def get_all_uncompleted_tasks(self):
        pass

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
    response = client.list_create_folder('hello')
    new = client.list_delete_folder(response)
