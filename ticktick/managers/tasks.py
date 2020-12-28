import datetime
import pytz
from ticktick.helpers.time_zone import convert_local_time_to_utc
from ticktick.helpers.constants import DATE_FORMAT
from ticktick.managers.check_logged_in import logged_in


class TaskManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    def create(self,
               task_name: str,
               date: datetime = None,
               priority: int = 0,
               list_id: str = None,
               tags: list = None,
               content: str = '',
               time_zone: str = None
               ) -> str:
        # task_name: -> No checks have to occur because task names can be repeated
        # priority: -> Have to make sure that it is {0, 1, 3, or 5}, Raise Exception If Otherwise
        if tags is None:
            tags = []
        if priority not in {0, 1, 3, 5}:
            raise ValueError(f"Priority must be 0, 1, 3, or 5")

        # project_id -> Default project id will be none
        if list_id is None:
            list_id = self._client.state['inbox_id']
        else:
            project_obj = self._client.get_by_id(list_id)
            if not project_obj:
                raise ValueError(f"Project id '{list_id}' Does Not Exist")

        # Tag list does not matter -> The user can enter any tag names they want in the list
        if tags is None:
            tags = []

        # Content can be whatever string that the user wants to pass

        # If another time zone is not entered, default to the profile
        if time_zone is None:
            time_zone = self._client.time_zone
        # Date
        if date is not None:
            date = convert_local_time_to_utc(date, time_zone)
            date = date.replace(tzinfo=datetime.timezone.utc).isoformat()
            # ISO 8601 Format Example: 2020-12-23T01:56:07+00:00
            # TickTick Required Format: 2020-12-23T01:56:07+0000 -> Where the last colon is removed for timezone
            # Remove the last colon from the string
            date = date[::-1].replace(":", "", 1)[::-1]

        url = self._client.BASE_URL + 'batch/task'
        payload = {
            'add': [{
                'title': task_name,
                'priority': priority,
                'tags': tags,
                'projectId': list_id,
                'content': content,
                'timeZone': self._client.time_zone,
                'startDate': date
            }]
        }
        response = self._client.session.post(url, json=payload, cookies=self._client.cookies)
        if response.status_code != 200 and response.status_code != 500:
            raise RuntimeError('Could Not Complete Request')
        self._client.sync()
        # Since an unknown exception is occurring, the response is not returning a proper id.
        # We have to find the newly created task in self.state['tasks'] manually to return the id
        # We can start the traversal from the end of the list though.
        for task in self._client.state['tasks'][::-1]:
            if task['title'] == task_name:
                task_id = task['id']

        return task_id

    def create_subtask(self, task_id: str):
        """
        /batch/taskParent
        Create a null task
        Call taskParent
        Update the null task
        :param task_id:
        :return:
        """
        pass

    def set_repeat(self, task_id: str):
        pass

    def update(self, task_id: str):
        pass

    def complete(self):
        pass

    def delete(self, task_id: str) -> str:
        """
        Deletes the task with the passed id remotely if it exists.
        :param task_id: Id of the task to be deleted
        :return: Id of the task deleted
        """
        # Check if the id exists
        obj = self._client.get_by_id(task_id, search_key='tasks')
        if not obj:
            raise ValueError(f"Task Id '{task_id}' Does Not Exist")

        url = self._client.BASE_URL + 'batch/task'
        payload = {
            'delete': [{
                'taskId': task_id,
                'projectId': obj['projectId']
            }]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        for k in range(len(self._client.state['tasks'])):
            if self._client.state['tasks'][k]['id'] == task_id:
                break
        del self._client.state['tasks'][k]
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
        url = self._client.BASE_URL + 'project/all/completed'

        if time_zone is None:
            time_zone = self._client.time_zone

        # Handles case when start_date occurs after end_date
        if end_date is not None and start_date > end_date:
            raise ValueError('Invalid Date Range: Start Date Occurs After End Date')

        # Handles invalid timezone argument
        if time_zone not in pytz.all_timezones_set:
            raise KeyError('Invalid Time Zone')

        # Single Day Entry
        if end_date is None:
            start_date = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            end_date = datetime.datetime(start_date.year, start_date.month, start_date.day, 23, 59, 59)

        # Multi DAy -> Full Day Entry
        elif full_day is True and end_date is not None:
            start_date = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)

        # Convert Local Time to UTC time based off the time_zone string specified
        start_date = convert_local_time_to_utc(start_date, time_zone)
        end_date = convert_local_time_to_utc(end_date, time_zone)

        parameters = {
            'from': start_date.strftime(DATE_FORMAT),
            'to': end_date.strftime(DATE_FORMAT),
            'limit': 100
        }
        response = self._client.http_get(url, params=parameters, cookies=self._client.cookies)
        return response

