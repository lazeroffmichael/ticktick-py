from ticktick.helpers.hex_color import check_hex_color, generate_hex_color
from ticktick.managers.check_logged_in import logged_in


class ProjectManager:
    """
    Handles all interactions for projects.
    """
    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token
        self.headers = self._client.HEADERS

    def builder(self, name: str, color: str = 'random', project_type: str = 'TASK', folder_id: str = None) -> dict:
        """
        Creates and returns a local project object. Helper method for [create][managers.projects.ProjectManager.create]
        to make batch creating projects easier.

        !!! note
            The project [folder][managers.projects.ProjectManager.create_folder] must already exist prior to calling this method.

        Arguments:
            name: Desired name of the project - project names cannot be repeated
            color: Hex color string. A random color will be generated if no color is specified.
            project_type: 'TASK' or 'NOTE'
            folder_id: The project folder id that the project should be placed under (if desired)

        Returns:
            A dictionary containing all the fields necessary to create a remote project.

        Raises:
            TypeError: If any of the types of the arguments are wrong.
            ValueError: Project name already exists
            ValueError: Project Folder corresponding to the ID does not exist.
            ValueError: The hex string color inputted is invalid.

        Argument rules are shared with [create][managers.projects.ProjectManager.create], so for more examples on how
        to use the arguments see that method.

        !!! example
            ```python
            project_name = 'Work'  # The name of our project

            # Lets assume that we have a project group folder that already exists named 'Productivity'
            productivity_folder = client.get_by_fields(name='Productivity', search='project_folders')
            productivity_id = productivity_folder['id']

            # Build the object
            project_object = client.project.builder(project_name, folder_id=productivity_id)
            ```

            ??? success "Result"
                ```python
                # The fields needed for a successful project creation are set.
                {'name': 'Work', 'color': '#665122', 'kind': 'TASK', 'groupId': '5ffe11b7b04b356ce74d49da'}
                ```
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not isinstance(color, str) and color is not None:
            raise TypeError("Color must be a string")
        if not isinstance(project_type, str):
            raise TypeError("Project type must be a string")
        if not isinstance(folder_id, str) and folder_id is not None:
            raise TypeError("Folder id must be a string")

        # Go through self.state['lists'] and determine if the name already exists
        id_list = self._client.get_by_fields(search='projects', name=name)
        if id_list:
            raise ValueError(f"Invalid Project Name '{name}' -> It Already Exists")

        # Determine if parent list exists
        if folder_id is not None:
            parent = self._client.get_by_id(folder_id, search='project_folders')
            if not parent:
                raise ValueError(f"Parent Id {folder_id} Does Not Exist")

        # Make sure project type is valid
        if project_type != 'TASK' and project_type != 'NOTE':
            raise ValueError(f"Invalid Project Type '{project_type}' -> Should be 'TASK' or 'NOTE'")

        # Check color_id
        if color == 'random':
            color = generate_hex_color()  # Random color will be generated
        elif color is not None:
            if not check_hex_color(color):
                raise ValueError('Invalid Hex Color String')

        return {'name': name, 'color': color, 'kind': project_type, 'groupId': folder_id}

    def create(self, name, color: str = 'random', project_type: str = 'TASK', folder_id: str = None):
        """
        Creates a project remotely. Supports single project creation or batch project creation.

        Arguments:
            name (str or list):
                **Single Project** (str) : The desired name of the project. Project names cannot be repeated.

                **Multiple Projects** (list) : A list of project objects created using the [builder][managers.projects.ProjectManager.builder] method.
            color: Hex color string. A random color will be generated if no color is specified.
            project_type: 'TASK' or 'NOTE'
            folder_id: The project folder id that the project should be placed under (if desired)

        Returns:
            dict or list: **Single Project**: Return the dictionary of the object.

            **Multiple Projects**: Return a list of dictionaries containing all the created objects in the same order as created.

        Raises:
            TypeError: If any of the types of the arguments are wrong.
            ValueError: Project name already exists
            ValueError: Project Folder corresponding to the ID does not exist.
            ValueError: The hex string color inputted is invalid.
            RuntimeError: The project(s) could not be created.

        !!! example "Single Project"

            === "Just A Name"
                ```python
                project = client.project.create('School')
                ```

                ??? success "Result"
                    ```python
                    # The dictionary object of the created project is returned.
                    {'id': '5ffe1673e4b062d60dd29dc0', 'name': 'School', 'isOwner': True, 'color': '#51b9e3', 'inAll': True,
                    'sortOrder': 0, 'sortType': None, 'userCount': 1, 'etag': 'uerkdkcd',
                    'modifiedTime': '2021-01-12T21:36:51.890+0000', 'closed': None, 'muted': False,
                    'transferred': None, 'groupId': None, 'viewMode': None, 'notificationOptions': None,
                    'teamId': None, 'permission': None, 'kind': 'TASK'}
                    ```
                    Our project is created.

                    [![project-create.png](https://i.postimg.cc/d1NNqN7F/project-create.png)](https://postimg.cc/PpZQy4zV)

            === "Specify a Color"
                A random color can be generated using [generate_hex_color][helpers.hex_color.generate_hex_color].
                However, just not specifying a color will automatically generate a random color (as seen in the previous tab).
                You can always specify the color that you want.

                ```python
                project = client.project.create('Work', color='#86bb6d')
                ```

                ??? success "Result"
                    Our project is created with the color specified.

                    [![project-color.png](https://i.postimg.cc/K8ppnvrb/project-color.png)](https://postimg.cc/5XvmJJRK)

            === "Changing the Project Type"
                The default project type is for Tasks. To change the type to handle Notes, pass in the string 'NOTE'

                ```python
                project = client.project.create('Hobbies', project_type='NOTE')
                ```

                ??? success "Result"
                    The project type is now for notes.

                    [![project-note.png](https://i.postimg.cc/fy0Mhrzt/project-note.png)](https://postimg.cc/rRcB1gtM)

            === "Creating Inside of A Folder"
                !!! warning "Note For `folder_id`"
                    The project [folder][managers.projects.ProjectManager.create_folder] must already exist prior to calling this method.

                ```python
                project_name = 'Day Job'  # The name of our project

                # Lets assume that we have a project group folder that already exists named 'Productivity'
                productivity_folder = client.get_by_fields(name='Productivity', search='project_folders')
                productivity_id = productivity_folder['id']

                # Create the object
                project_object = client.project.create(project_name, folder_id=productivity_id)
                ```

                ??? success "Result"
                    The project was created in the group folder.

                    [![project-create-with-folder.png](https://i.postimg.cc/mr53rmfN/project-create-with-folder.png)](https://postimg.cc/rd5RnCpK)

        !!! example "Multiple Projects (batch)"
            To create multiple projects, you will need to build the projects locally prior to calling the `create` method. This
            can be accomplished using the [builder][managers.projects.ProjectManager.builder] method. Pass in a list of the locally created
            project objects to create them remotely.

            !!! warning "(Again About Folders)"
                The project folders should already be created prior to calling the create method.

            ```python
            # Lets assume that we have a project group folder that already exists named 'Productivity'
            productivity_folder = client.get_by_fields(name='Productivity', search='project_folders')
            productivity_id = productivity_folder['id']
            # Names of our projects
            name_1 = 'Reading'
            name_2 = 'Writing'
            # Build the local projects
            project1 = client.project.builder(name_1, folder_id=productivity_id)
            project2 = client.project.builder(name_2, folder_id=productivity_id)
            project_list = [project1, project2]
            # Create the projects
            project_object = client.project.create(project_list)
            ```

            ??? success "Result"
                When multiple projects are created, the dictionaries will be returned in a list in the same order as
                the input.

                ```python
                [{'id': '5ffe24a18f081003f3294c44', 'name': 'Reading', 'isOwner': True, 'color': '#6fcbdf',
                'inAll': True, 'sortOrder': 0, 'sortType': None, 'userCount': 1, 'etag': 'qbj4z0gl',
                'modifiedTime': '2021-01-12T22:37:21.823+0000', 'closed': None, 'muted': False, 'transferred': None,
                'groupId': '5ffe11b7b04b356ce74d49da', 'viewMode': None, 'notificationOptions': None, 'teamId': None,
                'permission': None, 'kind': 'TASK'},

                {'id': '5ffe24a18f081003f3294c46', 'name': 'Writing', 'isOwner': True,
                'color': '#9730ce', 'inAll': True, 'sortOrder': 0, 'sortType': None, 'userCount': 1, 'etag': 'u0loxz2v',
                'modifiedTime': '2021-01-12T22:37:21.827+0000', 'closed': None, 'muted': False, 'transferred': None,
                'groupId': '5ffe11b7b04b356ce74d49da', 'viewMode': None, 'notificationOptions': None, 'teamId': None,
                'permission': None, 'kind': 'TASK'}]
                ```
                [![project-batch-create.png](https://i.postimg.cc/8CHH8xSZ/project-batch-create.png)](https://postimg.cc/d7hdrHDC)

        """
        if isinstance(name, list):
            # If task name is a list, we will batch create objects
            obj = name
            batch = True
        # Create the single project object
        elif isinstance(name, str):
            batch = False
            obj = self.builder(name=name,
                               color=color,
                               project_type=project_type,
                               folder_id=folder_id)
            obj = [obj]

        else:
            raise TypeError(f"Required Positional Argument Must Be A String or List of Project Objects")

        url = self._client.BASE_URL + 'batch/project'
        payload = {
            'add': obj
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        self._client.sync()
        if len(obj) == 1:
            return self._client.get_by_id(self._client.parse_id(response), search='projects')
        else:
            etag = response['id2etag']
            etag2 = list(etag.keys())  # Get the ids
            items = [''] * len(obj)  # Create enough spots for the objects
            for proj_id in etag2:
                found = self._client.get_by_id(proj_id, search='projects')
                for original in obj:
                    if found['name'] == original['name']:
                        # Get the index of original
                        index = obj.index(original)
                        # Place found at the index in return list
                        items[index] = found
            return items

    def update(self, obj):
        """
        Updates the passed project(s). Supports single project update and multiple project update (batch)

        Make local changes to the project objects that you want to change first, then pass the actual objects to the method.

        !!! info
            Every potential update to a project's attributes have not been tested. See [Example `TickTick` Project Dictionary](projects.md#example-ticktick-project-dictionary) for
            a listing of the fields present in a project.

        Arguments:
            obj (dict or list):
                **Single Project (dict)**: The project dictionary.

                **Multiple Projects (list)**: A list of project dictionaries.

        Returns:
            dict or list:
            **Single Project (dict)**: The updated project dictionary

            **Multiple Projects (list)**: A list containing the updated project dictionaries.

        Raises:
            TypeError: If the input is not a dict or a list.
            RuntimeError: If the projects could not be updated successfully.

        Updates are done by changing the fields in the objects locally first.

        !!! example "Single Project Update"

            === "Changing The Name"
                ```python
                # Lets assume that we have a project named "Reading" that we want to change to "Summer Reading"
                project = client.get_by_fields(name='Reading', search='projects')  # Get the project
                # Now lets change the name
                project['name'] = 'Summer Reading'
                # Updating a single project requires just passing in the entire dictionary.
                updated = client.project.update(project)
                ```

                ??? success "Result"
                    The dictionary is returned and the name changed remotely.
                    ```python
                    {'id': '5ffe24a18f081003f3294c44', 'name': 'Summer Reading', 'isOwner': True,
                    'color': '#6fcbdf', 'inAll': True, 'sortOrder': -6236426731520,
                    'sortType': 'sortOrder', 'userCount': 1, 'etag': '0vbsvn8e', 'modifiedTime': '2021-01-12T23:38:16.456+0000',
                    'closed': None, 'muted': False, 'transferred': None, 'groupId': '5ffe2d37b04b35082bbcdf74',
                    'viewMode': 'list', 'notificationOptions': None, 'teamId': None,
                    'permission': None, 'kind': 'TASK'}
                    ```
                    **Before**

                    [![project-update-before.png](https://i.postimg.cc/K8hcpzvP/project-update-before.png)](https://postimg.cc/crTNrd3C)

                    **After**

                    [![project-update-after.png](https://i.postimg.cc/DwcWqsdJ/project-update-after.png)](https://postimg.cc/FY7svY6N)

        !!! example "Multiple Project Update"

            === "Changing Multiple Names"

                ```python
                # Lets assume that we have a project named "Writing" that we want to change to "Summer Reading"
                project = client.get_by_fields(name='Writing', search='projects')  # Get the project
                project['name'] = 'Summer Writing'
                # Lets assume that we have a project named "Movies" that we want to change to "Summer Movies"
                movie_project = client.get_by_fields(name='Movies', search='projects')
                movie_project['name'] = 'Summer Movies'
                # Updating multiple projects requires passing the projects in a list.
                update_list = [project, movie_project]
                # Lets update remotely now
                updated_projects = client.project.update(update_list)
                ```

            ??? success "Result"
                A list containing the updated projects is returned.

                ```python
                [{'id': '5ffe24a18f081003f3294c46', 'name': 'Summer Reading',
                'isOwner': True, 'color': '#9730ce', 'inAll': True, 'sortOrder': 0,
                'sortType': None, 'userCount': 1, 'etag': 'bgl0pkm8',
                'modifiedTime': '2021-01-13T00:13:29.796+0000', 'closed': None,
                'muted': False, 'transferred': None, 'groupId': '5ffe11b7b04b356ce74d49da',
                'viewMode': None, 'notificationOptions': None, 'teamId': None, 'permission': None,
                'kind': 'TASK'},

                {'id': '5ffe399c8f08237f3d144ece', 'name': 'Summer Movies', 'isOwner': True,
                'color': '#F18181', 'inAll': True, 'sortOrder': -2843335458816, 'sortType': 'sortOrder',
                'userCount': 1, 'etag': 'jmjy1xtc', 'modifiedTime': '2021-01-13T00:13:29.800+0000',
                'closed': None, 'muted': False, 'transferred': None, 'groupId': '5ffe11b7b04b356ce74d49da',
                'viewMode': None, 'notificationOptions': None, 'teamId': None, 'permission': None, 'kind': 'TASK'}]
                ```

                **Before**

                [![project-update-multiople.png](https://i.postimg.cc/9QbcJH81/project-update-multiople.png)](https://postimg.cc/zyLmG61R)

                **After**

                [![project-update-multiple-after.png](https://i.postimg.cc/3RVGNv2y/project-update-multiple-after.png)](https://postimg.cc/0MGjHrWx)

        """
        # Check the types
        if not isinstance(obj, dict) and not isinstance(obj, list):
            raise TypeError("Project objects must be a dict or list of dicts.")

        if isinstance(obj, dict):
            tasks = [obj]
        else:
            tasks = obj

        url = self._client.BASE_URL + 'batch/project'
        payload = {
            'update': tasks
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        self._client.sync()
        if len(tasks) == 1:
            return self._client.get_by_id(self._client.parse_id(response), search='projects')
        else:
            etag = response['id2etag']
            etag2 = list(etag.keys())  # Get the ids
            items = [''] * len(obj)  # Create enough spots for the objects
            for proj_id in etag2:
                found = self._client.get_by_id(proj_id, search='projects')
                for original in obj:
                    if found['name'] == original['name']:
                        # Get the index of original
                        index = obj.index(original)
                        # Place found at the index in return list
                        items[index] = found
            return items

    def delete(self, ids):
        """
        Deletes the project(s) with the passed ID string.

        !!! warning
            [Tasks](tasks.md) will be deleted from the project. If you want to preserve the
            tasks before deletion, use [move_all][managers.tasks.TaskManager.move_all]

        Arguments:
            ids (str or list):
                **Single Deletion (str)**: ID string of the project

                **Multiple Deletions (list)**: List of ID strings of projects to be deleted.

        Returns:
            dict or list:
            **Single Deletion (dict)**: Dictionary of the deleted project.

            **Multiple Deletions (list)**: A list of dictionaries of the deleted projects.

        Raises:
            TypeError: If `ids` is not a string or list of strings
            ValueError: If `ids` does not exist.
            RuntimeError: If the deletion was not successful.

        !!! example

            === "Single Project Deletion"

                ```python
                # Lets assume that we have a project that exists named 'School'
                school = client.get_by_fields(name='School', search='projects')  # Get the project object
                project_id = school['id']  # Get the project id
                delete = client.project.delete(project_id)
                ```

                A dictionary of the deleted project object will be returned.

            === "Multiple Project Deletion"
                ```python
                # Lets assume that we have two projects that we want to delete: 'School' and 'Work'
                school = client.get_by_fields(name='School', search='projects')  # Get the project object
                work = client.get_by_fields(name='Work', search='projects')
                delete_ids = [school['id'], work['id']]  # A list of the ID strings of the projects to be deleted
                delete = client.project.delete(delete_ids)
                ```

                A list of the deleted dictionary objects will be returned.

        """
        if not isinstance(ids, str) and not isinstance(ids, list):
            raise TypeError('Ids Must Be A String or List Of Strings')

        if isinstance(ids, str):
            proj = self._client.get_by_fields(id=ids, search='projects')
            if not proj:
                raise ValueError(f"Project '{ids}' Does Not Exist To Delete")
            ids = [ids]
        else:
            for i in ids:
                proj = self._client.get_by_fields(id=i, search='projects')
                if not proj:
                    raise ValueError(f"Project '{i}' Does Not Exist To Delete")

        # Delete the task
        url = self._client.BASE_URL + 'batch/project'
        payload = {
            'delete': ids
        }
        self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        # Delete the list
        deleted_list = []
        for current_id in ids:
            tasks = self._client.task.get_from_project(current_id)
            for task in tasks:
                self._client.delete_from_local_state(id=task['id'], search='tasks')
            deleted_list.append(self._client.delete_from_local_state(id=current_id, search='projects'))

        if len(deleted_list) == 1:
            return deleted_list[0]
        else:
            return deleted_list

    def archive(self, ids):
        """
        Moves the project(s) to a project folder created by `TickTick` called "Archived Lists"

        To unarchive a project, change its `'closed'` field to `True`, then [update][managers.projects.ProjectManager.update]

        Arguments:
            ids (str or list):
                **Single Project (str)**: ID string of the project to archive.

                **Multiple Projects (list)**: List of ID strings of the projects to archive.

        Returns:
            dict or list:

            **Single Project (dict)**: Dictionary of the archived object.

            **Multiple Projects (list)**: List of dictionaries of the archived objects.

        Raises:
            TypeError: If `ids` is not a string or list.
            ValueError: If the project(s) don't already exist
            RuntimeError: If the project(s) could not be successfully archived.

        !!! example
            === "Single Project Archive"
                ```python
                # Lets assume there is a project that exists named "Reading"
                reading_project = client.get_by_fields(name="Reading", search="projects")
                reading_project_id = reading_project['id']
                archived = client.project.archive(reading_project_id)
                ```

                ??? success "Result"
                    A single dictionary is returned.
                    ```python
                    {'id': '5ffe1673e4b062d60dd29dc0', 'name': 'Reading', 'isOwner': True, 'color': '#51b9e3', 'inAll': True,
                    'sortOrder': 0, 'sortType': 'sortOrder', 'userCount': 1, 'etag': 'c9tgze9b',
                    'modifiedTime': '2021-01-13T00:34:50.449+0000', 'closed': True, 'muted': False,
                    'transferred': None, 'groupId': None, 'viewMode': None, 'notificationOptions': None,
                    'teamId': None, 'permission': None, 'kind': 'TASK'}
                    ```

                    **Before**

                    [![archive-before.png](https://i.postimg.cc/R0jfVt7W/archive-before.png)](https://postimg.cc/B8BtmXw3)

                    **After**

                    [![archived-after.png](https://i.postimg.cc/xjPkBh4J/archived-after.png)](https://postimg.cc/K4RvMqFx)

            === "Multiple Project Archive"
                ```python
                # Lets assume there is a project that exists named "Reading"
                reading_project = client.get_by_fields(name="Reading", search="projects")
                reading_project_id = reading_project['id']
                # Lets assume another project exists named "Writing"
                writing_project = client.get_by_fields(name='Writing', search='projects')
                writing_project_id = writing_project['id']
                # Archiving multiple requires putting the ID's in a list.
                archive_list = [reading_project_id, writing_project_id]
                archived = client.project.archive(archive_list)
                ```

                ??? success "Result"
                    A list of dictionary objects is returned.
                    ```python
                    [{'id': '5ffe1673e4b062d60dd29dc0', 'name': 'Reading', 'isOwner': True,
                    'color': '#51b9e3', 'inAll': True, 'sortOrder': -7335938359296,
                    'sortType': 'sortOrder', 'userCount': 1, 'etag': 'qrga45as',
                    'modifiedTime': '2021-01-13T00:40:49.839+0000', 'closed': True,
                    'muted': False, 'transferred': None, 'groupId': None, 'viewMode': None,
                    'notificationOptions': None, 'teamId': None, 'permission': None, 'kind': 'TASK'},

                    {'id': '5ffe41328f08237f3d147e33', 'name': 'Writing', 'isOwner': True,
                    'color': '#F2B04B', 'inAll': True, 'sortOrder': -7885694173184, 'sortType': 'sortOrder',
                    'userCount': 1, 'etag': 'aenkajam', 'modifiedTime': '2021-01-13T00:40:49.843+0000',
                    'closed': True, 'muted': False, 'transferred': None, 'groupId': None, 'viewMode': None,
                    'notificationOptions': None, 'teamId': None, 'permission': None, 'kind': 'TASK'}]
                    ```

                    **Before**

                    [![archive-multiple-before.png](https://i.postimg.cc/sgHHmnrb/archive-multiple-before.png)](https://postimg.cc/qNnGMxgG)

                    **After**

                    [![archived-multiple-after.png](https://i.postimg.cc/tg1SMhRJ/archived-multiple-after.png)](https://postimg.cc/rdkNdRr2)
        """
        if not isinstance(ids, str) and not isinstance(ids, list):
            raise TypeError('Ids Must Be A String or List Of Strings')

        objs = []
        if isinstance(ids, str):
            proj = self._client.get_by_fields(id=ids, search='projects')
            if not proj:
                raise ValueError(f"Project '{ids}' Does Not Exist To Archive")
            #  Change the list to archived
            proj['closed'] = True
            objs = [proj]
        else:
            for i in ids:
                proj = self._client.get_by_fields(id=i, search='projects')
                if not proj:
                    raise ValueError(f"Project '{i}' Does Not Exist To Archive")
                proj['closed'] = True
                objs.append(proj)

        return self.update(objs)

    def create_folder(self, name):
        """
        Creates a project folder to allow for project grouping. Project folder names can be repeated.

        Arguments:
            name (str or list):
                **Single Folder (str)**: A string for the name of the folder

                **Multiple Folders (list)**: A list of strings for names of the folders.

        Returns:
            dict or list:
            **Single Folder (dict)**: A dictionary for the created folder.

            **Multiple Folders (list)**: A list of dictionaries for the created folders.

        Raises:
            TypeError: If `name` is not a string or list
            RuntimeError: If the folder(s) could not be created.

        !!! example

            === "Creating a Single Folder"
                A single string for the name is the only parameter needed.

                ```python
                project_folder = client.project.create_folder('Productivity')
                ```

                ??? success "Result"
                    A single dictionary is returned.

                    ```python
                    {'id': '5ffe44528f089fb5795c45bf', 'etag': '9eun9kyc', 'name': 'Productivity', 'showAll': True,
                    'sortOrder': 0, 'deleted': 0, 'userId': 115781412, 'sortType': 'project', 'teamId': None}
                    ```

                    [![folder.png](https://i.postimg.cc/HWRTjtRW/folder.png)](https://postimg.cc/c6RpbfdP)



            === "Creating Multiple Folders"
                The desired names of the folders are passed to create as a list.

                ```python
                names = ['Productivity', 'School', 'Hobbies']
                project_folder = client.project.create_folder(names)
                ```


                ??? success "Result"
                    A list of dictionaries containing the foler objects is returned.

                    ```python
                    [{'id': '5ffe45d6e4b062d60dd3ce15', 'etag': '4nvnuiw1', 'name': 'Productivity',
                    'showAll': True, 'sortOrder': 0, 'deleted': 0, 'userId': 447666584, 'sortType': 'project',
                    'teamId': None},

                    {'id': '5ffe45d6e4b062d60dd3ce16', 'etag': 's072l3pu', 'name': 'School',
                    'showAll': True, 'sortOrder': 0, 'deleted': 0, 'userId': 447666584, 'sortType': 'project',
                    'teamId': None},

                    {'id': '5ffe45d6e4b062d60dd3ce17', 'etag': '12t1xmt9', 'name': 'Hobbies',
                    'showAll': True, 'sortOrder': 0, 'deleted': 0, 'userId': 447666584, 'sortType': 'project',
                    'teamId': None}]
                    ```

                    [![folders-multiple.png](https://i.postimg.cc/2jwXKjds/folders-multiple.png)](https://postimg.cc/0rzf6sBn)
        """
        if not isinstance(name, str) and not isinstance(name, list):
            raise TypeError('Name Must Be A String or List Of Strings')

        objs = []
        if isinstance(name, str):
            names = {
                    'name': name,
                    'listType': 'group'
                    }
            objs = [names]

        else:
            for nm in name:
                objs.append({
                    'name': nm,
                    'listType': 'group'
                })

        url = self._client.BASE_URL + 'batch/projectGroup'
        payload = {
            'add': objs
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        self._client.sync()
        if len(objs) == 1:
            return self._client.get_by_id(self._client.parse_id(response), search='project_folders')
        else:
            etag = response['id2etag']
            etag2 = list(etag.keys())  # Get the ids
            items = [''] * len(objs)  # Create enough spots for the objects
            for proj_id in etag2:
                found = self._client.get_by_id(proj_id, search='project_folders')
                for original in objs:
                    if found['name'] == original['name']:
                        # Get the index of original
                        index = objs.index(original)
                        # Place found at the index in return list
                        items[index] = found
            return items

    def update_folder(self, obj):
        """
        Updates the project folders(s) remotely based off changes made locally.

        Make the changes you want to the project folder(s) first.

        Arguments:
            obj (dict or list):
                **Single Folder (dict)**: The dictionary object of the folder to update.

                **Multiple Folders (list)**: A list containing dictionary objects of folders to update.

        Returns:
            dict or list:
            **Single Folder (dict)**: The dictionary object of the updated folder.

            **Multiple Folders (list)**: A list of dictionary objects corresponding to the updated folders.

        Raises:
            TypeError: If `obj` is not a dictionary or list
            RuntimeError: If the updating was unsuccessful.

        !!! example "Updating A Project Folder"
            === "Single Folder Update"

                ```python
                # Lets assume that we have a folder called "Productivity"
                productivity_folder = client.get_by_fields(name='Productivity', search='project_folders')
                # Lets change the name to "Hobbies"
                productivity_folder['name'] = "Hobbies"
                # Update
                updated_folder = client.project.update_folder(productivity_folder)
                ```

                ??? success "Result"
                    The dictionary of the updated folder is returned.

                    ```python
                    {'id': '5ffe7dab8f089fb5795d8ef2', 'etag': 'r9xl60e5', 'name': 'Hobbies', 'showAll': True,
                    'sortOrder': 0, 'deleted': 0, 'userId': 447666584, 'sortType': 'project', 'teamId': None}
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104408388-c48bbb80-5518-11eb-80d4-34e82bbaffd7.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104408436-e1c08a00-5518-11eb-953a-4933f407e4f9.png)

            === "Multiple Folder Update"

                ```python
                # Lets assume that we have a folder called "Productivity"
                productivity_folder = client.get_by_fields(name='Productivity', search='project_folders')
                # Lets assume that we have another folder called "Games"
                games_folder = client.get_by_fields(name='Games', search='project_folders')
                # Lets change the "Productivity" folder to "Work"
                productivity_folder['name'] = "Work"
                # Lets change the "Games" folder to "Hobbies"
                games_folder['name'] = "Hobbies"
                update_list = [productivity_folder, games_folder]  # List of objects to update
                # Update
                updated_folder = client.project.update_folder(update_list)
                ```

                ??? success "Result"
                    A list of the updated folder objects is returned.

                    ```python
                    [{'id': '5ffe80ce8f08068e86aab288', 'etag': '0oh0pxel', 'name': 'Work', 'showAll': True,
                    'sortOrder': 0, 'deleted': 0, 'userId': 447666584, 'sortType': 'project', 'teamId': None},

                    {'id': '5ffe80cf8f08068e86aab289', 'etag': 'xwvehtfo', 'name': 'Hobbies', 'showAll': True,
                    'sortOrder': 0, 'deleted': 0, 'userId': 447666584, 'sortType': 'project', 'teamId': None}]
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104409143-75468a80-551a-11eb-96c8-5953c97d6f6a.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104409181-8bece180-551a-11eb-8424-9f147d85eb80.png)
        """
        # Check the types
        if not isinstance(obj, dict) and not isinstance(obj, list):
            raise TypeError("Project objects must be a dict or list of dicts.")

        if isinstance(obj, dict):
            tasks = [obj]
        else:
            tasks = obj

        url = self._client.BASE_URL + 'batch/projectGroup'
        payload = {
            'update': tasks
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        self._client.sync()
        if len(tasks) == 1:
            return self._client.get_by_id(self._client.parse_id(response), search='project_folders')
        else:
            etag = response['id2etag']
            etag2 = list(etag.keys())  # Get the ids
            items = [''] * len(tasks)  # Create enough spots for the objects
            for proj_id in etag2:
                found = self._client.get_by_id(proj_id, search='project_folders')
                for original in tasks:
                    if found['name'] == original['name']:
                        # Get the index of original
                        index = tasks.index(original)
                        # Place found at the index in return list
                        items[index] = found
            return items

    def delete_folder(self, ids):
        """
        Deletes the folder(s).

        !!! tip
            Any projects inside of the folder will be preserved - they will just not be grouped anymore.

        Arguments:
            ids (str or list):
                **Single Folder (str)**: The ID of the folder to be deleted.

                **Multiple Folders (list)**: A list containing the ID strings of the folders to be deleted.

        Returns:
            dict or list:
            **Single Folder (dict)**: The dictionary object for the deleted folder.

            **Multiple Folders (list)**: A list of dictionary objects of the deleted folders.

        Raises:
            TypeError: If `ids` is not a str or list
            ValueError: If `ids` does not match an actual folder object.
            RunTimeError: If the folders could not be successfully deleted.

        !!! example "Folder Deletion"

            === "Single Folder Deletion"
                Pass in the ID of the folder object to delete it remotely.

                ```python
                # Lets assume we have a folder named "Productivity"
                project_folder = client.get_by_fields(name='Productivity', search='project_folders')  # Get the project folder
                deleted_folder = client.project.delete_folder(project_folder['id'])
                ```

                ??? success "Result"
                    The folder is deleted, and a single dictionary of the deleted folder object is returned.

                    ```python
                    {'id': '5ffe75008f089fb5795d544a', 'etag': 'e95rdzi7', 'name': 'Productivity',
                    'showAll': True, 'sortOrder': 0, 'deleted': 0, 'userId': 447666584,
                    'sortType': 'project', 'teamId': None}
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104407093-b5573e80-5515-11eb-99dc-16ca4f33d06a.png)

                    **After**

                    The project inside still exists.

                    ![image](https://user-images.githubusercontent.com/56806733/104407123-c607b480-5515-11eb-92ff-15df1d41b404.png)


            === "Multiple Folder Deletion"

                Pass in the list of ID strings of the folders to be deleted.

                ```python
                # Lets assume that we have two folders that already exist: "Productivity" and "Hobbies"
                productivity_folder = client.get_by_fields(name='Productivity', search='project_folders')
                hobbies_folder = client.get_by_fields(name='Hobbies', search='project_folders')
                ids = [productivity_folder['id'], hobbies_folder['id']]
                deleted_folders = client.project.delete_folder(ids)
                ```

                ??? success "Result"
                    The folders are deleted, and a list of dictionaries for the deleted folder objects are returned.

                    ```python
                    [{'id': '5ffe79d78f08237f3d1636ad', 'etag': '2o2dn2al', 'name': 'Productivity',
                    'showAll': True, 'sortOrder': 0, 'deleted': 0, 'userId': 447666584, 'sortType': 'project',
                    'teamId': None},

                    {'id': '5ffe79d78f08237f3d1636ae', 'etag': 'mah5a78l', 'name': 'Hobbies',
                    'showAll': True, 'sortOrder': 0, 'deleted': 0, 'userId': 447666584, 'sortType': 'project',
                    'teamId': None}]
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104407469-8097b700-5516-11eb-9919-069e5beb3b8a.png)

                    **After**

                    All folders deleted and all projects retained.

                    ![image](https://user-images.githubusercontent.com/56806733/104407546-a8871a80-5516-11eb-815b-4df41e3d797a.png)
        """
        if not isinstance(ids, str) and not isinstance(ids, list):
            raise TypeError('Ids Must Be A String or List Of Strings')

        if isinstance(ids, str):
            proj = self._client.get_by_fields(id=ids, search='project_folders')
            if not proj:
                raise ValueError(f"Project Folder '{ids}' Does Not Exist To Delete")
            ids = [ids]
        else:
            for i in ids:
                proj = self._client.get_by_fields(id=i, search='project_folders')
                if not proj:
                    raise ValueError(f"Project Folder '{i}' Does Not Exist To Delete")

        url = self._client.BASE_URL + 'batch/projectGroup'
        payload = {
            'delete': ids
        }
        self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        # Delete the list
        deleted_list = []
        for current_id in ids:
            deleted_list.append(self._client.get_by_id(current_id, search='project_folders'))
        self._client.sync()

        if len(deleted_list) == 1:
            return deleted_list[0]
        else:
            return deleted_list
