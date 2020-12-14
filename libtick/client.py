from datetime import datetime
import calendar
import httpx


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

    def get_summary(self, start_date: datetime, end_date: datetime):
        """
        Returns a dictionary containing the fields for each completed task between the given start_date and end_date
        :param start_date: datetime object containing the calendar date that you want the search to start at
        :param end_date: datetime object containing the calendar date that you want the summary to end at
        :return: dict object

        Normal Full Day Usage: When only year, month, and day values are initialized
            Single Day Summary -> my_dict = object_name.get_summary(datetime(2020, 11, 12), datetime(2020, 11, 12))
            Multi  Day Summary -> my_dict = object_name.get_summary(datetime(2020, 11, 12), datetime(2020, 11, 17))

        Specific Time Range: To choose a specified day and time range, initialize the datetime object with UTC time
            Specific Time Range -> my_dict = object_name.get_summary(datetime(2020, 11, 12, 9, 40), datetime(2020, 11, 15, 12, 40, 5))
        """

        # Check if logged in
        if not self.access_token:
            raise ValueError('You Are Not Logged In')

        url = self.BASE_URL + 'project/all/completed/'

        # Must set time fields for UTC standard for Normal Full Day Usage
        if (start_date.hour == 0 and start_date.minute == 0 and start_date.second == 0 and
            end_date.hour == 0 and end_date.minute == 0 and end_date.second == 0):

            # Change start_date hour to be 8
            start_date = datetime(start_date.year, start_date.month, start_date.day, 8, start_date.minute, start_date.second)

            #
            month_range = calendar.monthrange(end_date.year, end_date.month)
            new_year = end_date.year
            new_month = end_date.month

            if end_date.day == month_range[1] and end_date.month == 12:
                new_day, new_month = 1, 1
                new_year = end_date.year + 1

            elif end_date.day == month_range[1]:
                new_day = 1
                new_month = end_date.month + 1

            else:
                new_day = end_date.day + 1

            end_date = datetime(new_year, new_month, new_day, 7, 59, 0)



        date_string = '%Y-%m-%d %H:%M:%S'

        parameters = {
            'from': start_date.strftime(date_string),
            'to': end_date.strftime(date_string),
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
    #client = TickTickClient()
    #tasks = client.get_summary(datetime(2020, 12, 13, 10), datetime(2020, 12, 13, 16))
    #print(tasks)
    #for task in tasks:
        #print(task['title'])



