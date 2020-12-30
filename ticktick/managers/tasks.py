import datetime
import pytz
import time

from ticktick.helpers.time_methods import convert_local_time_to_utc, convert_iso_to_tick_tick_format
from ticktick.helpers.constants import DATE_FORMAT
from ticktick.managers.check_logged_in import logged_in
from calendar import monthrange


class TaskManager:
    PRIORITY_DICTIONARY = {'none': 0, 'low': 1, 'medium': 3, 'high': 5} # TODO: MAke this 0-3 like tags

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    def _time_checks(self, start_date: datetime = None, end_date: datetime = None, time_zone: str = None):
        """
        Performs the proper checks and conversions for converting datetime object to TickTick time string
        :return: (start_date, end_date)
        """
        # Date
        # If another time zone is not entered, default to the profile
        if time_zone is None:
            time_zone = self._client.time_zone
        else:
            if time_zone not in pytz.all_timezones_set:
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

            if all_day:
                # All day is true, however normally right now if we were to use a date like Jan 1 - Jan 3,
                # TickTick would create a task that is only Jan 1 - Jan 2 since the date would be up to Jan 3
                # Lets account for that by making the date actually be one more than the current end date
                # This will allow for more natural date input for all day tasks
                days = monthrange(end_date.year, end_date.month)
                if end_date.day + 1 > days[1]:  # Last day of the month
                    if end_date.month + 1 > 12:  # Last month of the year
                        year = end_date.year + 1  # Both last day of month and last day of year
                        day = 1
                        month = 1
                    else:  # Not last month of year, just reset the day and increment the month
                        year = end_date.year
                        month = end_date.month + 1
                        day = 1
                else:  # Dont have to worry about incrementing year or month
                    year = end_date.year
                    day = end_date.day + 1
                    month = end_date.month

                end_date = datetime.datetime(year, month, day)  # No hours, mins, or seconds needed
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
            end_date = start_date

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
            end_date = convert_iso_to_tick_tick_format(end_date, time_zone)
            start_date = end_date

        return {'startDate': start_date, 'dueDate': end_date, 'isAllDay': all_day, 'timeZone': time_zone}

    def _task_field_checks(self,
                           start_date: datetime = None,
                           end_date: datetime = None,
                           time_zone: str = None,
                           task_name: str = None,
                           priority: str = 'none',
                           list_id: str = None,
                           tags: list = None,
                           content: str = '',
                           ):
        """
        Performs error checks on the remaining task fields.
        :param task_name:
        :param priority:
        :param list_id:
        :param tags:
        :param content:
        :return:
        """
        dates = self._time_checks(start_date=start_date, end_date=end_date, time_zone=time_zone)
        # task_name: -> Make sure task_name is a string
        if not isinstance(task_name, str):
            raise ValueError(f"Invalid Task Name {task_name} -> Task Name Must Be A String")

        # priority: -> Make sure it is a string
        if not isinstance(priority, str):
            raise ValueError(f"Priority must be 'none', 'low', 'medium', or 'high'")

        # Lower case the input and make sure it is one of the four options
        lower = priority.lower()
        if lower not in self.PRIORITY_DICTIONARY:
            raise ValueError(f"Priority must be 'none', 'low', 'medium', or 'high'")

        # Priority is now an integer value
        priority = self.PRIORITY_DICTIONARY[lower]

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
        else:
            # Check if its a string
            if isinstance(tags, str):
                tags = [tags]
            elif isinstance(tags, list):
                for item in tags:
                    if not isinstance(item, str):
                        raise ValueError(f"Individual Tags Inside List Must Be In String Format")
            else:
                raise ValueError(f"Tags Must Be Passed A Single String, Or As A List Of Strings For Multiple Tags")

        # Content can be whatever string that the user wants to pass but make sure its a string
        if not isinstance(content, str):
            raise ValueError(f"Content Must Be A String")

        fields = {'title': task_name, 'priority': priority, 'projectId': list_id, 'tags': tags, 'content': content}

        return {**dates, **fields}  # Merge the dictionaries

    def build(self,
              task_name: str,
              start_date: datetime = None,
              end_date: datetime = None,
              priority: str = 'none',
              list_id: str = None,
              tags: list = None,
              content: str = '',
              time_zone: str = None
              ) -> dict:
        """
        Builds a task object with the passed fields. Performs proper error checking.
        :param task_name: Name of the task -> Required
        :param start_date: Start date of the task
        :param end_date: End date of the task
        :param priority: Priority level of the task
        :param list_id: Id of the list that the task should be created in
        :param tags: Tags that you want to include for the task
        :param content: Content that you want to include for the task
        :param time_zone: Timezone that you want to create the task in
        :return: Dictionary object containing all the values
        """

        return self._task_field_checks(task_name=task_name,
                                       priority=priority,
                                       list_id=list_id,
                                       tags=tags,
                                       content=content,
                                       start_date=start_date,
                                       end_date=end_date,
                                       time_zone=time_zone)

    @logged_in
    def create(self,
               task_name: str,
               start_date: datetime = None,
               end_date: datetime = None,
               priority: str = 'none',
               list_id: str = None,
               tags: list = None,
               content: str = '',
               time_zone: str = None,
               ) -> dict:
        """
        # TODO: Doc String
        :param task_name:
        :param start_date:
        :param end_date:
        :param priority:
        :param list_id:
        :param tags:
        :param content:
        :param time_zone:
        :return:
        """
        if isinstance(task_name, list):
            # If task name is a list, we will batch create objects
            obj = task_name
            batch = True
        # Get task object
        else:
            batch = False
            obj = self.build(task_name=task_name,
                             start_date=start_date,
                             end_date=end_date,
                             priority=priority,
                             list_id=list_id,
                             tags=tags,
                             content=content,
                             time_zone=time_zone)

        # TODO: Batch create the tags for batch or no batch

        url = self._client.BASE_URL + 'batch/task'
        payload = {
            'add': obj
        }
        response = self._client.session.post(url, json=payload, cookies=self._client.cookies)
        if response.status_code != 200 and response.status_code != 500:
            raise RuntimeError('Could Not Complete Request')

        self._client.sync()
        # Since an unknown server exception is occurring, the response is not returning a proper id.
        # We have to find the newly created task in self.state['tasks'] manually to return the id
        # We can start the traversal from the end of the list though.
        new_list = []
        if batch:
            for item in obj:
                for task in self._client.state['tasks'][::-1]:
                    if task['title'] == item['title']:
                        new_list.append(task)
        else:
            for task in self._client.state['tasks'][::-1]:
                if task['title'] == task_name:
                    return task


        return new_list

    @logged_in
    def duplicate(self):
        # TODO: Allow for specified amount of copies, whether to append copy or not.
        pass

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
        #TODO: Potentially add to create_task
        pass

    @logged_in
    def update(self, task_id: str):
        # TODO
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
        # TODO
        pass

    @logged_in
    def delete(self, task_id: str) -> str:
        # TODO: Implement multi arg feature
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
