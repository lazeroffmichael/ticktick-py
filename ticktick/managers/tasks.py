import datetime
import pytz
import time
import uuid
import copy

from ticktick.helpers.time_methods import convert_local_time_to_utc, convert_iso_to_tick_tick_format
from ticktick.helpers.constants import DATE_FORMAT
from ticktick.managers.check_logged_in import logged_in
from calendar import monthrange


class TaskManager:
    """
    !!! info
        Task methods are accessed through the `task` public member of your [`TickTickClient`](api.md) instance.

        ```python
        # Assumes that 'client' is the name that references the TickTickClient instance.

        task = client.task.method()
        ```

    !!! question "Question About Logging In or Other Functionality Available?"
        [API and Important Information](api.md)

    !!! tip
        All supported methods are documented below with usage examples, take a look!

        ** All usage examples assume that `client` is the name referencing the [`TickTickClient`](api.md) instance**

    """

    PRIORITY_DICTIONARY = {'none': 0, 'low': 1, 'medium': 3, 'high': 5}

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    @logged_in
    def create(self,
               name: str,
               start=None,
               end=None,
               priority: str = 'none',
               project: str = None,
               tags: list = None,
               content: str = '',
               tz: str = None,
               ) -> dict:
        """
        Create a task. This method supports single and batch task creation.

        Arguments:
            name: Any string is valid.
            start (datetime): Desired start time.
            end (datetime): Desired end time.
            priority: For a priority other than 'none': 'low', 'medium', 'high'.
            project: The id of the list (project) you want the task to be created in. The default will be your inbox.
            tags: Single string for the label of the tag, or a list of strings of labels for many tags.
            content: Desired text to go into the 'Description' field in the task.
            tz: Timezone string if you want to make your task for a timezone other than the timezone linked to your TickTick account.

        Returns:
            Dictionary of created task object.

        Raises:
            TypeError: If any of the parameter types do not match as specified in the parameters table.
            RunTimeError: If the task could not be created successfully.

        !!! tip "Important!"
            The [`datetime`](https://docs.python.org/3/library/datetime.html) module must be imported to use dates.

            First Way:
                ```python
                import datetime
                date = datetime.datetime(2021, 1, 1)
                ```

            Second Way:
                ```python
                from datetime import datetime
                date = datetime(2021, 1, 1)
                ```

        !!! example "Create A Single Task"
            Creating a single task is simple - specify whatever parameters you want directly.

            === "Just a Name"

                ```python
                title = "Molly's Birthday"
                task = client.task.create(title)
                ```

                ??? success "Result"
                    [![task-just-name.png](https://i.postimg.cc/TPDkqYwC/task-just-name.png)](https://postimg.cc/069d9v7w)

            === "Priority"

                Priorities can be changed using the following strings:

                - 'none' : <span style="color:grey"> *Grey* </span>
                - 'low' : <span style="color:Blue"> *Blue* </span>
                - 'medium' : <span style="color:#f5c71a"> *Yellow* </span>
                - 'high' : <span style="color:Red"> *Red* </span>

                ```python
                title = "Molly's Birthday"
                task = client.task.create(title, priority = 'medium')
                ```

                ??? success "Result"
                    [![task-priority.png](https://i.postimg.cc/QdrvMyqF/task-priority.png)](https://postimg.cc/ZCVw7j2m)

            === "All Day Date"

                An all day task is specified by using a `datetime` object without any hours, minutes, or seconds.
                You can pass your datetime object using either `start` or `end` for all day tasks.

                ```python
                date = datetime(2022, 7, 5)  # 7/5/2022
                title = "Molly's Birthday"
                task = client.task.create(title, start=date, priority='medium')
                ```

                ??? success "Result"
                    [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)

                    ---

                    [![start-date.png](https://i.postimg.cc/PfQwcLF0/start-date.png)](https://postimg.cc/Lhh5gsSV)




            === "Specific Duration"

                A specific duration can be set by using `datetime` objects and specifying both the
                start and end times.

                ```python
                start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
                end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
                title = "Molly's Birthday"
                task = client.task.create(title, start=start_time, end=end_time, priority='medium')
                ```

                ??? success "Result"
                    [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)

                    ---

                    [![duration2.png](https://i.postimg.cc/5tzHmjC7/duration2.png)](https://postimg.cc/xk0TffgM)

            === "Content"

                Content can be any string you want. Use escape sequences for newlines, tabs, etc.

                ```python
                start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
                end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
                title = "Molly's Birthday"
                remember = "Be there at two and don't forget the snacks"
                task = client.task.create(title,
                                          start=start_time,
                                          end=end_time,
                                          priority='medium',
                                          content=remember)
                ```

                ??? success "Result"
                    [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)

                    ---

                    [![content2.png](https://i.postimg.cc/285VK0WB/content2.png)](https://postimg.cc/SjwSX7Dy)

            === "Tags"

                **_Single Tag_:**

                A single tag can be passed as a simple string for the name. The tag will
                be created if it doesn't already exist.

                ```python
                start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
                end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
                title = "Molly's Birthday"
                remember = "Be there at two and don't forget the snacks"
                tag = 'Party'
                task = client.task.create(title,
                                          start=start_time,
                                          end=end_time,
                                          priority='medium',
                                          content=remember,
                                          tags=tag)
                ```

                ??? success "Result"
                    [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)

                    ---

                    [![tags1.png](https://i.postimg.cc/Y9ppmSfm/tags1.png)](https://postimg.cc/t1M0KpcX)

                **_Multiple Tags_:**

                Multiple tags can be added to a task by including all the desired tag names
                in a list.

                ```python
                start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
                end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
                title = "Molly's Birthday"
                remember = "Be there at two and don't forget the snacks"
                tag = ['Party', 'Friends', 'Food']
                task = client.task.create(title,
                                          start=start_time,
                                          end=end_time,
                                          priority='medium',
                                          content=remember,
                                          tags=tag)
                ```

                ??? success "Result"
                    [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)

                    ---

                    [![tags2.png](https://i.postimg.cc/7PtxfwCf/tags2.png)](https://postimg.cc/3WpMqMFT)

            === "Different Time Zone"

                To create the task for a different time zone pass in a time zone string.

                [Time Zone Help](timezones.md)

                ```python
                start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
                end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
                title = "Molly's Birthday"
                remember = "Be there at two and don't forget the snacks"
                tag = ['Party', 'Friends', 'Food']
                timezone = 'America/Costa_Rica'  # Notice the time zone in the result image
                task = client.task.create(title,
                                          start=start_time,
                                          end=end_time,
                                          priority='medium',
                                          content=remember,
                                          tags=tag,
                                          tz=timezone)
                ```

                ??? success "Result"
                    [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)

                    ---

                    [![tz1.png](https://i.postimg.cc/dtrvVdGV/tz1.png)](https://postimg.cc/BXSRhjhr)

            === "Different Project"

                !!! info
                    To create your task inside of a different [project](projects.md) other than your inbox,
                    pass in the ID corresponding to the [project](projects.md) that you want.

                !!! note
                    Your [project](projects.md) must exist before the creation of the task.

                ```python
                # Lets assume that we have a project that is already created and named 'Birthday's'

                project_obj = client.get_by_fields(name="Birthday's", search='projects')  # Get the list (project) object
                birthdays_id = project_obj['id']  # Obtain the id of the object
                start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
                end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
                title = "Molly's Birthday"
                remember = "Be there at two and don't forget the snacks"
                tag = ['Party', 'Friends', 'Food']
                task = client.task.create(title,
                              start=start_time,
                              end=end_time,
                              priority='medium',
                              content=remember,
                              tags=tag,
                              project=birthdays_id)
                ```

                ??? success "Result"

                    [![different-list1.png](https://i.postimg.cc/ncN4vXR5/different-list1.png)](https://postimg.cc/1fcVS3Zc)

                    ---

                    [![different-list2.png](https://i.postimg.cc/Mpz8WmVb/different-list2.png)](https://postimg.cc/0bX4nmtb)

        !!! example "Creating Multiple Tasks At Once (Batch)"

            Creating multiple tasks is also simple, however we have to create the individual
            task objects before passing them to the `create` method. This is efficient on resources if you need
            to create multiple tasks at a single time since the same amount of requests will be required no
            matter how many tasks are being created at once.

            This is accomplished using the [`builder`][managers.tasks.TaskManager.builder] method. Create the task objects with
            [`builder`][managers.tasks.TaskManager.builder] and pass the objects you want to create in a list to the create method.

            If the creation was successful, the created tasks will be returned in the same order as the input. All parameters
            supported with creating a single task are supported here as well.

            ```python
            # Create three tasks in the inbox
            task1 = client.task.builder('Hello I Am Task 1')
            task2 = client.task.builder('Hello I Am Task 2')
            task3 = client.task.builder('Hello I Am Task 3')
            task_objs = [task1, task2, task3]
            created_tasks = client.task.create(task_objs)
            ```

            ??? success "Result"

                [![batch-task.png](https://i.postimg.cc/J0tq8nQW/batch-task.png)](https://postimg.cc/GTwYJbNM)

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
        if tag_list:
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
            for tsk in self._client.state['tasks'][::-1]:  # Task List
                if len(ids) == 0:
                    break
                id = 0
                for id in range(len(ids)):
                    try:
                        if ids[id] in tsk['content']:
                            tsk['content'] = tsk['content'].replace(ids[id], '')
                            update_list[id] = tsk
                            del ids[id]
                            break
                    except:
                        break

        return self._client.task.update(update_list)

    @logged_in
    def create_subtask(self, obj, parent: str):
        """
        Creates a sub-task based off the designated id of the parent task. Can create a single sub-task or multiple sub-tasks.

        Arguments:
            obj (dict): `obj` is a task object or list of task objects.
            parent (str): The id of the task that will be the parent task.

        Returns:
            dict: If a single task - the single task dictionary. If multiple tasks - a list of dictionaries.

        Raises:
            TypeError: `obj` must be a dictionary or list of dictionaries. `parent` must be a string.
            ValueError: If `parent` task doesn't exist.
        """
        if not isinstance(obj, dict) and not isinstance(obj, list):
            raise TypeError('obj must be a dictionary or list of dictionaries')

        if not isinstance(parent, str):
            raise TypeError('parent must be a string')

        if isinstance(obj, dict):
            obj = [obj]

        parent_obj = self._client.get_by_id(search='tasks', obj_id=parent)
        if not parent_obj:
            raise ValueError("Parent task must exist before creating sub-tasks")

        tasks = self._client.task.create(obj)  # Create the tasks
        if isinstance(tasks, dict):
            tasks = [tasks]
        ids = [x['id'] for x in tasks]  # Get the list of ids

        subtasks = []
        for i in ids:  # Create the object dictionaries for setting the subtask
            temp = {
                'parentId': parent,
                'projectId': parent_obj['projectId'],
                'taskId': i
            }
            subtasks.append(temp)

        url = self._client.BASE_URL + 'batch/taskParent'
        response = self._client.http_post(url, json=subtasks, cookies=self._client.cookies)
        self._client.sync()
        # Find and return the updated child objects
        subtasks = []
        for task_id in ids:
            subtasks.append(self._client.get_by_id(task_id, search='tasks'))
        if len(subtasks) == 1:
            return subtasks[0]  # Return just the dictionary object if its a single task
        else:
            return subtasks

    @logged_in
    def set_repeat(self, task_id: str):
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
        """
        Deletes the task with the passed id remotely if it exists.

        !!! tip
            If a parent task is deleted - the children will remain (unlike normal parent task deletion in `TickTick`)

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
            task = {'projectId': task['projectId'], 'taskId': ids}
            tasks = [task]

        else:
            for id in ids:
                task = self._client.get_by_fields(id=id, search='tasks')
                if not task:
                    raise ValueError(f"'Task Id '{id}' Does Not Exist'")
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
    def move_projects(self, old: str, new: str) -> dict:  # TODO Finish Documentation
        """
        Moves all the tasks from the old project to the new project.

        Arguments:
            old: Id of the old project.
            new: Id of the new project.

        Returns:
            The tasks contained in the new project.

        Raises:
            ValueError: If either the old or new projects do not exist.

        !!! example
            Lets assume that we have a project named "School", and another project named "Work". To move all the tasks from "School" to "Work":

            ```python
            school_project = client.
        """
        # Make sure that old and new id's exist
        if old != self._client.inbox_id:
            old_list = self._client.get_by_fields(id=old, search='projects')
            if not old_list:
                raise ValueError(f"Project Id '{old}' Does Not Exist")

        if new != self._client.inbox_id:
            new_list = self._client.get_by_fields(id=new, search='projects')
            if not new_list:
                raise ValueError(f"Project Id '{new}' Does Not Exist")

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
        # Return the tasks in the new list
        return self._client.task.get_from_project(new)

    @logged_in
    def get_from_project(self, project: str) -> list:
        """
        Obtains the tasks that are contained in the project.

        Arguments:
            project: Id of the project to get the tasks from.

        Returns:
            A list of task objects from the project.

        Raises:
            ValueError: If the project id does not exist.
        """
        # Make sure that old and new id's exist
        if project != self._client.inbox_id:
            obj = self._client.get_by_fields(id=project, search='projects')
            if not obj:
                raise ValueError(f"List Id '{project}' Does Not Exist")

        # Get the list of tasks that share the project id
        tasks = self._client.get_by_fields(projectId=project, search='tasks')
        if isinstance(tasks, dict):
            return [tasks]
        else:
            return tasks

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

        if not isinstance(start, datetime.datetime):
            raise TypeError('Start Must Be A Datetime Object')

        if not isinstance(end, datetime.datetime) and end is not None:
            raise TypeError('End Must Be A Datetime Object')

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
                           project: str = None,
                           tags: list = None,
                           content: str = '',
                           ):
        """
        Performs error checks on the remaining task fields.
        :param task_name:
        :param priority:
        :param project:
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
        if project is None or project == self._client.inbox_id:
            project = self._client.inbox_id
        else:
            project_obj = self._client.get_by_id(project, search='projects')
            if not project_obj:
                raise ValueError(f"List id '{project}' Does Not Exist")

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

        fields = {'title': task_name, 'priority': priority, 'projectId': project, 'tags': tags, 'content': content}

        return {**dates, **fields}  # Merge the dictionaries

    @logged_in
    def builder(self,
                name: str,
                start=None,
                end=None,
                priority: str = 'none',
                project: str = None,
                tags: list = None,
                content: str = '',
                tz: str = None
                ) -> dict:
        """
        Builds a task object with the passed fields. Performs proper error checking. This function serves as a helper
        for batch creating tasks in [`create`][managers.tasks.TaskManager.create].

        Arguments:
            name: Any string is valid.
            start (datetime): Desired start time.
            end (datetime): Desired end time.
            priority: For a priority other than 'none': 'low', 'medium', 'high'.
            project: The id of the list (project) you want the task to be created in. The default will be your inbox.
            tags: Single string for the label of the tag, or a list of strings of labels for many tags.
            content: Desired text to go into the 'Description' field in the task.
            tz: Timezone string if you want to make your task for a timezone other than the timezone linked to your TickTick account.

        Returns:
            A dictionary containing the proper fields needed for task creation.

        Raises:
            TypeError: If any of the parameter types do not match as specified in the parameters table.

        !!! example
            ```python
                start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
                end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
                title = "Molly's Birthday"
                remember = "Be there at two and don't forget the snacks"
                tag = ['Party', 'Friends', 'Food']
                task = client.task.builder(title,
                                          start=start_time,
                                          end=end_time,
                                          priority='medium',
                                          content=remember,
                                          tags=tag)
            ```

            ??? success "Result"
                A dictionary object containing the appropriate fields is returned.

                ```python
                {'startDate': '2022-07-05T21:30:00+0000', 'dueDate': '2022-07-06T06:30:00+0000', 'isAllDay': False, 'timeZone': 'America/Los_Angeles',
                'title': "Molly's Birthday", 'priority': 3, 'projectId': 'inbox115781412', 'tags': ['Party', 'Friends', 'Food'],
                'content': "Be there at two and don't forget the snacks"}
                ```

        """

        return self._task_field_checks(task_name=name,
                                       priority=priority,
                                       project=project,
                                       tags=tags,
                                       content=content,
                                       start_date=start,
                                       end_date=end,
                                       time_zone=tz)