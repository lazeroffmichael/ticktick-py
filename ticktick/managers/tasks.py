import datetime
import pytz
import time

from ticktick.helpers.time_methods import convert_local_time_to_utc, convert_iso_to_tick_tick_format
from ticktick.helpers.constants import DATE_FORMAT
from ticktick.managers.check_logged_in import logged_in


class TaskManager:

    PRIORITY_DICTIONARY = {'none': 0, 'low': 1, 'medium': 3, 'high': 5}

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    @logged_in
    def create(self,
               task_name: str,
               start_date: datetime = None,
               end_date: datetime = None,
               priority: str = 'none',
               list_id: str = None,
               tags: list = None,
               content: str = '',
               time_zone: str = None
               ) -> str:
        # task_name: -> Make sure task_name is a string
        if not isinstance(task_name, str):
            raise ValueError(f"Invalid Task Name {task_name} -> Task Name Must Be A String")

        # Date
        # If another time zone is not entered, default to the profile
        if time_zone is None:
            time_zone = self._client.time_zone
        else:
            if time_zone not in pytz.all_timezones_set():
                raise ValueError(f"Timezone '{time_zone}' Is Invalid")

        all_day = None  # all day will begin at none
        # Lets first check if both dates  are passed in, and if they are if start date comes before end date
        if start_date is not None and end_date is not None:
            if not isinstance(start_date, datetime.datetime):
                raise ValueError(f"Invalid Start Date: {start_date} -> Must Be A Datetime Object")
            if not isinstance(start_date, datetime.datetime):
                raise ValueError(f"Invalid End Date: {end_date} -> Must Be A Datetime Object")

            # Check that start_date comes before end_date
            if start_date > end_date:
                raise ValueError(f"Start Date: '{start_date}' cannot come after End Date: '{end_date}'")
            if (start_date.hour != 0 or start_date.minute != 0 or start_date.second != 0 or start_date.microsecond != 0
                    or end_date.hour != 0 or end_date.minute != 0 or end_date.second != 0 or end_date.microsecond != 0):
                # A specific hour, minute, second, or microsecond was given - so all day is not false and there
                # is a specific time.
                all_day = False
            else:
                all_day = True
            start_date = convert_iso_to_tick_tick_format(start_date, time_zone)
            end_date = convert_iso_to_tick_tick_format(end_date, time_zone)

        # start_date passed but end_date not passed
        elif start_date is not None and end_date is None:
            if not isinstance(start_date, datetime.datetime):
                raise ValueError(f"Invalid Start Date: {start_date} -> Must Be A Datetime Object")
            # Determine all day
            if start_date.hour != 0 or start_date.minute != 0 or start_date.second != 0 or start_date.microsecond != 0:
                all_day = False
            else:
                all_day = True
            # Parse start_date
            start_date = convert_iso_to_tick_tick_format(start_date, time_zone)

        # end_date passed but start_date not passed
        elif end_date is not None and start_date is None:
            if not isinstance(end_date, datetime.datetime):
                raise ValueError(f"Invalid End Date: {end_date} -> Must Be A Datetime Object")
            # Determine all day
            if end_date.hour != 0 or end_date.minute != 0 or end_date.second != 0 or end_date.microsecond != 0:
                all_day = False
            else:
                all_day = True
            # But end_date will actually take the place of start_date
            start_date = convert_iso_to_tick_tick_format(end_date, time_zone)

        # priority:
        # Lowercase the input and make sure that it is in the priority dictionary
        if priority.lower() not in self.PRIORITY_DICTIONARY:
            raise ValueError(f"Priority must be 'none', 'low', 'medium', or 'high'")

        priority = self.PRIORITY_DICTIONARY[priority]

        # project_id -> Default project id will be none
        if list_id is None or list_id == self._client.state['inbox_id']:
            list_id = self._client.state['inbox_id']
        else:
            project_obj = self._client.get_by_id(list_id, search='lists')
            if not project_obj:
                raise ValueError(f"List id '{list_id}' Does Not Exist")

        # Tag list does not matter -> The user can enter any tag names they want in the list
        if tags is None:
            tags = []

        # Content can be whatever string that the user wants to pass
        if not isinstance(content, str):
            raise ValueError(f"Content Must Be A String")

        url = self._client.BASE_URL + 'batch/task'
        payload = {
            'add': [{
                'title': task_name,
                'startDate': start_date,
                'dueDate': end_date,
                'isAllDay': all_day,
                'priority': priority,
                'tags': tags,
                'projectId': list_id,
                'content': content,
                'timeZone': self._client.time_zone
            }]
        }
        response = self._client.session.post(url, json=payload, cookies=self._client.cookies)
        if response.status_code != 200 and response.status_code != 500:
            raise RuntimeError('Could Not Complete Request')
        if tags:
            # A delay has to be added to allow for proper sync of tags created from the server
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
