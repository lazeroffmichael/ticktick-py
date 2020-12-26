from helpers.constants import VALID_HEX_VALUES
import re


class TagsManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    def create(self, name: str, color_id: str = None, parent_etag: str = None) -> str:
        """
        Creates a tag
        :param name: Name of the tag
        :param color_id: Hex id string of the tag (6 characters)
        :param parent_etag: Etag of the already existing tag that will become the parent
        :return: Etag of the created tag
        """
        # Tag names should not be repeated, so make sure passed name does not exist
        tag_list = self._client.get_etag(search_key='lists', name=name)
        if tag_list:
            raise ValueError(f"Invalid Tag Name '{name}' -> It Already Exists")

        # Check color_id
        if color_id is not None:
            color = re.search(VALID_HEX_VALUES, color_id)
            if not color:
                raise ValueError('Invalid Hex Color String')

        # Check parent_etag
        if parent_etag is not None:
            parent = self._client.get_by_etag(parent_etag)
            if not parent:
                raise ValueError(f"Invalid Parent Etag '{parent_etag}' -> Does Not Exist")

        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'add': [{
                'name': name,
                'parent': parent_etag,
                'color': color_id
            }]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return self._client.parse_etag(response)

    def update(self):
        pass

    def delete(self, etag: str) -> str:
        """
        Deletes the tag with the passed etag if it exists
        :param etag: Etag string of the task
        :return: Etag string of the task
        """
        # Determine if the tag exists

        tag_obj = self._client.get_by_etag(etag, search_key='tags')
        if not tag_obj:
            raise ValueError(f"Tag '{etag}' Does Not Exist To Delete")

        url = self._client.BASE_URL + 'tag'
        params = {
            'name': tag_obj['name']
        }
        response = self._client.http_delete(url, params=params, cookies=self._client.cookies)
        # Find the tag in the tags list and delete it
        for tag in range(len(self._client.state['tags'])):
            if self._client.state['tags'][tag]['etag'] == tag_obj['etag']:
                del self._client.state['tags'][tag]
                break

        return tag_obj['etag']
