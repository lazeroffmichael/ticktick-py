from ticktick.helpers.hex_color import check_hex_color, generate_hex_color
from ticktick.managers.check_logged_in import logged_in


class ProjectManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    @logged_in
    def builder(self, name: str, color: str = 'random', project_type: str = 'TASK', folder_id: str = None) -> dict:
        """
        Creates and returns a project object.

        Arguments:
            name: Desired name of the project - project names cannot be repeated
            color: Hex color string. If none is entered a random color will be generated.
            project_type: 'TASK' or 'NOTE'
            folder_id: The project folder id that the project should be placed under (if desired)

        Returns:
            dict: A dictionary containing all the fields necessary to create a remote project.

        Raises:
            TypeError: If any of the types of the arguments are wrong.
            ValueError: Project name already exists
            ValueError: Project Folder corresponding to the ID does not exist.
            ValueError: The hex string color inputted is invalid.
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not isinstance(color, str):
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

    @logged_in
    def create(self, name: str, color: str = 'random', project_type: str = 'TASK', folder_id: str = None) -> str:
        """
        Creates a project(list) with the specified parameters.
        :param folder_id:
        :param name: Name of the project to be created
        :param color: Desired color for the project in hex
        :param project_type: Defaults to normal "TASK" type, or specify 'NOTE' for note type list
        :return: Id of the created list
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
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
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

    @logged_in
    def update(self, obj):
        """
        Updates the passed project(s)

        Make local changes to the project objects that you want to change first.

        Arguments:
            obj (dict or list): Dict for a single object, or a list of dicts for multiple objects.

        Returns:

        Raises:
            ValueError:
        :param obj: List id of the list to be updated
        :return: list_id
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
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
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

    @logged_in
    def delete(self, ids):
        """
        Deletes the project(s) with the passed IDS.

        !!! warning
            [Tasks](tasks.md) will be deleted from the project. If you want to preserve the
            tasks before deletion, use [move_projects][managers.tasks.TaskManager.move_projects]

        Arguments:
            ids (str or list): ID string of the project to be deleted, or list of ID strings of projects
                to be deleted.

        Returns:
            dict or list: For a single project deleted, a single dictionary of the deleted project will be returned. For multiple
                project deletions, a list of dictionaries will be returned.

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
        self._client.http_post(url, json=payload, cookies=self._client.cookies)
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

    @logged_in
    def archive(self, ids: str) -> str:
        """
        Moves the project(s) to a project folder called "Archived"
        :param ids: Id of the list to be archived
        :return: String specifying the archive was successful
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

    @logged_in
    def create_folder(self, name):
        """
        Creates a project folder -> Folder names can be reused
        :param name: Name of the folder
        :return: httpx response
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
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
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

    @logged_in
    def update_folder(self, folder_id: str) -> str:  # TODO Batch
        """
        Updates an already created list remotely
        :param folder_id: Id of the folder to be updated
        :return: Id of the folder updated
        """

        # Check if the id exists
        obj = self._client.get_by_id(folder_id, search='project_folders')
        if not obj:
            raise KeyError(f"Folder id '{folder_id}' Does Not Exist To Update")

        url = self._client.BASE_URL + 'batch/projectGroup'
        payload = {
            'update': [obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return self._client.get_by_id(self._client.parse_id(response), search='project_folders')

    @logged_in
    def delete_folder(self, ids: str):
        """
        Deletes the folder and ungroups the lists inside
        :param ids:id of the folder
        :return:id of the folder deleted
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
        self._client.http_post(url, json=payload, cookies=self._client.cookies)
        # Delete the list
        deleted_list = []
        for current_id in ids:
            deleted_list.append(self._client.delete_from_local_state(id=current_id, search='project_folders'))

        if len(deleted_list) == 1:
            return deleted_list[0]
        else:
            return deleted_list

