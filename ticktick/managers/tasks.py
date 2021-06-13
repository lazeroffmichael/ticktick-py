import datetime
import pytz
import time
import uuid
import copy

from ticktick.helpers.time_methods import convert_local_time_to_utc, convert_date_to_tick_tick_format
from ticktick.helpers.constants import DATE_FORMAT
from ticktick.managers.check_logged_in import logged_in
from calendar import monthrange


# TODO Implement support for dates

class TaskManager:
    """
    Handles all interactions for tasks.
    """
    PRIORITY_DICTIONARY = {'none': 0, 'low': 1, 'medium': 3, 'high': 5}

    TASK_CREATE_ENDPOINT = "/open/v1/task"

    def __init__(self, client_class):
        # ._client is a reference to the original client_class
        self._client = client_class

        # declare access token
        self.oauth_access_token = ''

        # set access token to valid oauth access token if available
        if self._client.oauth_manager.access_token_info is not None:
            self.oauth_access_token = self._client.oauth_manager.access_token_info['access_token']

        # create header dictionary
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': 'Bearer {}'.format(self.oauth_access_token)}

    def _generate_create_url(self):
        """
        Returns the endpoint url for task creation
        """

        CREATE_ENDPOINT = "/open/v1/task"
        return self._client.OPEN_API_BASE_URL + CREATE_ENDPOINT

    def create(self, task):
        """
        Create a task.
        """

        # generate url
        url = self._generate_create_url()

        # make request
        response = self._client.http_post(url=url, json=task, headers=self.headers)

        # sync local state
        self._client.sync()

        # TODO: Figure out tags
        # since the openapi does not explicitly support tag creation - lets create a new tag for the new task
        # try:
        #     tags = task['tag']
        #     if isinstance(tags, str):
        #         # single tag -> check to see if it exists before creating another one
        #         search = self._client.get_by_fields(name=tags, search='tags')
        #     elif:
        #         isinstance(tags, list)
        #         # multiple tags
        #         pass
        # except KeyError:
        #     pass

        # set 'inbox' to be the actual inbox id
        if response['projectId'] == 'inbox':
            response['projectId'] = self._client.inbox_id

        # return response
        return response

    def _generate_update_url(self, taskID: str):
        """
        Generates the url for updating a task based off the taskID
        """

        UPDATE_ENDPOINT = f"/open/v1/task/{taskID}"
        return self._client.OPEN_API_BASE_URL + UPDATE_ENDPOINT

    def update(self, task):
        """
        Update a task. The task should already be created.
        """

        # TODO: Make tags work

        # generate url
        url = self._generate_update_url(task['id'])

        # make request
        response = self._client.http_post(url=url, json=task, headers=self.headers)

        # sync local state
        self._client.sync()

        # return response
        return response

    def _generate_mark_complete_url(self, projectID, taskID):
        """
        Generates the url for marking a task as complete based off the projectID and taskID
        """

        COMPLETE_ENDPOINT = f"/open/v1/project/{projectID}/task/{taskID}/complete"
        return self._client.OPEN_API_BASE_URL + COMPLETE_ENDPOINT

    def complete(self, task):
        """
        Marks a task as complete. Pass in the task dictionary to be marked as completed.
        """

        # generate url
        url = self._generate_mark_complete_url(task['projectId'], task['id'])

        # make request
        response = self._client.http_post(url=url, json=task, headers=self.headers)

        # sync local state
        self._client.sync()

        if response == '':
            return task

        # return response
        return response

    def _generate_delete_url(self):
        """
        Generates end point url for task deletion
        """
        return self._client.BASE_URL + 'batch/task'

    def delete(self, task):
        """
        Deletes a task. Supports single task deletion, and batch task deletion.

        For a single task pass in the task dictionary. For multiple tasks pass in a list of task dictionaries.
        """

        # generate url
        url = self._generate_delete_url()

        to_delete = []

        # if its just a dict then we are going to have to make a list object for it
        if isinstance(task, dict):
            # ticktick returns for the 'projectId': 'inbox' instead of the actual inbox id - which is required for
            # proper deletion
            if task['projectId'] == 'inbox':
                task['projectId'] = self._client.inbox_id

            delete_dict = {'projectId': task['projectId'], 'taskId': task['id']}
            to_delete.append(delete_dict)

        # iterate through "task"
        else:
            for item in task:
                if item['projectId'] == 'inbox':
                    item['projectId'] = self._client.inbox_id
                delete_dict = {'projectId': item['projectId'], 'taskId': item['id']}
                to_delete.append(delete_dict)

        payload = {'delete': to_delete}

        # make request
        self._client.http_post(url, json=payload, cookies=self._client.cookies)

        # sync local state
        self._client.sync()

        # return input
        return task

    # @logged_in
    # def create(self,
    #            name: str,
    #            start=None,
    #            end=None,
    #            priority: str = 'none',
    #            project: str = None,
    #            tags: list = None,
    #            content: str = '',
    #            tz: str = None,
    #            ) -> dict:
    #     """
    #     Create a task. This method supports single and batch task creation.
    #
    #     Arguments:
    #         name: Any string is valid.
    #         start (datetime): Desired start time.
    #         end (datetime): Desired end time.
    #         priority: For a priority other than 'none': 'low', 'medium', 'high'.
    #         project: The id of the list (project) you want the task to be created in. The default will be your inbox.
    #         tags: Single string for the label of the tag, or a list of strings of labels for many tags.
    #         content: Desired text to go into the 'Description' field in the task.
    #         tz: Timezone string if you want to make your task for a timezone other than the timezone linked to your TickTick account.
    #
    #     Returns:
    #         Dictionary of created task object.
    #
    #     Raises:
    #         TypeError: If any of the parameter types do not match as specified in the parameters table.
    #         RunTimeError: If the task could not be created successfully.
    #
    #     !!! example "Create A Single Task"
    #         Creating a single task is simple - specify whatever parameters you want directly.
    #
    #         Creating a single task will return the dictionary object of the created task.
    #
    #         === "Just a Name"
    #
    #             ```python
    #             title = "Molly's Birthday"
    #             task = client.task.create(title)
    #             ```
    #
    #             ??? success "Result"
    #                 [![task-just-name.png](https://i.postimg.cc/TPDkqYwC/task-just-name.png)](https://postimg.cc/069d9v7w)
    #
    #         === "Priority"
    #
    #             Priorities can be changed using the following strings:
    #
    #             - 'none' : <span style="color:grey"> *Grey* </span>
    #             - 'low' : <span style="color:Blue"> *Blue* </span>
    #             - 'medium' : <span style="color:#f5c71a"> *Yellow* </span>
    #             - 'high' : <span style="color:Red"> *Red* </span>
    #
    #             ```python
    #             title = "Molly's Birthday"
    #             task = client.task.create(title, priority = 'medium')
    #             ```
    #
    #             ??? success "Result"
    #                 [![task-priority.png](https://i.postimg.cc/QdrvMyqF/task-priority.png)](https://postimg.cc/ZCVw7j2m)
    #
    #         === "All Day Date"
    #
    #             An all day task is specified by using a `datetime` object without any hours, minutes, or seconds.
    #             You can pass your datetime object using either `start` or `end` for all day tasks.
    #
    #             ```python
    #             date = datetime(2022, 7, 5)  # 7/5/2022
    #             title = "Molly's Birthday"
    #             task = client.task.create(title, start=date, priority='medium')
    #             ```
    #
    #             ??? success "Result"
    #                 [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)
    #
    #                 ---
    #
    #                 [![start-date.png](https://i.postimg.cc/PfQwcLF0/start-date.png)](https://postimg.cc/Lhh5gsSV)
    #
    #
    #
    #
    #         === "Specific Duration"
    #
    #             A specific duration can be set by using `datetime` objects and specifying both the
    #             start and end times.
    #
    #             ```python
    #             start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
    #             end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
    #             title = "Molly's Birthday"
    #             task = client.task.create(title, start=start_time, end=end_time, priority='medium')
    #             ```
    #
    #             ??? success "Result"
    #                 [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)
    #
    #                 ---
    #
    #                 [![duration2.png](https://i.postimg.cc/5tzHmjC7/duration2.png)](https://postimg.cc/xk0TffgM)
    #
    #         === "Content"
    #
    #             Content can be any string you want. Use escape sequences for newlines, tabs, etc.
    #
    #             ```python
    #             start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
    #             end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
    #             title = "Molly's Birthday"
    #             remember = "Be there at two and don't forget the snacks"
    #             task = client.task.create(title,
    #                                       start=start_time,
    #                                       end=end_time,
    #                                       priority='medium',
    #                                       content=remember)
    #             ```
    #
    #             ??? success "Result"
    #                 [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)
    #
    #                 ---
    #
    #                 [![content2.png](https://i.postimg.cc/285VK0WB/content2.png)](https://postimg.cc/SjwSX7Dy)
    #
    #         === "Tags"
    #
    #             **_Single Tag_:**
    #
    #             A single tag can be passed as a simple string for the name. The tag will
    #             be created if it doesn't already exist.
    #
    #             ```python
    #             start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
    #             end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
    #             title = "Molly's Birthday"
    #             remember = "Be there at two and don't forget the snacks"
    #             tag = 'Party'
    #             task = client.task.create(title,
    #                                       start=start_time,
    #                                       end=end_time,
    #                                       priority='medium',
    #                                       content=remember,
    #                                       tags=tag)
    #             ```
    #
    #             ??? success "Result"
    #                 [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)
    #
    #                 ---
    #
    #                 [![tags1.png](https://i.postimg.cc/Y9ppmSfm/tags1.png)](https://postimg.cc/t1M0KpcX)
    #
    #             **_Multiple Tags_:**
    #
    #             Multiple tags can be added to a task by including all the desired tag names
    #             in a list.
    #
    #             ```python
    #             start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
    #             end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
    #             title = "Molly's Birthday"
    #             remember = "Be there at two and don't forget the snacks"
    #             tag = ['Party', 'Friends', 'Food']
    #             task = client.task.create(title,
    #                                       start=start_time,
    #                                       end=end_time,
    #                                       priority='medium',
    #                                       content=remember,
    #                                       tags=tag)
    #             ```
    #
    #             ??? success "Result"
    #                 [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)
    #
    #                 ---
    #
    #                 [![tags2.png](https://i.postimg.cc/7PtxfwCf/tags2.png)](https://postimg.cc/3WpMqMFT)
    #
    #         === "Different Time Zone"
    #
    #             To create the task for a different time zone pass in a time zone string.
    #
    #             [Time Zone Help](/usage/helpers/#time-zones)
    #
    #             ```python
    #             start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
    #             end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
    #             title = "Molly's Birthday"
    #             remember = "Be there at two and don't forget the snacks"
    #             tag = ['Party', 'Friends', 'Food']
    #             timezone = 'America/Costa_Rica'  # Notice the time zone in the result image
    #             task = client.task.create(title,
    #                                       start=start_time,
    #                                       end=end_time,
    #                                       priority='medium',
    #                                       content=remember,
    #                                       tags=tag,
    #                                       tz=timezone)
    #             ```
    #
    #             ??? success "Result"
    #                 [![start-date-2.png](https://i.postimg.cc/SNctHGpk/start-date-2.png)](https://postimg.cc/2V8wZh6K)
    #
    #                 ---
    #
    #                 [![tz1.png](https://i.postimg.cc/dtrvVdGV/tz1.png)](https://postimg.cc/BXSRhjhr)
    #
    #         === "Different Project"
    #
    #             !!! info
    #                 To create your task inside of a different [project](projects.md) other than your inbox,
    #                 pass in the ID corresponding to the [project](projects.md) that you want.
    #
    #             !!! note
    #                 Your [project](projects.md) must exist before the creation of the task.
    #
    #             ```python
    #             # Lets assume that we have a project that is already created and named 'Birthday's'
    #
    #             project_obj = client.get_by_fields(name="Birthday's", search='projects')  # Get the list (project) object
    #             birthdays_id = project_obj['id']  # Obtain the id of the object
    #             start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
    #             end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
    #             title = "Molly's Birthday"
    #             remember = "Be there at two and don't forget the snacks"
    #             tag = ['Party', 'Friends', 'Food']
    #             task = client.task.create(title,
    #                           start=start_time,
    #                           end=end_time,
    #                           priority='medium',
    #                           content=remember,
    #                           tags=tag,
    #                           project=birthdays_id)
    #             ```
    #
    #             ??? success "Result"
    #
    #                 [![different-list1.png](https://i.postimg.cc/ncN4vXR5/different-list1.png)](https://postimg.cc/1fcVS3Zc)
    #
    #                 ---
    #
    #                 [![different-list2.png](https://i.postimg.cc/Mpz8WmVb/different-list2.png)](https://postimg.cc/0bX4nmtb)
    #
    #     !!! example "Creating Multiple Tasks At Once (Batch)"
    #
    #         Creating multiple tasks is also simple, however we have to create the individual
    #         task objects before passing them to the `create` method. This is efficient on resources if you need
    #         to create multiple tasks at a single time since the same amount of requests will be required no
    #         matter how many tasks are being created at once.
    #
    #         This is accomplished using the [`builder`][managers.tasks.TaskManager.builder] method. Create the task objects with
    #         [`builder`][managers.tasks.TaskManager.builder] and pass the objects you want to create in a list to the create method.
    #
    #         If the creation was successful, the created tasks will be returned in the same order as the input in a list. All parameters
    #         supported with creating a single task are supported here as well.
    #
    #         ```python
    #         # Create three tasks in the inbox
    #         task1 = client.task.builder('Hello I Am Task 1')
    #         task2 = client.task.builder('Hello I Am Task 2')
    #         task3 = client.task.builder('Hello I Am Task 3')
    #         task_objs = [task1, task2, task3]
    #         created_tasks = client.task.create(task_objs)
    #         ```
    #
    #         ??? success "Result"
    #
    #             [![batch-task.png](https://i.postimg.cc/J0tq8nQW/batch-task.png)](https://postimg.cc/GTwYJbNM)
    #
    #     """
    #     if isinstance(name, list):
    #         # If task name is a list, we will batch create objects
    #         obj = name
    #         batch = True
    #     # Get task object
    #     elif isinstance(name, str):
    #         batch = False
    #         obj = self.builder(name=name,
    #                            start=start,
    #                            end=end,
    #                            priority=priority,
    #                            project=project,
    #                            tags=tags,
    #                            content=content,
    #                            tz=tz)
    #         obj = [obj]
    #
    #     else:
    #         raise TypeError(f"Required Positional Argument Must Be A String or List of Task Objects")
    #
    #     tag_list = []
    #     for o in obj:
    #         for tag in o['tags']:
    #             if self._client.get_by_fields(label=tag, search='tags'):
    #                 continue  # Dont create the tag if it already exists
    #             tag_obj = self._client.tag.builder(tag)
    #             same = False
    #             for objs in tag_list:
    #                 if objs['label'] == tag_obj['label']:
    #                     same = True
    #             if not same:
    #                 tag_list.append(tag_obj)
    #
    #     # Batch create the tags
    #     if tag_list:
    #         tags = self._client.tag.create(tag_list)
    #
    #     if not batch:  # For a single task we will just send it to the update
    #         return self._client.task.update(obj)
    #
    #     else:
    #         # We are going to create a unique identifier and append it to content.
    #         # We will be able to distinguish which task is which by this identifier
    #         # Once we find the tasks, we will make one more call to update to remove the
    #         # Identifier from the content string.
    #         ids = []
    #         for task in obj:
    #             identifier = str(uuid.uuid4())  # Identifier
    #             ids.append(identifier)
    #             task['content'] += identifier  # Append the identifier onto the end of it
    #
    #     url = self._client.BASE_URL + 'batch/task'
    #     payload = {
    #         'add': obj
    #     }
    #     response = self._client.session.post(url, json=payload, cookies=self._client.cookies)
    #     if response.status_code != 200 and response.status_code != 500:
    #         raise RuntimeError('Could Not Complete Request')
    #
    #     self._client.sync()
    #     # We will find the tasks by their identifiers
    #     update_list = [''] * len(obj)
    #     if batch:
    #         for tsk in self._client.state['tasks'][::-1]:  # Task List
    #             if len(ids) == 0:
    #                 break
    #             id = 0
    #             for id in range(len(ids)):
    #                 try:
    #                     if ids[id] in tsk['content']:
    #                         tsk['content'] = tsk['content'].replace(ids[id], '')
    #                         update_list[id] = tsk
    #                         del ids[id]
    #                         break
    #                 except:
    #                     break
    #
    #     return self._client.task.update(update_list)

    def make_subtask(self, obj, parent: str):
        """
        Makes the passed task(s) sub-tasks to the parent task.

        !!! note "Important"
            All of the tasks should already be created prior to using this method. Furthermore,
            the tasks should already be present in the same project as the parent task.

        Arguments:
            obj (dict):
                **Single Sub-Task (dict)**: The task object dictionary.

                **Multiple Sub-Tasks (list)**: A list of task object dictionaries.

            parent (str): The ID of the task that will be the parent task.

        Returns:
            dict:
             **Single Sub-Task (dict)**: Created sub-task dictionary.

             **Multiple Sub-Tasks (list)**: List of created sub-task dictionaries.

        Raises:
            TypeError: `obj` must be a dictionary or list of dictionaries. `parent` must be a string.
            ValueError: If `parent` task doesn't exist.
            ValueError: If `obj` does not share the same project as parent.
            RuntimeError: If the creation was unsuccessful.

        !!! example "Creating Sub-Tasks"
            === "Single Sub-Task Creation"
                Pass the task object that will be made a sub-task to the parent with the passed ID.

                ```python
                # Lets make a task in our inbox named "Read" with a sub-task "50 Pages"
                read_task = client.task.create('Read')
                pages_task = client.task.create('50 pages')
                now_subtask = client.task.make_subtask(pages_task, read_task['id'])
                ```

                ??? success "Result"
                    The dictionary of the sub-task is returned.

                    ```python
                    {'id': '5ffff4968f08af50b4654c6b', 'projectId': 'inbox115781412', 'sortOrder': -3298534883328,
                    'title': '50 pages', 'content': '', 'timeZone': 'America/Los_Angeles', 'isFloating': False,
                    'reminder': '', 'reminders': [], 'priority': 0, 'status': 0, 'items': [],
                    'modifiedTime': '2021-01-14T07:37:36.487+0000', 'etag': 'xv5cjzoz', 'deleted': 0,
                    'createdTime': '2021-01-14T07:36:54.751+0000', 'creator': 115781412,
                    'parentId': '5ffff4968f08af50b4654c62', 'kind': 'TEXT'}
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104558809-4272c400-55f8-11eb-8c55-e2f77c9d1ac8.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104558849-55859400-55f8-11eb-9692-c3e01aa73233.png)

            === "Multiple Sub-Task Creation"
                Pass all the tasks you want to make sub-tasks in a list.

                ```python
                # Lets make a task in our inbox named "Read" with a sub-tasks "50 Pages", "100 Pages", and "200 Pages"
                read_task = client.task.create("Read")
                # Lets batch create our sub-tasks
                fifty_pages = client.task.builder('50 Pages')
                hundred_pages = client.task.builder('100 Pages')
                two_hundred_pages = client.task.builder('200 Pages')
                page_tasks = client.task.create([fifty_pages, hundred_pages, two_hundred_pages])
                # Make the page tasks sub-tasks to read_task
                subtasks = client.task.make_subtask(page_tasks, read_task['id'])
                ```

                ??? success "Result"
                    A list of the sub-tasks is returned.

                    ```python
                    [{'id': '5ffff6348f082c11cc0da84d', 'projectId': 'inbox115781412', 'sortOrder': -5497558138880,
                    'title': '50 Pages', 'content': '', 'timeZone': 'America/Los_Angeles',
                    'isFloating': False, 'reminder': '', 'reminders': [], 'priority': 0, 'status': 0,
                    'items': [], 'modifiedTime': '2021-01-14T07:45:04.032+0000', 'etag': 'avqm3u6o',
                    'deleted': 0, 'createdTime': '2021-01-14T07:43:48.858+0000', 'creator': 567893575,
                    'parentId': '5ffff6348f082c11cc0da84a', 'kind': 'TEXT'},

                    {'id': '5ffff6348f082c11cc0da84e', 'projectId': 'inbox115781412', 'sortOrder': -5497558138880,
                    'title': '100 Pages', 'content': '', 'timeZone': 'America/Los_Angeles',
                    'isFloating': False, 'reminder': '', 'reminders': [], 'priority': 0, 'status': 0,
                    'items': [], 'modifiedTime': '2021-01-14T07:45:04.035+0000', 'etag': '6295mmmu',
                    'deleted': 0, 'createdTime': '2021-01-14T07:43:49.286+0000', 'creator': 567893575,
                    'parentId': '5ffff6348f082c11cc0da84a', 'kind': 'TEXT'},

                    {'id': '5ffff6348f082c11cc0da84f', 'projectId': 'inbox115781412', 'sortOrder': -5497558138880,
                    'title': '200 Pages', 'content': '', 'timeZone': 'America/Los_Angeles',
                    'isFloating': False, 'reminder': '', 'reminders': [], 'priority': 0, 'status': 0,
                    'items': [], 'modifiedTime': '2021-01-14T07:45:04.038+0000', 'etag': 'du59zwck',
                    'deleted': 0, 'createdTime': '2021-01-14T07:43:49.315+0000', 'creator': 567893575,
                    'parentId': '5ffff6348f082c11cc0da84a', 'kind': 'TEXT'}]
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104559418-36d3cd00-55f9-11eb-9004-177671a92474.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104559535-64207b00-55f9-11eb-84cf-ca4f989ea075.png)
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

        ids = []
        # Go through obj and if the projects are different make them the same as parent
        for o in obj:
            if o['projectId'] != parent_obj['projectId']:
                raise ValueError("All tasks must be in the same project as the parent")
            ids.append(o['id'])

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

    # @logged_in
    # def update(self, obj):
    #     """
    #     Updates task(s) remotely. Supports single task update and batch task update.
    #
    #     To update a task, change any field in it's dictionary directly then pass to the method.
    #
    #     !!! tip "For Help On What Fields Are Present In The Task Dictionaries"
    #         [Example `TickTick` Task Dictionary](tasks.md#example-ticktick-task-dictionary)
    #
    #
    #     Arguments:
    #         obj (dict or list):
    #             **Single Task (dict)**: The changed task dictionary object.
    #
    #             **Multiple Tasks (list)**: The changed task dictionary objects in a list.
    #
    #     Returns:
    #         dict or list:
    #         **Single Task (dict)**: The updated task dictionary object.
    #
    #         **Multiple Tasks (list)**: The updated task dictionary objects in a list.
    #
    #     Raises:
    #         TypeError: If `obj` is not a dictionary or list.
    #         RuntimeError: If the updating was unsuccessful.
    #
    #     !!! tip "Formatting Dates Help"
    #         TickTick uses a certain syntax for their dates. To convert a datetime object to a compatible
    #         string to be used for updating dates, see [convert_date_to_tick_tick_format][helpers.time_methods.convert_date_to_tick_tick_format]
    #
    #     !!! example "Updating Tasks"
    #         === "Single Task Update"
    #             Updating a single task requires changing the task dictionary directly, and then
    #             passing the entire object to `update`.
    #
    #             ```python
    #             # Lets say we have a task named "Hang out with Jon" that we want to rename to "Call Jon"
    #             jon_task = client.get_by_fields(title='Hang out with Jon', search='tasks')
    #             # Change the field directly
    #             jon_task['title'] = 'Call Jon'
    #             # Pass the entire object to update.
    #             updated_jon_task = client.task.update(jon_task)
    #             ```
    #
    #             ??? success "Result"
    #                 The updated task dictionary is returned.
    #
    #                 ```python
    #                 {'id': '5fff566fb04b355792c79417', 'projectId': 'inbox115781412', 'sortOrder': -101429947662336,
    #                 'title': 'Call Jon', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
    #                 'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles',
    #                 'isFloating': False, 'isAllDay': True, 'reminders': [], 'exDate': [], 'priority': 0,
    #                 'status': 0, 'items': [], 'progress': 0, 'modifiedTime': '2021-01-13T20:22:07.000+0000',
    #                 'etag': '5qiug0q2', 'deleted': 0, 'createdTime': '2021-01-13T20:22:07.000+0000',
    #                 'creator': 759365027, 'kind': 'TEXT'}
    #                 ```
    #
    #                 **Before**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104506247-f8f38c00-5599-11eb-9f8e-c4bbb256cf03.png)
    #
    #                 **After**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104506300-0e68b600-559a-11eb-952d-ac5d189535b4.png)
    #
    #         === "Multiple Task Update"
    #             Updating multiple tasks requires changing the task dictionaries directly, and then
    #             passing the dictionaries in a list to `update`.
    #
    #             ```python
    #             # Lets say we have a task named "Hang out with Jon" that we want to rename to "Call Jon"
    #             jon_task = client.get_by_fields(title='Hang out with Jon', search='tasks')
    #             # Change the field directly
    #             jon_task['title'] = 'Call Jon'
    #
    #             # Lets say we have another task named "Read Book" that we want to change the progress to 70%.
    #             book_task = client.get_by_fields(title='Read Book', search='tasks')
    #             # Change the field directly
    #             book_task['progress'] = 70
    #
    #             # Create a list of the objects and pass to update
    #             update_tasks = [jon_task, book_task]
    #             updated = client.task.update(update_tasks)
    #             ```
    #
    #             ??? success "Result"
    #                 The updated task dictionaries are returned in a list.
    #
    #                 ```python
    #                 [{'id': '5fff566fb04b355792c79417', 'projectId': 'inbox115781412', 'sortOrder': -101429947662336,
    #                 'title': 'Call Jon', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
    #                 'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles',
    #                 'isFloating': False, 'isAllDay': True, 'reminders': [], 'exDate': [], 'priority': 0,
    #                 'status': 0, 'items': [], 'progress': 0, 'modifiedTime': '2021-01-13T20:29:56.000+0000',
    #                 'etag': 'nxahco6u', 'deleted': 0, 'createdTime': '2021-01-13T20:22:07.000+0000',
    #                 'creator': 557493756, 'kind': 'TEXT'},
    #
    #                 {'id': '5fff584db04b355792c79430', 'projectId': 'inbox115781412', 'sortOrder': -102529459290112,
    #                 'title': 'Read Book', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
    #                 'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles',
    #                 'isFloating': False, 'isAllDay': True, 'reminders': [], 'exDate': [], 'priority': 0,
    #                 'status': 0, 'items': [], 'progress': 70, 'modifiedTime': '2021-01-13T20:30:05.000+0000',
    #                 'etag': 'hdz5rbcj', 'deleted': 0, 'createdTime': '2021-01-13T20:30:05.000+0000',
    #                 'creator': 557493756, 'kind': 'TEXT'}]
    #                 ```
    #
    #                 **Before**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104507072-15dc8f00-559b-11eb-9253-3629e1abc668.png)
    #
    #                 **After**
    #
    #                 Notice the progress icon located near the date now for "Read Book"
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104507219-4ae8e180-559b-11eb-99bf-f0a018c4ae5c.png)
    #     """
    #     if not isinstance(obj, dict) and not isinstance(obj, list):
    #         raise TypeError("Task Objects Must Be A Dictionary or List of Dictionaries.")
    #
    #     if isinstance(obj, dict):
    #         tasks = [obj]
    #     else:
    #         tasks = obj
    #
    #     url = self._client.BASE_URL + 'batch/task'
    #     payload = {
    #         'update': tasks
    #     }
    #     response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
    #     self._client.sync()
    #
    #     if len(tasks) == 1:
    #         return self._client.get_by_id(self._client.parse_id(response), search='tasks')
    #     else:
    #         etag = response['id2etag']
    #         etag2 = list(etag.keys())  # Tag names are out of order
    #         labels = [x['id'] for x in tasks]  # Tag names are in order
    #         items = [''] * len(tasks)  # Create enough spots for the objects
    #         for tag in etag2:
    #             index = labels.index(tag)  # Object of the index is here
    #             found = self._client.get_by_id(labels[index], search='tasks')
    #             items[index] = found  # Place at the correct index
    #         return items

    # @logged_in
    # def complete(self, ids):
    #     """
    #     Marks the task(s) as complete. Supports single task completion and batch task completion.
    #
    #     Arguments:
    #         ids (str or list):
    #             **Single Task (str)**: The ID string of the task.
    #
    #             **Multiple Tasks (list)**: A list of ID strings for the tasks.
    #
    #     Returns:
    #         dict or list:
    #         **Single Task (dict)**: The dictionary of the completed task.
    #
    #         **Multiple Tasks (list)**: A list of dictionaries for the completed tasks.
    #
    #     Raises:
    #         TypeError: If `ids` is not a string or list.
    #         ValueError: If `ids` is not a task that exists.
    #         RuntimeError: If completing was unsuccessful.
    #
    #     !!! example "Task Completing"
    #         === "Single Task Completion"
    #             Pass the ID string of the task to complete.
    #
    #             ```python
    #             # Lets assume that we have a task named "Go To Dentist" that we want to mark as complete.
    #             dentist_task = client.get_by_fields(title='Go To Dentist', search='tasks')
    #             complete_task = client.task.complete(dentist_task['id'])  # Pass the ID of the object
    #             ```
    #
    #             ??? success "Result"
    #                 The task is completed and the dictionary object returned.
    #
    #                 ```python
    #                 {'id': '5fff5009b04b355792c79397', 'projectId': 'inbox115781412', 'sortOrder': -99230924406784,
    #                 'title': 'Go To Dentist', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
    #                 'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles', 'isFloating': False,
    #                 'isAllDay': True, 'reminders': [], 'exDate': [], 'priority': 0, 'status': 2, 'items': [],
    #                 'progress': 0, 'modifiedTime': '2021-01-13T19:56:11.000+0000', 'etag': 'djiiqso6', 'deleted': 0,
    #                 'createdTime': '2021-01-13T19:54:49.000+0000', 'creator': 6147345572, 'kind': 'TEXT'}
    #                 ```
    #
    #                 **Before**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104503673-39510b00-5596-11eb-88df-88eeee9ab4b0.png)
    #
    #                 **After**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104504069-c4ca9c00-5596-11eb-96c9-5698e19989ea.png)
    #
    #         === "Multiple Tasks Completion"
    #             Pass a list of ID strings to complete the tasks.
    #
    #             ```python
    #             # Lets assume that we have a task named "Go To Dentist" and a task named "Go To Store"
    #             dentist_task = client.get_by_fields(title='Go To Dentist', search='tasks')
    #             store_task = client.get_by_fields(title='Go To Store', search='tasks')
    #             ids = [dentist_task['id'], store_task['id']]
    #             completed_tasks = client.task.complete(ids)
    #             ```
    #
    #             ??? success "Result"
    #                 The tasks are completed and the dictionary objects returned in a list.
    #
    #                 ```python
    #                 [{'id': '5fff5009b04b355792c79397', 'projectId': 'inbox115781412', 'sortOrder': -99230924406784,
    #                 'title': 'Go To Dentist', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
    #                 'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles',
    #                 'isFloating': False, 'isAllDay': True, 'reminders': [], 'exDate': [],
    #                 'completedTime': '2021-01-13T19:57:00.285+0000', 'completedUserId': 115781412,
    #                 'priority': 0, 'status': 2, 'items': [], 'progress': 0,
    #                 'modifiedTime': '2021-01-13T19:56:11.000+0000', 'etag': 'qq9drp8d', 'deleted': 0,
    #                 'createdTime': '2021-01-13T19:54:49.000+0000', 'creator': 215414317, 'kind': 'TEXT'},
    #
    #                 {'id': '5fff51f3b04b355792c793e6', 'projectId': 'inbox115781412', 'sortOrder': -100330436034560,
    #                 'title': 'Go To Store', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
    #                 'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles',
    #                 'isFloating': False, 'isAllDay': True, 'reminders': [], 'exDate': [],
    #                 'priority': 0, 'status': 2, 'items': [], 'progress': 0,
    #                 'modifiedTime': '2021-01-13T20:02:59.000+0000', 'etag': 'be8m3g3x',
    #                 'deleted': 0, 'createdTime': '2021-01-13T20:02:59.000+0000', 'creator': 215414317,
    #                 'tags': [], 'kind': 'TEXT'}]
    #                 ```
    #
    #                 **Before**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104504451-4f130000-5597-11eb-9f92-386a6be10ca6.png)
    #
    #                 **After**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104504511-6a7e0b00-5597-11eb-9855-c4edce01713b.png)
    #
    #     """
    #     if not isinstance(ids, str) and not isinstance(ids, list):
    #         raise TypeError("Ids Must Be A String Or List Of Ids")
    #
    #     tasks = []
    #     if isinstance(ids, str):
    #         task = self._client.get_by_fields(id=ids, search='tasks')
    #         if not task:
    #             raise ValueError('The Task Does Not Exist To Mark As Complete')
    #         task['status'] = 2  # Complete
    #         tasks.append(task)
    #     else:
    #         for id in ids:
    #             task = self._client.get_by_fields(id=id, search='tasks')
    #             if not task:
    #                 raise ValueError(f"'Task Id '{id}' Does Not Exist'")
    #             task['status'] = 2  # Complete
    #             tasks.append(task)
    #
    #     url = self._client.BASE_URL + 'batch/task'
    #     payload = {
    #         'update': tasks
    #     }
    #     response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
    #
    #     self._client.sync()
    #     if len(tasks) == 1:
    #         return tasks[0]
    #     else:
    #         return tasks

    # @logged_in
    # def delete(self, ids):
    #     """
    #     Deletes task(s). Supports single task deletion, and batch task deletion.
    #
    #     !!! tip
    #         If a parent task is deleted - the children will remain (unlike normal parent task deletion in `TickTick`)
    #
    #     Arguments:
    #         ids (str or list):
    #             **Single Task (str)**: ID string of the task to be deleted.
    #
    #             **Multiple Tasks (list)**: List of ID strings for the tasks to be deleted.
    #
    #     Returns:
    #         dict or list:
    #         **Single Task (dict)**: Dictionary object of the deleted task.
    #
    #         **Multiple Tasks (list)**: List of dictionary objects for the deleted tasks.
    #
    #     Raises:
    #         TypeError: If `ids` is not a string or list.
    #         ValueError: If `ids` does not exist.
    #         RuntimeError: If the deletion was unsuccessful.
    #
    #     !!! example "Task Deletion"
    #         === "Single Task Deletion"
    #             Pass the ID of the string to be deleted.
    #
    #             ```python
    #             # Lets assume that our task is named "Dentist" and it's in our inbox.
    #             task = client.get_by_fields(title="Dentist", projectId=client.inbox_id, search='tasks')
    #             deleted_task = client.task.delete(task['id'])
    #             ```
    #
    #             ??? success "Result"
    #                 The deleted task object is returned.
    #
    #                 ```python
    #                 {'id': '5ffead3cb04b35082bbced71', 'projectId': 'inbox115781412', 'sortOrder': -2199023255552,
    #                 'title': 'Dentist', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
    #                 'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles',
    #                 'isFloating': False, 'isAllDay': True, 'reminders': [], 'exDate': [], 'priority': 0,
    #                 'status': 0, 'items': [], 'progress': 0, 'modifiedTime': '2021-01-13T08:20:12.000+0000',
    #                 'etag': 'tijkifu0', 'deleted': 0, 'createdTime': '2021-01-13T08:20:12.000+0000',
    #                 'creator': 73561212, 'tags': [], 'kind': 'TEXT'}
    #                 ```
    #
    #                 **Before**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104425305-615c5200-5535-11eb-93fa-3184b5d679b7.png)
    #
    #                 **After**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104425375-76d17c00-5535-11eb-9e12-3af1cf727957.png)
    #
    #         === "Multiple Task Deletion"
    #             Pass a list of ID strings for the tasks to be deleted.
    #
    #             ```python
    #             # Lets assume we have two tasks we want to delete from our inbox - "Dentist" and "Read"
    #             dentist = client.get_by_fields(title="Dentist", projectId=client.inbox_id, search='tasks')
    #             read = client.get_by_fields(title="Read", projectId=client.inbox_id, search='tasks')
    #             id_list = [dentist['id'], read['id']]
    #             deleted_task = client.task.delete(id_list)
    #             ```
    #
    #             ??? success "Result"
    #                 A list of the deleted tasks is returned.
    #
    #                 ```python
    #                 [{'id': '5ffeae528f081003f32cb661', 'projectId': 'inbox115781412', 'sortOrder': -1099511627776,
    #                 'title': 'Dentist', 'content': '', 'timeZone': 'America/Los_Angeles', 'isFloating': False,
    #                 'reminder': '', 'reminders': [], 'priority': 0, 'status': 0, 'items': [],
    #                 'modifiedTime': '2021-01-13T08:24:50.334+0000', 'etag': 'fwsrqx4j', 'deleted': 0,
    #                 'createdTime': '2021-01-13T08:24:50.340+0000', 'creator': 115781412, 'kind': 'TEXT'},
    #
    #                 {'id': '5ffeae528f081003f32cb664', 'projectId': 'inbox115781412', 'sortOrder': -2199023255552,
    #                 'title': 'Read', 'content': '', 'timeZone': 'America/Los_Angeles', 'isFloating': False,
    #                 'reminder': '', 'reminders': [], 'priority': 0, 'status': 0, 'items': [],
    #                 'modifiedTime': '2021-01-13T08:24:50.603+0000', 'etag': '1sje21ao', 'deleted': 0,
    #                 'createdTime': '2021-01-13T08:24:50.609+0000', 'creator': 115781412, 'kind': 'TEXT'}]
    #                 ```
    #                 **Before**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104425633-c4e67f80-5535-11eb-9735-bea3db63e0ab.png)
    #
    #                 **After**
    #
    #                 ![image](https://user-images.githubusercontent.com/56806733/104425375-76d17c00-5535-11eb-9e12-3af1cf727957.png)
    #
    #     """
    #     if not isinstance(ids, str) and not isinstance(ids, list):
    #         raise TypeError('Ids Must Be A String or List Of Strings')
    #     tasks = []
    #     if isinstance(ids, str):
    #         task = self._client.get_by_fields(id=ids, search='tasks')
    #         if not task:
    #             raise ValueError(f"Task '{ids}' Does Not Exist To Delete")
    #         task = {'projectId': task['projectId'], 'taskId': ids}
    #         tasks = [task]
    #
    #     else:
    #         for id in ids:
    #             task = self._client.get_by_fields(id=id, search='tasks')
    #             if not task:
    #                 raise ValueError(f"'Task Id '{id}' Does Not Exist'")
    #             task = {'projectId': task['projectId'], 'taskId': id}
    #             tasks.append(task)
    #
    #     url = self._client.BASE_URL + 'batch/task'
    #     payload = {'delete': tasks}
    #     response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
    #     return_list = []
    #     if len(tasks) == 1:
    #         return_list.append(self._client.get_by_id(ids, search='tasks'))
    #     else:
    #         for item in tasks:
    #             o = self._client.get_by_id(item['taskId'], search='tasks')
    #             return_list.append(o)
    #     self._client.sync()
    #     if len(return_list) == 1:
    #         return return_list[0]
    #     return return_list
    #

    def move(self, obj, new: str):
        """
        Moves task(s) from their current project to the new project. It will move the specified
        tasks with `obj` to the new project.

        !!! important
            If moving multiple tasks, they must all be from the same project.
        Arguments:
            obj (dict or list):
                **Single Task (dict)**: Pass the single task dictionary object to move.

                **Multiple Tasks (list)**: Pass a list of task dictionary objects to move.
            new: The ID string of the project that the task(s) should be moved to.

        Returns:
            dict or list:
            **Single Task (dict)**: Returns the dictionary of the moved task.

            **Multiple Tasks (list)**: Returns a list of dictionaries for the moved tasks.

        Raises:
            TypeError: If `obj` is not a dict or list or if `new` is not a str.
            ValueError: For multiple tasks, if the projects are not all the same.
            ValueError: If the new project does not exist.
            RuntimeError: If the task(s) could not be successfully moved.

        !!! example "Move Examples"
            === "Moving A Single Task"
                Pass in the task object, and the ID of the project the task should be moved to.

                ```python
                # Lets assume that we have a task 'Read' that exists in a project named "Work"
                # Lets move that task to the inbox
                read_task = client.get_by_fields(title='Read', search='tasks')
                move_read_task = client.task.move(read_task, client.inbox_id)
                ```

                ??? success "Result"
                    The dictionary object of the moved task is returned.

                    ```python
                    {'id': '5fffed61b04b355792c799a8', 'projectId': 'inbox115781412', 'sortOrder': 0,
                    'title': 'Read', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
                    'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles',
                    'isFloating': False, 'isAllDay': True, 'reminders': [], 'exDate': [], 'priority': 0,
                    'status': 0, 'items': [], 'progress': 0, 'modifiedTime': '2021-01-14T07:08:15.875+0000',
                    'etag': 'twrmcr55', 'deleted': 0, 'createdTime': '2021-01-14T07:06:09.000+0000',
                    'creator': 47593756, 'tags': [], 'kind': 'TEXT'}
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104556170-f1f96780-55f3-11eb-9a35-aecc3beea105.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104556336-46044c00-55f4-11eb-98c1-4cffcf4bd006.png)

            === "Moving Multiple Tasks"
                Pass in the task objects in a list, and the ID of the project that tasks should be moved to.
                Again, the tasks in the list should all be from the same project.

                ```python
                # Lets move two tasks: 'Read' and 'Write' that exist in a project named "Work"
                # Lets move the tasks to another project named "Hobbies" that already exists.
                hobbies_project = client.get_by_fields(name='Hobbies', search='projects')
                hobbies_id = hobbies_project['id']  # Id of the hobbies project
                read_task = client.get_by_fields(title='Read', search='tasks')
                write_task = client.get_by_fields(title='Write', search='tasks')
                move_tasks = client.task.move([read_task, write_task], hobbies_id)  # Task objects in a list
                ```

                ??? success "Result"
                    The tasks that were moved are returned in a list.

                    ```python
                    [{'id': '5ffff003b04b355792c799d3', 'projectId': '5fffeff68f08654c982c141a', 'sortOrder': 0,
                    'title': 'Read', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
                    'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles',
                    'isFloating': False, 'isAllDay': True, 'reminders': [], 'exDate': [], 'priority': 0,
                    'status': 0, 'items': [], 'progress': 0, 'modifiedTime': '2021-01-14T07:19:28.595+0000',
                    'etag': 'co8jfqyn', 'deleted': 0, 'createdTime': '2021-01-14T07:17:23.000+0000',
                    'creator': 768495743, 'kind': 'TEXT'},

                    {'id': '5ffff004b04b355792c799d4', 'projectId': '5fffeff68f08654c982c141a', 'sortOrder': 0,
                    'title': 'Write', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
                    'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles',
                    'isFloating': False, 'isAllDay': True, 'reminders': [], 'exDate': [], 'priority': 0,
                    'status': 0, 'items': [], 'progress': 0, 'modifiedTime': '2021-01-14T07:19:28.596+0000',
                    'etag': '5unkf7xg', 'deleted': 0, 'createdTime': '2021-01-14T07:17:24.000+0000',
                    'creator': 768495743, 'tags': [], 'kind': 'TEXT'}]
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104557103-857f6800-55f5-11eb-8b92-cf51bc159745.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104557388-063e6400-55f6-11eb-8ba4-aa64f3f739bd.png)

    """
        # Type errors
        if not isinstance(obj, dict) and not isinstance(obj, list):
            raise TypeError('obj should be a dict or list of dicts')
        if not isinstance(new, str):
            raise TypeError('new should be a string')

        # Get the parent project
        if new != self._client.inbox_id:
            project = self._client.get_by_id(new, search='projects')
            if not project:
                raise ValueError('The ID for the new project does not exist')

        if isinstance(obj, dict):
            obj = [obj]

        # Go through and check that the projects are all the same
        move_tasks = []
        project_id = obj[0]['projectId']
        for task in obj:
            if task['projectId'] != project_id:
                raise ValueError('All the tasks must come from the same project')
            else:
                move_tasks.append({
                    'fromProjectId': project_id,
                    'taskId': task['id'],
                    'toProjectId': new
                })

        url = self._client.BASE_URL + 'batch/taskProject'
        self._client.http_post(url, json=move_tasks, cookies=self._client.cookies)
        self._client.sync()
        # Return the tasks in the new list
        ids = [x['id'] for x in obj]
        return_list = []
        for i in ids:
            return_list.append(self._client.get_by_id(i))
        if len(return_list) == 1:
            return return_list[0]
        else:
            return return_list

    @logged_in
    def move_all(self, old: str, new: str) -> list:
        """
        Moves all the tasks from the old project to the new project.

        Arguments:
            old: ID of the old project.
            new: ID of the new project.

        Returns:
            The tasks contained in the new project.

        Raises:
            ValueError: If either the old or new projects do not exist.
            RuntimeError: If the movement was unsuccessful.

        !!! example
            Lets assume that we have a project named "School", and another project named "Work". To move all the tasks from "School" to "Work":

            ```python
            # Get the projects
            school_project = client.get_by_fields(name='School', search='projects')
            work_project = client.get_by_fields(name='Work', search='projects')
            # Call the method
            moved_tasks = client.task.move_projects(school_project['id'], work_project['id'])
            ```

            ??? success "Result"
                The tasks that were moved are returned.

                ```python
                [{'id': '5ffea9afe4b062d60dd62aef', 'projectId': '5ffea9afe4b062d60dd62aea', 'sortOrder': 0,
                'title': 'Finish documentation for project', 'content': '', 'timeZone': 'America/Los_Angeles',
                'isFloating': False, 'reminder': '', 'reminders': [], 'priority': 0, 'status': 0, 'items': [],
                'modifiedTime': '2021-01-13T08:06:31.407+0000', 'etag': 'ogclghmd', 'deleted': 0,
                'createdTime': '2021-01-13T08:05:03.901+0000', 'creator': 447666584, 'kind': 'TEXT'},

                {'id': '5ffea9b0e4b062d60dd62af4', 'projectId': '5ffea9afe4b062d60dd62aea', 'sortOrder': 0,
                'title': 'Call the boss man', 'content': '', 'timeZone': 'America/Los_Angeles',
                'isFloating': False, 'reminder': '', 'reminders': [], 'priority': 0, 'status': 0, 'items': [],
                'modifiedTime': '2021-01-13T08:06:31.409+0000', 'etag': '65c73q8i', 'deleted': 0,
                'createdTime': '2021-01-13T08:05:04.117+0000', 'creator': 447666584, 'kind': 'TEXT'}]
                ```

                **Before**: Two tasks are contained in the "School" project

                ![image](https://user-images.githubusercontent.com/56806733/104423574-1e997a80-5533-11eb-9417-34c31e603d21.png)

                **After**: The two tasks are moved to the 'Work' project

                ![image](https://user-images.githubusercontent.com/56806733/104423710-4a1c6500-5533-11eb-90f3-2c3d024280af.png)
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
            return tasks  # No tasks to move so just return the empty list
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

    def get_from_project(self, project: str):
        """
        Obtains the tasks that are contained in the project.

        Arguments:
            project: ID string of the project to get the tasks from.

        Returns:
            dict or list:
            **Single Task In Project (dict)**: The single task object dictionary.

            **Multiple Tasks In Project (list)**: A list of task object dictionaries.

            **No Tasks Found (list)**: Empty list.

        Raises:
            ValueError: If the project ID does not exist.

        !!! example "Getting Uncompleted Tasks From The Inbox"
            ```python
            tasks = client.task.get_from_project(client.inbox_id)
            ```

            ??? success "Result"
                See `Returns` for the different return values based on the amount of tasks present
                in the project.

                ```python
                [{'id': '5ffe93efb04b35082bbce7af', 'projectId': 'inbox115781412', 'sortOrder': 2199023255552, 'title': 'Go To Library',
                'content': '', 'startDate': '2021-01-12T08:00:00.000+0000', 'dueDate': '2021-01-12T08:00:00.000+0000',
                'timeZone': 'America/Los_Angeles', 'isFloating': False, 'isAllDay': True,
                'reminders': [], 'exDate': [], 'priority': 0, 'status': 0, 'items': [], 'progress': 0,
                'modifiedTime': '2021-01-13T06:32:15.000+0000', 'etag': 'kkh0w1jk', 'deleted': 0,
                'createdTime': '2021-01-13T06:32:15.000+0000', 'creator': 447666584, 'tags': [],
                'kind': 'TEXT'},

                {'id': '5ffe93f3b04b35082bbce7b0', 'projectId': 'inbox115781412', 'sortOrder': 1099511627776, 'title': 'Deposit Funds',
                'content': '', 'startDate': '2021-01-12T08:00:00.000+0000', 'dueDate': '2021-01-12T08:00:00.000+0000',
                'timeZone': 'America/Los_Angeles', 'isFloating': False, 'isAllDay': True,
                'reminders': [], 'exDate': [], 'priority': 0, 'status': 0, 'items': [], 'progress': 0, 'modifiedTime': '2021-01-13T06:32:19.000+0000',
                'etag': 'w4hj21wf', 'deleted': 0, 'createdTime': '2021-01-13T06:32:19.000+0000', 'creator': 447666584, 'tags': [],
                'kind': 'TEXT'}]
                ```

                ![image](https://user-images.githubusercontent.com/56806733/104415494-f86ddd80-5526-11eb-8b84-75bf3886ba46.png)
        """
        # Make sure the project exists
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
    def get_completed(self, start, end=None, full: bool = True, tz: str = None) -> list:
        """
        Obtains all completed tasks from the given start date and end date.

        !!! note
            There is a limit of 100 items for the request

        Arguments:
            start (datetime): Start time datetime object.
            end (datetime): End time datetime object.
            full: Boolean specifying whether hours, minutes, and seconds are to be taken into account for the query.
            tz: String specifying a specific time zone, however this will default to your accounts normal time zone.

        Returns:
            A list containing all the completed tasks based on the times.

        Raises:
            TypeError: If the proper types are not used.
            ValueError: If start occurs after end.
            KeyError: If the time zone string passed is not a valid time zone string.
            RuntimeError: If getting the tasks is unsuccessful.

        !!! example "Getting Completed Tasks"
            === "Completed Tasks In A Single Day"
                Getting the tasks for a full, complete day requires passing in
                the datetime object corresponding to the day that you want.

                ```python
                # Get the tasks for 1/11/2021
                tasks = client.task.get_completed(datetime(2021, 1, 11))
                ```

                ??? success "Result"
                    The list of completed tasks is returned.

                    ```python
                    [{'id': '5ffca35f4c201114702a0607', 'projectId': '004847faa60015487be444cb',
                    'sortOrder': -50027779063826, 'title': 'Shoulders and Arms', 'content': '', 'desc': '',
                    'startDate': '2021-01-11T08:00:00.000+0000', 'dueDate': '2021-01-11T08:00:00.000+0000',
                    'timeZone': 'America/Los_Angeles', 'isFloating': False, 'isAllDay': True, 'reminders': [],
                    'repeatFlag': '', 'exDate': [], 'completedTime': '2021-01-11T23:25:46.000+0000',
                    'completedUserId': 185769383, 'priority': 0, 'status': 2, 'items': [], 'progress': 0,
                    'modifiedTime': '2021-01-11T23:25:41.000+0000', 'etag': '6hlk4e8t', 'deleted': 0,
                    'createdTime': '2021-01-11T19:13:35.000+0000', 'creator': 185769383, 'tags': ['fitness'],
                    'commentCount': 0, 'pomodoroSummaries': [{'userId': 185769383, 'count': 0, 'estimatedPomo': 0,
                    'duration': 0}], 'focusSummaries': [{'userId': 185769383, 'pomoCount': 0, 'estimatedPomo': 0,
                    'estimatedDuration': 0, 'pomoDuration': 0, 'stopwatchDuration': 3720}], 'kind': 'TEXT'}]
                    ```

                    ![image](https://user-images.githubusercontent.com/56806733/104562952-e1e68580-55fd-11eb-9e09-f432caa8616b.png)

            === "Completed Tasks Over A Range Of Days"
                Getting the tasks for a range of days requires passing in datetime objects
                for the start day, and the end day that you want.

                ```python
                # Get the tasks between 8/7/18 and 8/10/18
                start = datetime(2018, 8, 7)
                end = datetime(2018, 8, 10)
                tasks = client.task.get_completed(start, end)
                ```

                ??? success "Result"
                    Completed tasks in a list are returned.

                    ```python
                    [{'id': '5ffffebab04b355792c79e38', 'projectId': 'inbox115781412', 'sortOrder': -7696581394432,
                    'title': 'Ride Bike', 'content': '', 'startDate': '2021-01-14T08:00:00.000+0000',
                    'dueDate': '2021-01-14T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles',
                    'isFloating': False, 'isAllDay': True, 'reminders': [], 'exDate': [],
                    'completedTime': '2018-08-09T07:20:11.000+0000', 'completedUserId': 185769383,
                    'priority': 0, 'status': 2, 'items': [], 'progress': 0,
                    'modifiedTime': '2021-01-14T08:21:01.000+0000', 'etag': 'mhjyig4y',
                    'deleted': 0, 'createdTime': '2021-01-14T08:20:10.000+0000', 'creator': 185769383, 'kind': 'TEXT'},

                    {'id': '5ffffeaab04b355792c79d89', 'projectId': 'inbox115781412',
                    'sortOrder': -6597069766656, 'title': 'Read Book', 'content': '',
                    'startDate': '2021-01-14T08:00:00.000+0000', 'dueDate': '2021-01-14T08:00:00.000+0000',
                    'timeZone': 'America/Los_Angeles', 'isFloating': False, 'isAllDay': True, 'reminders': [],
                    'exDate': [], 'completedTime': '2018-08-08T07:20:12.000+0000', 'completedUserId': 185769383,
                    'priority': 0, 'status': 2, 'items': [], 'progress': 0,
                    'modifiedTime': '2021-01-14T08:20:46.000+0000', 'etag': 'tzd4coms', 'deleted': 0,
                    'createdTime': '2021-01-14T08:19:54.000+0000', 'creator': 185769383, 'kind': 'TEXT'}]
                    ```

                    ![image](https://user-images.githubusercontent.com/56806733/104563478-8c5ea880-55fe-11eb-9bcf-91bc44c02083.png)

            === "Completed Tasks Over A Specific Duration Of Time"
                You can also get completed tasks that were completed in a specific time duration.
                Include specific hours, minutes, and seconds for the datetime objects, and
                specify `full` to be false -> meaning that the specific times will be put into effect.

                ```python
                # Get the tasks completed between 12PM and 5PM on 12/15/2020
                start = datetime(2020, 12, 15, 12)  # 12PM 12/15/2020
                end = datetime(2020, 12, 15, 17)    # 5PM 12/15/2020
                tasks = client.task.get_completed(start, end, full=False)
                ```
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

    def time_conversions(self, start_date: datetime = None, end_date: datetime = None, time_zone: str = None):
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
            if not isinstance(end_date, datetime.datetime):
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
            start_date = convert_date_to_tick_tick_format(start_date, time_zone)
            end_date = convert_date_to_tick_tick_format(end_date, time_zone)

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
            start_date = convert_date_to_tick_tick_format(start_date, time_zone)
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
            end_date = convert_date_to_tick_tick_format(end_date, time_zone)
            start_date = end_date

        return {'startDate': start_date, 'dueDate': end_date, 'isAllDay': all_day, 'timeZone': time_zone}

    # def _task_field_checks(self,
    #                        start_date: datetime = None,
    #                        end_date: datetime = None,
    #                        time_zone: str = None,
    #                        task_name: str = None,
    #                        priority: str = 'none',
    #                        project: str = None,
    #                        tags: list = None,
    #                        content: str = '',
    #                        ):
    #     """
    #     Performs error checks on the remaining task fields.
    #     :param task_name:
    #     :param priority:
    #     :param project:
    #     :param tags:
    #     :param content:
    #     :return:
    #     """
    #     dates = self.time_conversions(start_date=start_date, end_date=end_date, time_zone=time_zone)
    #     # task_name: -> Make sure task_name is a string
    #     if not isinstance(task_name, str):
    #         raise TypeError(f"Invalid Task Name {task_name} -> Task Name Must Be A String")
    #
    #     # priority: -> Make sure it is a string
    #     if not isinstance(priority, str):
    #         raise TypeError(f"Priority must be 'none', 'low', 'medium', or 'high'")
    #
    #     # Lower case the input and make sure it is one of the four options
    #     lower = priority.lower()
    #     if lower not in self.PRIORITY_DICTIONARY:
    #         raise TypeError(f"Priority must be 'none', 'low', 'medium', or 'high'")
    #
    #     # Priority is now an integer value
    #     priority = self.PRIORITY_DICTIONARY[lower]
    #
    #     # project_id -> Default project id will be none
    #     if project is None or project == self._client.inbox_id:
    #         project = self._client.inbox_id
    #     else:
    #         project_obj = self._client.get_by_id(project, search='projects')
    #         if not project_obj:
    #             raise ValueError(f"List id '{project}' Does Not Exist")
    #
    #     # Tag list does not matter -> The user can enter any tag names they want in the list
    #     if tags is None:
    #         tags = []
    #     else:
    #         # Check if its a string
    #         if isinstance(tags, str):
    #             tags = [tags]
    #         elif isinstance(tags, list):
    #             for item in tags:
    #                 if not isinstance(item, str):
    #                     raise ValueError(f"Individual Tags Inside List Must Be In String Format")
    #         else:
    #             raise ValueError(f"Tags Must Be Passed A Single String, Or As A List Of Strings For Multiple Tags")
    #
    #     # Content can be whatever string that the user wants to pass but make sure its a string
    #     if not isinstance(content, str):
    #         raise ValueError(f"Content Must Be A String")
    #
    #     fields = {'title': task_name, 'priority': priority, 'projectId': project, 'tags': tags, 'content': content}
    #
    #     return {**dates, **fields}  # Merge the dictionaries

    @staticmethod
    def builder(title: str = '',
                content: str = None,
                desc: str = None,
                allDay: bool = None,
                startDate: datetime = None,
                dueDate: datetime = None,
                timeZone: str = None,
                reminders: list = None,
                repeat: str = None,
                priority: int = None,
                sortOrder: int = None,
                items: list = None):
        """
        Builds a task dictionary with the passed fields. This is a helper
        method for task creation.
        """

        task = {'title': title}
        if content is not None:
            task['content'] = content
        if desc is not None:
            task['desc'] = desc
        if allDay is not None:
            task['allDay'] = allDay
        if startDate is not None:
            task['startDate'] = startDate
        if dueDate is not None:
            task['dueDate'] = dueDate
        if timeZone is not None:
            task['timeZone'] = timeZone
        if reminders is not None:
            task['reminders'] = reminders
        if repeat is not None:
            task['repeat'] = repeat
        if priority is not None:
            task['priority'] = priority
        if sortOrder is not None:
            task['sortOrder'] = sortOrder
        if items is not None:
            task['items'] = items

        return task

    # @logged_in
    # def builder(self,
    #             name: str,
    #             start=None,
    #             end=None,
    #             priority: str = 'none',
    #             project: str = None,
    #             tags: list = None,
    #             content: str = '',
    #             tz: str = None
    #             ) -> dict:
    #     """
    #     Builds a local task object with the passed fields. Performs proper error checking. This function serves as a helper
    #     for batch creating tasks in [`create`][managers.tasks.TaskManager.create].
    #
    #     Arguments:
    #         name: Any string is valid.
    #         start (datetime): Desired start time.
    #         end (datetime): Desired end time.
    #         priority: For a priority other than 'none': 'low', 'medium', 'high'.
    #         project: The id of the list (project) you want the task to be created in. The default will be your inbox.
    #         tags: Single string for the label of the tag, or a list of strings of labels for many tags.
    #         content: Desired text to go into the 'Description' field in the task.
    #         tz: Timezone string if you want to make your task for a timezone other than the timezone linked to your TickTick account.
    #
    #     Returns:
    #         A dictionary containing the proper fields needed for task creation.
    #
    #     Raises:
    #         TypeError: If any of the parameter types do not match as specified in the parameters table.
    #
    #     !!! example
    #         ```python
    #             start_time = datetime(2022, 7, 5, 14, 30)  # 7/5/2022 at 2:30 PM
    #             end_time = datetime(2022, 7, 5, 23, 30)  # 7/5/2022 at 11:30 PM
    #             title = "Molly's Birthday"
    #             remember = "Be there at two and don't forget the snacks"
    #             tag = ['Party', 'Friends', 'Food']
    #             task = client.task.builder(title,
    #                                       start=start_time,
    #                                       end=end_time,
    #                                       priority='medium',
    #                                       content=remember,
    #                                       tags=tag)
    #         ```
    #
    #         ??? success "Result"
    #             A dictionary object containing the appropriate fields is returned.
    #
    #             ```python
    #             {'startDate': '2022-07-05T21:30:00+0000', 'dueDate': '2022-07-06T06:30:00+0000', 'isAllDay': False, 'timeZone': 'America/Los_Angeles',
    #             'title': "Molly's Birthday", 'priority': 3, 'projectId': 'inbox115781412', 'tags': ['Party', 'Friends', 'Food'],
    #             'content': "Be there at two and don't forget the snacks"}
    #             ```
    #
    #     """
    #
    #     return self._task_field_checks(task_name=name,
    #                                    priority=priority,
    #                                    project=project,
    #                                    tags=tags,
    #                                    content=content,
    #                                    start_date=start,
    #                                    end_date=end,
    #                                    time_zone=tz)
