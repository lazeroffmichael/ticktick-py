import datetime
import pytz
import time

from ticktick.helpers.time_zone import convert_local_time_to_utc
from ticktick.helpers.constants import DATE_FORMAT
from ticktick.managers.check_logged_in import logged_in


class TaskManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    @logged_in
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
            project_obj = self._client.get_by_id(list_id, search='lists')
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
        if tags:
            time.sleep(2)

        self._client.sync()
        # Since an unknown server exception is occurring, the response is not returning a proper id.
        # We have to find the newly created task in self.state['tasks'] manually to return the id
        # We can start the traversal from the end of the list though.
        for task in self._client.state['tasks'][::-1]:
            if task['title'] == task_name:
                task_id = task['id']

        return self._client.get_by_id(task_id, search='tasks')

    @logged_in
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

    @logged_in
    def set_repeat(self, task_id: str):
        pass

    @logged_in
    def update(self, task_id: str):
        """
        Pushes any changes remotely that have been done to the task with the id.
        :param task_id:
        :return: Updated object received from the server
        """
        # Find the object
        obj = self._client.get_by_fields(id=task_id, search='tasks')
        if not obj:
            raise ValueError(f"Task Id '{task_id}' Does Not Exist")



        pass

    @logged_in
    def complete(self):
        pass

    @logged_in
    def delete(self, task_id: str) -> str:
        """
        Deletes the task with the passed id remotely if it exists.
        :param task_id: Id of the task to be deleted
        :return: Id of the task deleted
        """
        # Check if the id exists
        obj = self._client.get_by_id(task_id, search='tasks')
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
        return self._client.delete_from_local_state(id=task_id, search='tasks')

    @logged_in
    def get_trash(self):
        pass

    @logged_in
    def move_lists(self, old_list_id: str, new_list_id: str) -> dict:
        """
        Moves all the tasks of the old list into the new list
        :param old_list_id: Id of the old list where the tasks currently reside
        :param new_list_id: Id of the new list where the tasks will be moved
        :return: Object of the list that contains all the tasks.
        """
        # Make sure that old and new id's exist
        if old_list_id != self._client.state['inbox_id']:
            old_list = self._client.get_by_fields(id=old_list_id, search='lists')
            if not old_list:
                raise ValueError(f"List Id '{old_list_id}' Does Not Exist")
            old_list = old_list[0]

        if new_list_id != self._client.state['inbox_id']:
            new_list = self._client.get_by_fields(id=new_list_id, search='lists')
            if not new_list:
                raise ValueError(f"List Id '{new_list_id}' Does Not Exist")
            new_list = new_list[0]

        # Get the tasks from the old list
        tasks = self.get_from_list(old_list_id)
        if not tasks:
            return new_list  # No tasks to move so just return the new list
        task_project = []  # List containing all the tasks that will be updated

        for task in tasks:
            task_project.append({
                'fromProjectId': old_list_id,
                'taskId': task['id'],
                'toProjectId': new_list_id
            })

        url = self._client.BASE_URL + 'batch/taskProject'
        url2 = self._client.BASE_URL + 'batch/task'
        # Make the initial call to move the tasks
        self._client.http_post(url, json=task_project, cookies=self._client.cookies)

        self._client.sync()
        # Return the new_list_id object
        return self._client.get_by_id(new_list_id)

    @logged_in
    def get_from_list(self, list_id: str) -> list:
        """
        Obtains the tasks that are contained in the list with the id
        :param list_id: Id of the list to get the tasks from
        :return: List of task objects
        """
        # Make sure that old and new id's exist
        if list_id != self._client.state['inbox_id']:
            obj = self._client.get_by_fields(id=list_id, search='lists')
            if not obj:
                raise ValueError(f"List Id '{list_id}' Does Not Exist")

        # Get the list of tasks that share the project id
        return self._client.get_by_fields(projectId=list_id, search='tasks')

    @logged_in
    def get_completed(self, start_date: datetime, end_date: datetime = None, full_day: bool = True, time_zone: str = None) -> list:
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
