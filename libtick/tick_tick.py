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
    :param func: Function that is decorated
    :return: Inner function
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

    def __init__(self, username: str, password: str) -> None:
        """
        Initializes a client session.
        :param username: TickTick Username
        :param password: TickTick Password
        """
        self.access_token = ''
        self.cookies = {}
        self.login(username, password)
        self.lists = self.get_lists_name_and_id()

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

    def create_task(self, task_name: str):
        pass

    def create_tag(self):
        pass

    def get_inbox_id(self):
        pass



    @logged_in
    def create_list(self, list_name: str, color_id: str = None, list_type: str = 'TASK') -> dict:
        """
        Creates a list (project) with the specified parameters.
        :param list_name: Name of the project to be created
        :param color_id: Desired color for the project in hex
        :param list_type: Defaults to normal "TASK" type, or specify 'NOTE' for note type list
        :return: Dictionary containing {list_name:list_id_value}
        """
        """Creates a new list with the passed parameters"""
        if list_name in self.lists:
            raise ValueError('Cannot Create List -> Duplicate Name')

        if list_type != 'TASK' and list_type != 'NOTE':
            raise ValueError('Invalid List Type -> Must be "TASK" or "NOTE"')

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
        self.lists = self.get_lists_name_and_id()
        return {list_name: self.lists[list_name]}

    @logged_in
    def delete_list(self, list_name: str) -> str:
        """
        Deletes the list of the passed name if the list exists.
        :param list_name: Name of the list to be deleted
        :return: Output message that the deletion was successful
        """
        # Check if the name exists
        if list_name not in self.lists:
            raise KeyError(f'"{list_name}" Does Not Exist To Delete')

        url = self.BASE_URL + 'batch/project'
        payload = {
            'delete': [self.lists[list_name]],
        }
        response = httpx.post(url, json=payload, cookies=self.cookies)
        self.check_status_code(response, 'Could Not Delete List')
        # Update class project dictionary
        self.lists = self.get_lists_name_and_id()
        return f'{list_name} Deletion Successful'

    @logged_in
    def get_lists(self) -> list:
        """
        Obtains the attributes for each list (project) in your profile
        :return: List
        """
        url = self.BASE_URL + 'projects'
        response = httpx.get(url, cookies=self.cookies)
        self.check_status_code(response, 'Could Not Retrieve Values')

        return response.json()

    @logged_in
    def get_lists_name_and_id(self) -> dict:
        """
        Maps each list (project) name to its respective id.
        :return: Dictionary
        """
        request = self.get_lists()
        name_dict = dict()
        for task in request:
            name = task['name']
            task_id = task['id']
            name_dict[name] = task_id

        return name_dict

    @logged_in
    def get_summary(self, time_zone: str, start_date: datetime, end_date: datetime = None, full_day: bool = True) -> list:
        """
        Obtains all the attributes for all the completed tasks on the date or range of dates passed.

        A full list of valid time_zone strings are in helpers -> timezones.txt
        SINGLE DAY SUMMARY: get_summary(time_zone, start_date)
        MULTI DAY SUMMARY: get_summary(time_zone, start_date, end_date)
        SPECIFIC TIME RANGE: get_summary(time_zone, start_date, end_date, full_day = False)

        :param time_zone: String specifying the local time zone
        :param start_date: Datetime object
        :param end_date: Datetime object
        :param full_day: Boolean specifying whether hours, minutes, and seconds are to be taken into account for the datetime objects
        :return: list containing all the task attributes
        """
        url = self.BASE_URL + 'project/all/completed'

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

    def start_focus_timer(self):
        """Starts the focus timer"""
        pass

    def start_pomodoro_timer(self):
        pass

    def create_habit(self):
        pass

    def update_habit(self):
        pass

    def create_smart_list(self):
        pass

    def complete_task(self):
        pass

    def get_templates(self):
        # https://api.ticktick.com/api/v2/templates
        pass


if __name__ == '__main__':
    usern = os.getenv('TICKTICK_USER')
    passw = os.getenv('TICKTICK_PASS')
    client = TickTickClient(usern, passw)
    name = 'Yuh2'
    color = '#DD730CDD'
    client.create_list(name, color, list_type='NOTE')

    client.delete_list(name)
