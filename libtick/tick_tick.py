import re
import httpx
import os
import pytz

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
    Contains all methods for interacting with TickTick servers
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
        self.lists = []
        self.list_groups = []
        self.list_name_and_body = {}
        self.inbox_id = ''
        self.tags = []
        self.tasks = []
        self.time_zone = ''
        self.profile_id = None

        self.login(username, password)
        self._settings()
        self._initial_sync()

    def login(self, username: str, password: str) -> None:
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
        # Make an HTTP POST request
        response = httpx.post(url, json=user_info, params=parameters)

        # Raise error for any status code other than 200 (OK)
        self.check_status_code(response, 'Could Not Log In -> Invalid Username or Password')

        response_information = response.json()
        self.access_token = response_information['token']
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
        response = httpx.get(url, params=parameters, cookies=self.cookies)
        self.check_status_code(response, 'Could Not Retrieve Values')
        json_dict = response.json()

        self.time_zone = json_dict['timeZone']
        self.profile_id = json_dict['id']

        return response

    @logged_in
    def _initialize_lists_name_and_body(self) -> dict:
        """
        Maps each list (project) name to its attribute body.
        :return: Dictionary
        """
        name_dict = dict()
        for i in self.lists:
            project_name = i['name']
            body = i
            name_dict[project_name] = body

        return name_dict

    @logged_in
    def _initial_sync(self) -> httpx:
        """
        Performs the initial get of the class members from ticktick
        :return:
        """
        response1 = httpx.get(self.INITIAL_BATCH_URL, cookies=self.cookies)
        self.check_status_code(response1, 'Could Not Retrieve Values')
        response = response1.json()

        # Set inboxId
        self.inbox_id = response['inboxId']
        # Set list groups
        self.list_groups = response['projectGroups']
        # Set lists
        self.lists = response['projectProfiles']
        self.list_name_and_body = self._initialize_lists_name_and_body()
        # Set Uncompleted Tasks
        self.tasks = response['syncTaskBean']['update']
        # Set tags
        self.tags = response['tags']

        return response1

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
    #   List (Project) Methods

    @logged_in
    def create_list(self, list_name: str, color_id: str = None, list_type: str = 'TASK') -> httpx:
        """
        Creates a list (project) with the specified parameters.
        :param list_name: Name of the project to be created
        :param color_id: Desired color for the project in hex
        :param list_type: Defaults to normal "TASK" type, or specify 'NOTE' for note type list
        :return: Dictionary containing {list_name:list_id_value}
        """
        if list_name in self.list_name_and_body:
            raise ValueError(f"Invalid List Name '{list_name}' -> It Already Exists")
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
        response = httpx.post(url, json=payload, cookies=self.cookies)
        self.check_status_code(response, 'Could Not Create List')
        self._update_list_name_and_body()

        return response

    @logged_in
    def update_list(self):
        pass

    @logged_in
    def create_list_folder(self, folder_name: str) -> str:
        """
        Creates a list folder
        :param folder_name: Name of the folder
        :return: String declaring success
        """
        # Folder names can be reused

    @logged_in
    def delete_list(self, list_name: str) -> httpx:
        """
        Deletes the list with the passed list_id if it exists
        :param list_name: Id of the list to be deleted
        :return: httpx object
        """
        # Check if the id exists
        if list_name not in self.list_name_and_body:
            raise KeyError(f"List '{list_name}' Does Not Exist To Delete")

        url = self.BASE_URL + 'batch/project'
        payload = {
            'delete': [self.list_name_and_body[list_name]['id']],
        }
        response = httpx.post(url, json=payload, cookies=self.cookies)
        self.check_status_code(response, 'Could Not Delete List')
        self.list_name_and_body.pop(list_name)
        try:
            self.lists.remove(list_name)
        finally:
            return response

    @logged_in
    def archive_list(self, list_name: str) -> httpx:
        """
        Moves the passed list to "Archived Lists" instead of deleting
        :param list_name: Name of the list to be moved
        :return: String specifying the archive was successful
        """
        # Check if the name exists
        if list_name not in self.list_name_and_body:
            raise KeyError(f"List: '{list_name}' Does Not Exist To Archive")

        # Check if the list is already archived
        if self.list_name_and_body[list_name]['closed'] is False or self.list_name_and_body[list_name]['closed'] is None:
            url = self.BASE_URL + 'batch/project'
            self.list_name_and_body[list_name]['closed'] = True
            payload = {
                'update': [self.list_name_and_body[list_name]]
            }
            response = httpx.post(url, json=payload, cookies=self.cookies)
            self.check_status_code(response, 'Could Not Archive List')

        # List still exists so don't delete

        return response

    def create_smart_list(self):
        pass

    @logged_in
    def _get_lists(self) -> list:
        """
        Obtains the attributes for each list (project) in your profile
        :return: List
        """
        url = self.BASE_URL + 'projects'
        response = httpx.get(url, cookies=self.cookies)
        self.check_status_code(response, 'Could Not Retrieve Values')

        return response.json()

    def _update_list_name_and_body(self) -> dict:
        self.lists = self._get_lists()
        self.list_name_and_body = self._initialize_lists_name_and_body()
        return self.list_name_and_body

    #   ---------------------------------------------------------------------------------------------------------------
    #   Focus Timer and Pomodoro Methods

    def start_focus_timer(self):
        """Starts the focus timer"""
        pass

    def start_pomodoro_timer(self):
        pass

    #   ---------------------------------------------------------------------------------------------------------------
    #   Habit Methods
    def create_habit(self):
        pass

    def update_habit(self):
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
    client.create_list('Hello')
    print(client.lists)
    print(client.list_name_and_body)
    client.delete_list('Hello')
    print(client.lists)
    print(client.list_name_and_body)