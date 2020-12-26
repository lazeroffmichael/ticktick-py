from helpers.constants import VALID_HEX_VALUES
from ticktick.managers.check_logged_in import logged_in
import re


class ListManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    @logged_in
    def create(self, list_name: str, color_id: str = None, list_type: str = 'TASK', folder_id: str = None) -> str:
        """
        Creates a list (project) with the specified parameters.
        :param folder_id:
        :param list_name: Name of the project to be created
        :param color_id: Desired color for the project in hex
        :param list_type: Defaults to normal "TASK" type, or specify 'NOTE' for note type list
        :return: Id of the created list
        """
        # Go through self.state['lists'] and determine if the name already exists
        id_list = self._client.get_id(search_key='lists', name=list_name)
        if id_list:
            raise ValueError(f"Invalid List Name '{list_name}' -> It Already Exists")

        # Determine if parent list exists
        if folder_id is not None:
            parent = self._client.get_by_id(folder_id, search_key='list_folders')
            if not parent:
                raise ValueError(f"Parent Id {folder_id} Does Not Exist")

        # Make sure list type is valid
        if list_type != 'TASK' and list_type != 'NOTE':
            raise ValueError(f"Invalid List Type '{list_type}' -> Should be 'TASK' or 'NOTE'")

        if color_id is not None:
            check_color = re.search(VALID_HEX_VALUES, color_id)
            if not check_color:
                raise ValueError('Invalid Hex Color String')

        url = self._client.BASE_URL + 'batch/project'
        payload = {
            'add': [{'name': list_name,
                     'color': color_id,
                     'kind': list_type,
                     'groupId': folder_id
                     }]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return self._client.parse_id(response)

    @logged_in
    def update(self, list_id: str) -> str:
        """
        Updates the list remotely with the passed id
        Make local changes to the list you want to change -> then update
        :param list_id: List id of the list to be updated
        :return: list_id
        """
        # Check if the id exists
        returned_object = self._client.get_by_id(list_id, search_key='lists')
        if not returned_object:
            raise KeyError(f"List id '{list_id}' Does Not Exist To Update")

        url = self._client.BASE_URL + 'batch/project'
        payload = {
            'update': [returned_object]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return self._client.parse_id(response)

    @logged_in
    def delete(self, list_id: str) -> str:
        """
        Deletes the list with the passed list_id if it exists
        :param list_id: Id of the list to be deleted
        :return: id of the list that was deleted
        """
        # Check if the id exists
        list_object = self._client.get_by_id(list_id, search_key='lists')
        if not list_object:
            raise KeyError(f"List id '{list_id}' Does Not Exist To Delete")

        url = self._client.BASE_URL + 'batch/project'
        payload = {
            'delete': [list_id],
        }
        self._client.http_post(url, json=payload, cookies=self._client.cookies)
        for j in range(len(self._client.state['lists'])):
            if self._client.state['lists'][j]['id'] == list_id:
                break
        del self._client.state['lists'][j]

        return list_id

    @logged_in
    def archive(self, list_id: str) -> str:
        """
        Moves the passed list to "Archived Lists" instead of deleting
        :param list_id: Id of the list to be archived
        :return: String specifying the archive was successful
        """
        # Check if the name exists
        obj = self._client.get_by_id(list_id)
        if not obj:
            raise KeyError(f"List id '{list_id}' Does Not Exist To Archive")

        # Check if the list is already archived
        if obj['closed'] is False or obj['closed'] is None:
            url = self._client.BASE_URL + 'batch/project'
            obj['closed'] = True
            payload = {
                'update': [obj]
            }
            self._client.http_post(url, json=payload, cookies=self._client.cookies)

        # List still exists so don't delete
        return list_id

    @logged_in
    def create_folder(self, folder_name: str) -> dict:
        """
        Creates a list folder
        :param folder_name: Name of the folder
        :return: httpx response
        """
        # Folder names can be reused
        url = self._client.BASE_URL + 'batch/projectGroup'
        payload = {
            'add': [{'name': folder_name,
                     'listType': 'group'
                     }]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return self._client.parse_id(response)

    @logged_in
    def update_folder(self, folder_id: str) -> str:
        """
        Updates an already created list remotely
        :param folder_id: Id of the folder to be updated
        :return: Id of the folder updated
        """
        # Check if the id exists
        obj = self._client.get_by_id(folder_id, search_key='list_folders')
        if not obj:
            raise KeyError(f"Folder id '{folder_id}' Does Not Exist To Update")

        url = self._client.BASE_URL + 'batch/projectGroup'
        payload = {
            'update': [obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return folder_id

    @logged_in
    def delete_folder(self, folder_id: str) -> str:
        """
        Deletes the folder and ungroups the lists inside
        :param folder_id:id of the folder
        :return:id of the folder deleted
        """
        # Check if the id exists
        obj = self._client.get_by_id(folder_id)
        if not obj:
            raise KeyError(f"Folder id '{folder_id}' Does Not Exist To Delete")

        url = self._client.BASE_URL + 'batch/projectGroup'
        payload = {
            'delete': [folder_id]
        }
        self._client.http_post(url, json=payload, cookies=self._client.cookies)
        for k in range(len(self._client.state['list_folders'])):
            if self._client.state['list_folders'][k]['id'] == folder_id:
                break

        del self._client.state['list_folders'][k]

        return folder_id

    def create_smart_list(self):
        pass