from datetime import datetime

import httpx
import os

from helpers.time_zone import convert_local_time_to_UTC, date_format


class TickTickClient:
    BASE_URL = 'https://api.ticktick.com/api/v2/'

    def __init__(self, username: str, password: str) -> None:
        """
        Initializes a client session by loggin into TickTick
        :param username: TickTick Username
        :param password: TickTick Password
        """
        self.access_token = ''
        self.cookies = {}
        self.login(username, password)

    def login(self, username: str, password: str) -> None:
        """
        Obtains session token
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
        if response.status_code != 200:
            raise ValueError('Could Not Log In - Invalid Username or Password')

        response_information = response.json()
        self.access_token = response_information['token']
        self.cookies['t'] = self.access_token

    def create_task(self, task_name: str):
        pass

    def create_tag(self):
        pass

    def get_projects(self) -> dict:
        """Returns a dictionary of Project ID Values mapped to project names"""
        pass

    def get_summary(self, start_date: datetime, end_date: datetime, time_zone: str):
        """
        Returns a dictionary containing the fields for each completed task between the given start_date and end_date

        List of timezones can be found in helpers -> timezones.txt
        :param start_date: datetime object containing the calendar date that you want the search to start at
        :param end_date: datetime object containing the calendar date that you want the summary to end at
        :param time_zone: Local time zone string
        :return: dict object
        """
        # Check if logged in
        if not self.access_token:
            raise ValueError('You Are Not Logged In')

        url = self.BASE_URL + 'project/all/completed/'

        if start_date == end_date:
            new_end_hour = 23
            new_end_minute = 59
            end_date = datetime(end_date.year, end_date.month, end_date.day, new_end_hour, new_end_minute)

        start_date = convert_local_time_to_UTC(start_date, time_zone)
        end_date = convert_local_time_to_UTC(end_date, time_zone)

        parameters = {
            'from': start_date.strftime(date_format),
            'to': end_date.strftime(date_format),
            'limit': 100
        }
        request = httpx.get(url, params=parameters, cookies=self.cookies)

        if request.status_code != 200:
            raise ValueError('Could Not Get Values')

        return request.json()

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


if __name__ == '__main__':
    usern = os.getenv('TICKTICK_USER')
    passw = os.getenv('TICKTICK_PASS')
    client = TickTickClient(usern, passw)
    tz = 'US/Pacific'
    tasks = client.get_summary(datetime(2020, 12, 13), datetime(2020, 12, 13))
    print(tasks)
    for task in tasks:
        print(task['title'])
