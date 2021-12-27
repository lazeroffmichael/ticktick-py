import datetime
import pytz

from ticktick.helpers.time_methods import convert_local_time_to_utc, convert_date_to_tick_tick_format
from ticktick.helpers.constants import DATE_FORMAT
from calendar import monthrange


class TaskManager:
    """
    Handles all interactions for tasks.
    """

    TASK_CREATE_ENDPOINT = "/open/v1/task"

    def __init__(self, client_class):
        # ._client is a reference to the original client_class
        self._client = client_class

        # declare access token
        self.oauth_access_token = ''

        # set access token to valid oauth access token if available
        if self._client.oauth_manager.access_token_info is not None:
            self.oauth_access_token = self._client.oauth_manager.access_token_info['access_token']

        # oauth headers have some extra fields
        self.oauth_headers = {'Content-Type': 'application/json',
                              'Authorization': 'Bearer {}'.format(self.oauth_access_token),
                              'User-Agent': self._client.USER_AGENT}

        self.headers = self._client.HEADERS

    def _generate_create_url(self):
        """
        Returns the endpoint url for task creation
        """

        CREATE_ENDPOINT = "/open/v1/task"
        return self._client.OPEN_API_BASE_URL + CREATE_ENDPOINT

    def create(self, task):
        """
        Create a task. Use [`builder`][managers.tasks.TaskManager.builder] for easy task dictionary
        creation.

        !!! warning
            Creating tasks with tags is not functional but will be implemented in a future update.

        Arguments:
            task (dict): Task dictionary to be created.

        Returns:
            dict: Dictionary of created task object. Note that the task object is a "simplified" version of the full
            task object. Use [`get_by_id`][api.TickTickClient.get_by_id] for the full task object.

        !!! example "Creating Tasks"
            === "Just A Name"
                ```python
                title = "Molly's Birthday"
                task = client.task.builder(title)   # Local dictionary
                molly = client.task.create(task)    # Create task remotely
                ```

                ??? success "Result"

                    ```python
                    {'id': '60ca9dbc8f08516d9dd56324',
                     'projectId': 'inbox115781412',
                     'title': "Molly's Birthday",
                     'timeZone': '',
                     'reminders': [],
                     'priority': 0,
                     'status': 0,
                     'sortOrder': -1336456383561728,
                     'items': []}
                    ```
                    ![image](https://user-images.githubusercontent.com/56806733/122314079-5898ef00-cecc-11eb-8614-72b070b306c6.png)

            === "Dates and Descriptions"
                ```python
                title = "Molly's Birthday Party"

                start_time = datetime(2027, 7, 5, 14, 30)  # 7/5/2027 @ 2:30PM
                end_time = datetime(2027, 7, 5, 19, 30)    # 7/5/2027 @ 7:30PM

                content = "Bring Cake"

                task = client.task.builder(title,
                                           startDate=start_time,
                                           dueDate=end_time,
                                           content=content)

                mollys_party = client.task.create(task)
                ```

                ??? success "Result"
                    ```python
                    {'id': '60ca9fe58f08fe31011862f2',
                     'projectId': 'inbox115781412',
                     'title': "Molly's Birthday Party",
                     'content': 'Bring Cake',
                     'timeZone': '',
                     'startDate': '2027-07-05T21:30:00.000+0000',
                     'dueDate': '2027-07-06T02:30:00.000+0000',
                     'priority': 0,
                     'status': 0,
                     'sortOrder': -1337555895189504,
                     'items': [],
                     'allDay': False}
                    ```
                    ![image](https://user-images.githubusercontent.com/56806733/122314760-a4986380-cecd-11eb-88af-9562d352470f.png)

            === "Different Project"
                ```python
                # Get the project object
                events = client.get_by_fields(name="Events", search='projects')

                events_id = events['id']    # Need the project object id

                title = "Molly's Birthday"

                task = client.task.builder(title, projectId=events_id)

                mollys_birthday = client.task.create(task)
                ```

                ??? success "Result"
                    ```python
                    {'id': '60caa2278f08fe3101187002',
                     'projectId': '60caa20d8f08fe3101186f74',
                     'title': "Molly's Birthday",
                     'timeZone': '',
                     'reminders': [],
                     'priority': 0,
                     'status': 0,
                     'sortOrder': -1099511627776,
                     'items': []}
                    ```
                    ![image](https://user-images.githubusercontent.com/56806733/122315454-eece1480-cece-11eb-8394-94a2aec1ba70.png)
        """

        # generate url
        url = self._generate_create_url()

        # make request
        response = self._client.http_post(url=url, json=task, headers=self.oauth_headers)

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

        To update a task, change any field in it's dictionary directly then pass to the method.

        !!! warning
            Creating tasks with tags is not functional but will be implemented in a future update.

        Arguments:
            task (dict): Task dictionary to be updated

        Returns:
            dict: The updated task dictionary object

        !!! tip "Formatting Dates Help"
            TickTick uses a certain syntax for their dates. To convert a datetime object to a compatible
            string to be used for updating dates, see [convert_date_to_tick_tick_format][helpers.time_methods.convert_date_to_tick_tick_format]

        !!! example "Changing The Date"

            ```python
            # Get the task
            mollys_birthday = client.get_by_fields(title="Molly's Birthday", search="tasks")

            # New Date
            new_date = datetime(2027, 5, 6)

            # Get the new date string
            new_date_string = convert_date_to_tick_tick_format(new_date, tz=client.time_zone)

            # Update the task dictionary
            mollys_birthday['startDate'] = new_date_string

            # Update the task
            molly_updated = client.task.update(mollys_birthday)
            ```

            **Original Task**
            ![image](https://user-images.githubusercontent.com/56806733/122316205-49b43b80-ced0-11eb-8d14-61fa5bb5b10a.png)

            ??? success "Result"
                ```python
                {'id': '60caa2278f08fe3101187002',
                'projectId': '60caa20d8f08fe3101186f74',
                'title': "Molly's Birthday",
                'content': '',
                'timeZone': '',
                'startDate': '2027-05-06T07:00:00.000+0000',
                'dueDate': '2027-05-05T07:00:00.000+0000',
                'reminders': [],
                'priority': 0,
                'status': 0,
                'sortOrder': -1099511627776,
                'items': [],
                'allDay': True}
                ```
                ![image](https://user-images.githubusercontent.com/56806733/122316408-ad3e6900-ced0-11eb-89f9-6d980b5cc954.png)
        """

        # TODO: Make tags work

        # generate url
        url = self._generate_update_url(task['id'])

        # make request
        response = self._client.http_post(url=url, json=task, headers=self.oauth_headers)

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

    def complete(self, task: dict):
        """
        Marks a task as complete. Pass in the task dictionary to be marked as completed.

        !!! note
            The task should already be created

        Arguments:
            task (dict): The task dictionary object.

        Returns:
            dict: The original passed in task.

        !!! example "Task Completing"
            ```python
            # Lets assume that we have a task named "Dentist" that we want to mark as complete.

            dentist_task = client.get_by_fields(title='Dentist', search='tasks')
            complete_task = client.task.complete(dentist_task)  # Pass the task dictionary
            ```

            ??? success "Result"
                The task is completed and the dictionary object returned.

                ```python
                {'id': '5fff5009b04b355792c79397', 'projectId': 'inbox115781412', 'sortOrder': -99230924406784,
                'title': 'Go To Dentist', 'content': '', 'startDate': '2021-01-13T08:00:00.000+0000',
                'dueDate': '2021-01-13T08:00:00.000+0000', 'timeZone': 'America/Los_Angeles', 'isFloating': False,
                'isAllDay': True, 'reminders': [], 'exDate': [], 'priority': 0, 'status': 2, 'items': [],
                'progress': 0, 'modifiedTime': '2021-01-13T19:56:11.000+0000', 'etag': 'djiiqso6', 'deleted': 0,
                'createdTime': '2021-01-13T19:54:49.000+0000', 'creator': 6147345572, 'kind': 'TEXT'}
                ```

                **Before**

                ![image](https://user-images.githubusercontent.com/56806733/104503673-39510b00-5596-11eb-88df-88eeee9ab4b0.png)

                **After**

                ![image](https://user-images.githubusercontent.com/56806733/104504069-c4ca9c00-5596-11eb-96c9-5698e19989ea.png)
        """

        # generate url
        url = self._generate_mark_complete_url(task['projectId'], task['id'])

        # make request
        response = self._client.http_post(url=url, json=task, headers=self.oauth_headers)

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

        Arguments:
             task (str or list):
                 **Single Task (dict)**: Task dictionary to be deleted

                 **Multiple Tasks (list)**: List of task dictionaries to be deleted

        Returns:
             dict or list:
                **Single Task (dict)**: Task dictionary that was deleted

                **Multiple Tasks (list)**: List of task dictionaries that were deleted

        !!! example "Task Deletion"

            === "Single Task Deletion"

                ```python
                # Get the task
                task = client.get_by_fields(title="Molly's Birthday", search="tasks")

                # Delete the task
                deleted = client.task.delete(task)
                ```

                ??? success "Result"
                    ``` python
                    {'id': '60caa2278f08fe3101187002',
                    'projectId': '60caa20d8f08fe3101186f74',
                    'sortOrder': -1099511627776,
                    'title': "Molly's Birthday",
                    'content': '',
                    'startDate': '2027-05-06T07:00:00.000+0000',
                    'dueDate': '2027-05-06T07:00:00.000+0000',
                    'timeZone': '',
                    'isFloating': False,
                    'isAllDay': True,
                    'reminders': [],
                    'repeatFirstDate': '2027-05-05T07:00:00.000+0000',
                    'exDate': [],
                    'priority': 0,
                    'status': 0,
                    'items': [],
                    'progress': 0,
                    'modifiedTime': '2021-06-17T01:25:19.000+0000',
                    'etag': 'rrn4paqp',
                    'deleted': 0,
                    'createdTime': '2021-06-17T01:15:19.365+0000',
                    'creator': 119784412,
                    'kind': 'TEXT'}
                    ```

            === "Multiple Task Deletion"
                ``` python
                # Get the tasks
                wash_car = client.get_by_fields(title="Wash Car", search="tasks")
                do_dishes = client.get_by_fields(title="Do Dishes", search="tasks")

                # Make a list for the tasks
                to_delete = [wash_car, do_dishes]

                # Delete the tasks
                deleted = client.task.delete(to_delete)
                ```

                **Before**

                ![image](https://user-images.githubusercontent.com/56806733/122317746-e11a8e00-ced2-11eb-8449-519615de5935.png)


                ??? success "Result"
                    ```python
                    [{'id': '60caa8e714f7103cef35765a', 'projectId': '60caa20d8f08fe3101186f74',
                    'sortOrder': -1099511627776, 'title': 'Wash Car', 'content': '',
                    'timeZone': 'America/Los_Angeles', 'isFloating': False,
                    'reminder': '', 'reminders': [], 'exDate': [], 'priority': 0, 'status': 0,
                    'items': [], 'progress': 0, 'modifiedTime': '2021-06-17T01:44:07.000+0000', 'etag': '8372m61k',
                    'deleted': 0, 'createdTime': '2021-06-17T01:44:07.000+0000',
                    'creator': 115761422, 'tags': [], 'kind': 'TEXT'},

                    {'id': '60caa8ea14f7103cef35765f', 'projectId': '60caa20d8f08fe3101186f74',
                    'sortOrder': -2199023255552, 'title': 'Do Dishes', 'content': '',
                    'timeZone': 'America/Los_Angeles', 'isFloating': False, 'reminder': '',
                    'reminders': [], 'exDate': [], 'priority': 0, 'status': 0, 'items': [],
                    'progress': 0, 'modifiedTime': '2021-06-17T01:44:10.000+0000',
                    'etag': 'sfka0mvn', 'deleted': 0, 'createdTime': '2021-06-17T01:44:10.000+0000',
                    'creator': 1155481312, 'tags': [], 'kind': 'TEXT'}]
                    ```
                    ![image](https://user-images.githubusercontent.com/56806733/122317923-2212a280-ced3-11eb-8a6b-8a32fa8426ce.png)


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
        self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)

        # sync local state
        self._client.sync()

        # return input
        return task

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
        response = self._client.http_post(url, json=subtasks, cookies=self._client.cookies, headers=self.headers)
        self._client.sync()
        # Find and return the updated child objects
        subtasks = []
        for task_id in ids:
            subtasks.append(self._client.get_by_id(task_id, search='tasks'))
        if len(subtasks) == 1:
            return subtasks[0]  # Return just the dictionary object if its a single task
        else:
            return subtasks

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
        self._client.http_post(url, json=move_tasks, cookies=self._client.cookies, headers=self.headers)
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
            moved_tasks = client.task.move_all(school_project['id'], work_project['id'])
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
        # Make the initial call to move the tasks
        self._client.http_post(url, json=task_project, cookies=self._client.cookies, headers=self.headers)

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
        response = self._client.http_get(url, params=parameters, cookies=self._client.cookies, headers=self.headers)
        return response

    def dates(self, start, due=None, tz=None):
        """
        Performs necessary date conversions from datetime objects to strings. This
        method allows for more natural input of data to the [`builder`][managers.tasks.TaskManager.builder]
        method.

        Arguments:
            start (datetime): Desired start time
            due (datetime): Desired end time
            tz (str): Time zone string if the desired time zone is not the account default.

        Returns:
            dict: Contains 'startDate', 'endDate', 'timeZone', and 'allDay' when applicable.


        1. All Day Start Time (single day task)
        2. All Day Start and End Time (multi-day range)
        3. Specific Start Time (specific time task)
        4. Specific Start and End Time (specific start and end task)

        !!! example "Last Day Of The Month"
            ```python
            start = datetime(2027, 3, 27)
            end = datetime(2027, 3, 31)

            dates = client.task.dates(start, end)
            ```

            ??? success "Result"
                ```
                {'startDate': '2027-03-27T07:00:00+0000',
                'dueDate': '2027-04-01T07:00:00+0000',
                'allDay': True}
                ```
        """
        dates = {}
        # Set time zone
        if tz is not None:
            dates['timeZone'] = tz
        else:
            tz = self._client.time_zone

        # Check if just start date
        if due is None:
            if start.hour != 0 or start.minute != 0 or start.second != 0 or start.microsecond != 0:
                dates['startDate'] = convert_date_to_tick_tick_format(start, tz)
                dates['allDay'] = False
            else:
                dates['startDate'] = convert_date_to_tick_tick_format(start, tz)
                dates['allDay'] = True
            return dates

        # Check all day for both
        if (start.hour != 0 or start.minute != 0 or start.second != 0 or start.microsecond != 0
                or due.hour != 0 or due.minute != 0 or due.second != 0 or due.microsecond != 0):
            # Just convert the dates and return
            dates['startDate'] = convert_date_to_tick_tick_format(start, tz)
            dates['dueDate'] = convert_date_to_tick_tick_format(due, tz)
            dates['allDay'] = False
            return dates

        # All day is true, however normally right now if we were to use a date like Jan 1 - Jan 3,
        # TickTick would create a task that is only Jan 1 - Jan 2 since the date would be up to Jan 3
        # Lets account for that by making the date actually be one more than the current end date
        # This will allow for more natural date input for all day tasks
        days = monthrange(due.year, due.month)
        if due.day + 1 > days[1]:  # Last day of the month
            if due.month + 1 > 12:  # Last month of the year
                year = due.year + 1  # Both last day of month and last day of year
                day = 1
                month = 1
            else:  # Not last month of year, just reset the day and increment the month
                year = due.year
                month = due.month + 1
                day = 1
        else:  # Dont have to worry about incrementing year or month
            year = due.year
            day = due.day + 1
            month = due.month

        due = datetime.datetime(year, month, day)  # No hours, mins, or seconds needed

        dates['startDate'] = convert_date_to_tick_tick_format(start, tz)
        dates['dueDate'] = convert_date_to_tick_tick_format(due, tz)
        dates['allDay'] = True

        return dates

    def builder(self,
                title: str = '',
                projectId: str = None,
                content: str = None,
                desc: str = None,
                allDay: bool = None,
                startDate: datetime.datetime = None,
                dueDate: datetime.datetime = None,
                timeZone: str = None,
                reminders: list = None,
                repeat: str = None,
                priority: int = None,
                sortOrder: int = None,
                items: list = None):
        """
        Builds a task dictionary with the passed fields. This is a helper
        method for task creation.

        Arguments:
            title (str): Desired name of the task
            projectId (str): ID string of the project
            content (str): Content body of the task
            desc (str): Description of the task checklist
            allDay (bool): Boolean for whether the task is all day or not
            startDate (datetime.datetime): Start time of the task
            dueDate (datetime.datetime): End time of the task
            timeZone (str): Time zone for the task
            reminders (list): List of reminder triggers
            repeat (str): Recurring rules for the task
            priority (int): None:0, Low:1, Medium:3, High5
            sortOrder (int): Task sort order
            items (list): Subtasks of task

        Returns:
            dict: A dictionary containing the fields necessary for task creation.

        !!! example
            Building a local task object with a title, start, and due time.

            ```python
            start = datetime(2027, 5, 2)
            end = datetime(2027, 5, 7)
            title = 'Festival'
            task_dict = client.task.builder(title, startDate=start, dueDate=end)
            ```

            ??? Result

                ```python
                {'startDate': '2027-05-02T07:00:00+0000',
                 'dueDate': '2027-05-08T07:00:00+0000',
                 'allDay': True,
                 'title': 'Festival'}
                ```
        """
        task = {'title': title}
        if projectId is not None:
            task['projectId'] = projectId
        if content is not None:
            task['content'] = content
        if desc is not None:
            task['desc'] = desc
        if allDay is not None:
            task['allDay'] = allDay
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

        dates = {}

        # date conversions
        if startDate is not None:
            dates = self.dates(startDate, dueDate, timeZone)

        # merge dicts
        return {**dates, **task}
