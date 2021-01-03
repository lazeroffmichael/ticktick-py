import datetime
import pytz
import time
import uuid

from ticktick.helpers.time_methods import convert_local_time_to_utc, convert_iso_to_tick_tick_format
from ticktick.helpers.constants import DATE_FORMAT
from ticktick.managers.check_logged_in import logged_in
from calendar import monthrange


class TaskManager:
    PRIORITY_DICTIONARY = {'none': 0, 'low': 1, 'medium': 3, 'high': 5}

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    @logged_in
    def create(self,
               name: str,
               start: datetime = None,
               end: datetime = None,
               priority: str = 'none',
               project: str = None,
               tags: list = None,
               content: str = '',
               tz: str = None,
               ) -> dict:
        """
        # TODO: Doc String
        :param name:
        :param start:
        :param end:
        :param priority:
        :param project:
        :param tags:
        :param content:
        :param tz:
        :return:
        """
        if isinstance(name, list):
            # If task name is a list, we will batch create objects
            obj = name
            batch = True
        # Get task object
        elif isinstance(name, str):
            batch = False
            obj = self.builder(name=name,
                               start=start,
                               end=end,
                               priority=priority,
                               project=project,
                               tags=tags,
                               content=content,
                               tz=tz)
            obj = [obj]

        else:
            raise TypeError(f"Required Positional Argument Must Be A String or List of Task Objects")

        tag_list = []
        for o in obj:
            for tag in o['tags']:
                if self._client.get_by_fields(label=tag, search='tags'):
                    continue  # Dont create the tag if it already exists
                tag_obj = self._client.tag.builder(tag)
                same = False
                for objs in tag_list:
                    if objs['label'] == tag_obj['label']:
                        same = True
                if not same:
                    tag_list.append(tag_obj)

        # Batch create the tags
        tags = self._client.tag.create(tag_list)

        if not batch:  # For a single task we will just send it to the update
            return self._client.task.update(obj)

        else:
            # We are going to create a unique identifier and append it to content.
            # We will be able to distinguish which task is which by this identifier
            # Once we find the tasks, we will make one more call to update to remove the
            # Identifier from the content string.
            ids = []
            for task in obj:
                identifier = str(uuid.uuid4())  # Identifier
                ids.append(identifier)
                task['content'] += identifier  # Append the identifier onto the end of it

        url = self._client.BASE_URL + 'batch/task'
        payload = {
            'add': obj
        }
        response = self._client.session.post(url, json=payload, cookies=self._client.cookies)
        if response.status_code != 200 and response.status_code != 500:
            raise RuntimeError('Could Not Complete Request')

        self._client.sync()
        # We will find the tasks by their identifiers
        update_list = [''] * len(obj)
        if batch:
            for tsk in self._client.state['tasks'][::-1]: # Task List
                if len(ids) == 0:
                    break
                id = 0
                for id in range(len(ids)):
                    if ids[id] in tsk['content']:
                        tsk['content'] = tsk['content'].replace(ids[id], '')
                        update_list[id] = tsk
                        break
                del ids[id]

        return self._client.task.update(update_list)

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
    def update(self, obj):
        # TODO
        """
        Pushes any changes remotely that have been done to the task with the id.
        :param  obj: Object or list of objects that you want to update remotely.
        :return: Updated object or list of objects retrieved from the server.
        """
        if not isinstance(obj, dict) and not isinstance(obj, list):
            raise TypeError("Task Objects Must Be A Dictionary or List of Dictionaries.")

        if isinstance(obj, dict):
            tasks = [obj]
        else:
            tasks = obj

        url = self._client.BASE_URL + 'batch/task'
        payload = {
            'update': tasks
        }
        response = self._client.session.post(url, json=payload, cookies=self._client.cookies)
        if response.status_code != 200 and response.status_code != 500:
            raise RuntimeError('Could Not Complete Request')
        response = response.json()
        self._client.sync()

        if len(tasks) == 1:
            return self._client.get_by_id(self._client.parse_id(response), search='tasks')
        else:
            etag = response['id2etag']
            etag2 = list(etag.keys())  # Tag names are out of order
            labels = [x['id'] for x in tasks]  # Tag names are in order
            items = [''] * len(tasks)  # Create enough spots for the objects
            for tag in etag2:
                index = labels.index(tag)  # Object of the index is here
                found = self._client.get_by_id(labels[index], search='tasks')
                items[index] = found  # Place at the correct index
            return items

    @logged_in
    def complete(self, ids):
        """
        Marks the passed task with the id as complete.
        :param ids: Single Id String or List of IDS
        :return: The updated single object or list of objects
        """
        if not isinstance(ids, str) and not isinstance(ids, list):
            raise TypeError("Ids Must Be A String Or List Of Ids")

        tasks = []
        if isinstance(ids, str):
            task = self._client.get_by_fields(id=ids, search='tasks')
            if not task:
                raise ValueError('The Task Does Not Exist To Mark As Complete')
            task[0]['status'] = 2  # Complete
            tasks = task
        else:
            for id in ids:
                task = self._client.get_by_fields(id=id, search='tasks')
                if not task:
                    raise ValueError(f"'Task Id '{id}' Does Not Exist'")
                task[0]['status'] = 2  # Complete
                tasks.append(task[0])

        url = self._client.BASE_URL + 'batch/task'
        payload = {
            'update': tasks
        }
        response = self._client.session.post(url, json=payload, cookies=self._client.cookies)
        if response.status_code != 200 and response.status_code != 500:
            raise RuntimeError('Could Not Complete Request')

        self._client.sync()
        if len(tasks) == 1:
            return tasks[0]
        else:
            return tasks

    @logged_in
    def delete(self, ids) -> str:
        # TODO: Implement multi arg feature
        """
        Deletes the task with the passed id remotely if it exists.
        :param ids: Id of the task to be deleted
        :return: Id of the task deleted
        """
        if not isinstance(ids, str) and not isinstance(ids, list):
            raise TypeError('Ids Must Be A String or List Of Strings')
        tasks = []
        if isinstance(ids, str):
            task = self._client.get_by_fields(id=ids, search='tasks')
            if not task:
                raise ValueError(f"Task '{ids}' Does Not Exist To Delete")
            task = task[0]
            task = {'projectId': task['projectId'], 'taskId': ids}
            tasks = [task]

        else:
            for id in ids:
                task = self._client.get_by_fields(id=id, search='tasks')
                if not task:
                    raise ValueError(f"'Task Id '{id}' Does Not Exist'")
                task = task[0]
                task = {'projectId': task['projectId'], 'taskId': id}
                tasks.append(task)

        url = self._client.BASE_URL + 'batch/task'
        payload = {'delete': tasks}
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        if len(tasks) == 1:
            return self._client.delete_from_local_state(id=ids, search='tasks')
        else:
            return_list = []
            for item in tasks:
                o = self._client.delete_from_local_state(id=item['taskId'], search='tasks')
                return_list.append(o)
            return return_list


    @logged_in
    def get_trash(self):
        pass

    @logged_in
    def move_projects(self, old: str, new: str) -> dict:
        """
        Moves all the tasks of the old list into the new list
        :param old: Id of the old list where the tasks currently reside
        :param new: Id of the new list where the tasks will be moved
        :return: Object of the list that contains all the tasks.
        """
        # Make sure that old and new id's exist
        if old != self._client.state['inbox_id']:
            old_list = self._client.get_by_fields(id=old, search='lists')
            if not old_list:
                raise ValueError(f"List Id '{old}' Does Not Exist")
            old_list = old_list[0]

        if new != self._client.state['inbox_id']:
            new_list = self._client.get_by_fields(id=new, search='lists')
            if not new_list:
                raise ValueError(f"List Id '{new}' Does Not Exist")
            new_list = new_list[0]

        # Get the tasks from the old list
        tasks = self.get_from_project(old)
        if not tasks:
            return new_list  # No tasks to move so just return the new list
        task_project = []  # List containing all the tasks that will be updated

        for task in tasks:
            task_project.append({
                'fromProjectId': old,
                'taskId': task['id'],
                'toProjectId': new
            })

        url = self._client.BASE_URL + 'batch/taskProject'
        url2 = self._client.BASE_URL + 'batch/task'
        # Make the initial call to move the tasks
        self._client.http_post(url, json=task_project, cookies=self._client.cookies)

        self._client.sync()
        # Return the new_list_id object
        return self._client.get_by_id(new)

    @logged_in
    def get_from_project(self, project: str) -> list:
        """
        Obtains the tasks that are contained in the list with the id
        :param project: Id of the list to get the tasks from
        :return: List of task objects
        """
        # Make sure that old and new id's exist
        if project != self._client.state['inbox_id']:
            obj = self._client.get_by_fields(id=project, search='lists')
            if not obj:
                raise ValueError(f"List Id '{project}' Does Not Exist")

        # Get the list of tasks that share the project id
        return self._client.get_by_fields(projectId=project, search='tasks')

    @logged_in
    def get_completed(self, start: datetime, end: datetime = None, full: bool = True, tz: str = None) -> list:
        """
        Obtains the objects for all completed tasks from the given start date and end date
        Note: There is a limit of 100 items for the request

        A full list of valid time_zone strings are in helpers -> timezones.txt
        SINGLE DAY SUMMARY: get_summary(time_zone, start_date)
        MULTI DAY SUMMARY: get_summary(time_zone, start_date, end_date)
        SPECIFIC TIME RANGE: get_summary(time_zone, start_date, end_date, full_day=False)

        :param tz: String specifying the local time zone
        :param start: Datetime object
        :param end: Datetime object
        :param full: Boolean specifying whether hours, minutes, and seconds are to be taken into account for the datetime objects
        :return: list containing all the tasks and their attributes
        """
        url = self._client.BASE_URL + 'project/all/completed'

        if tz is None:
            tz = self._client.time_zone

        # Handles case when start_date occurs after end_date
        if end is not None and start > end:
            raise ValueError('Invalid Date Range: Start Date Occurs After End Date')

        # Handles invalid timezone argument
        if tz not in pytz.all_timezones_set:
            raise KeyError('Invalid Time Zone')

        # Single Day Entry
        if end is None:
            start = datetime.datetime(start.year, start.month, start.day, 0, 0, 0)
            end = datetime.datetime(start.year, start.month, start.day, 23, 59, 59)

        # Multi DAy -> Full Day Entry
        elif full is True and end is not None:
            start = datetime.datetime(start.year, start.month, start.day, 0, 0, 0)
            end = datetime.datetime(end.year, end.month, end.day, 23, 59, 59)

        # Convert Local Time to UTC time based off the time_zone string specified
        start = convert_local_time_to_utc(start, tz)
        end = convert_local_time_to_utc(end, tz)

        parameters = {
            'from': start.strftime(DATE_FORMAT),
            'to': end.strftime(DATE_FORMAT),
            'limit': 100
        }
        response = self._client.http_get(url, params=parameters, cookies=self._client.cookies)
        return response

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
                raise TypeError(f"Invalid Start Date: {start_date} -> Must Be A Datetime Object")
            if not isinstance(start_date, datetime.datetime):
                raise TypeError(f"Invalid End Date: {end_date} -> Must Be A Datetime Object")

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
                raise TypeError(f"Invalid Start Date: {start_date} -> Must Be A Datetime Object")
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
                raise TypeError(f"Invalid End Date: {end_date} -> Must Be A Datetime Object")
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
            raise TypeError(f"Invalid Task Name {task_name} -> Task Name Must Be A String")

        # priority: -> Make sure it is a string
        if not isinstance(priority, str):
            raise TypeError(f"Priority must be 'none', 'low', 'medium', or 'high'")

        # Lower case the input and make sure it is one of the four options
        lower = priority.lower()
        if lower not in self.PRIORITY_DICTIONARY:
            raise TypeError(f"Priority must be 'none', 'low', 'medium', or 'high'")

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

    def builder(self,
                name: str,
                start: datetime = None,
                end: datetime = None,
                priority: str = 'none',
                project: str = None,
                tags: list = None,
                content: str = '',
                tz: str = None
                ) -> dict:
        """
        Builds a task object with the passed fields. Performs proper error checking.
        :param name: Name of the task -> Required
        :param start: Start date of the task
        :param end: End date of the task
        :param priority: Priority level of the task
        :param project: Id of the list that the task should be created in
        :param tags: Tags that you want to include for the task
        :param content: Content that you want to include for the task
        :param tz: Timezone that you want to create the task in
        :return: Dictionary object containing all the values
        """

        return self._task_field_checks(task_name=name,
                                       priority=priority,
                                       list_id=project,
                                       tags=tags,
                                       content=content,
                                       start_date=start,
                                       end_date=end,
                                       time_zone=tz)