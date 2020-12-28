from ticktick.helpers.hex_color import check_hex_color, generate_hex_color


def _sort_string_value(sort_type: int) -> str:
    """
    Returns the string corresponding to the sort type integer
    :param sort_type:
    :return:
    """
    if sort_type not in {0, 1, 2, 3}:
        raise ValueError(f"Sort Number '{sort_type}' Is Invalid -> Must Be 0, 1, 2 or 3")
    else:
        sort_dict = {0: 'project',
                     1: 'dueDate',
                     2: 'title',
                     3: 'priority'}
    return sort_dict[sort_type]


class TagsManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    def create(self,
               name: str,
               color_id: str = None,
               parent_etag: str = None,
               sort_type: int = None
               ) -> str:
        """
        Creates a tag
        Allows creation with a name that may normally not be allowed by TickTick for tags
        Normal TickTick excluded characters are: \\ / " # : * ? < > | Space
        :param name: Name of the tag
        :param color_id: Hex id string of the tag (6 characters) -> Default is random color
        :param parent_etag: Etag of the already existing tag that will become the parent
        :param sort_type: Int corresponding to a specific sort type
            0: Sort By List
            1: Sort By Time
            2: Sort By Title
            3: Sort By Tag
            4: Sort By Priority
        :return: Etag of the created tag
        """
        # Tag names should not be repeated, so make sure passed name does not exist
        tag_list = self._client.get_etag(search_key='tags', name=name)
        if tag_list:
            raise ValueError(f"Invalid Tag Name '{name}' -> It Already Exists")

        # Check color_id
        if color_id is None:
            color_id = generate_hex_color()  # Random color will be generated
        else:
            if not check_hex_color(color_id):
                raise ValueError('Invalid Hex Color String')

        # Check parent_etag
        if parent_etag is not None:
            parent = self._client.get_by_etag(parent_etag)
            if not parent:
                raise ValueError(f"Invalid Parent Etag '{parent_etag}' -> Does Not Exist")
            parent_etag = parent['name']

        # Check sort_type
        if sort_type is None:
            sort_type = 'project'
        else:
            sort_type = _sort_string_value(sort_type)

        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'add': [{
                'name': name,
                'parent': parent_etag,
                'color': color_id,
                'sortType': sort_type
            }]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return self._client.parse_etag(response)

    def update(self,
               etag: str,
               new_name: str = None,
               color: str = None,
               parent_etag: str = None,
               sort: int = None):
        """
        Updates the tag with the passed etag based on the passed parameters
        :param etag: Etag of the tag to be updated
        :param new_name: Name that the tag should be set to
        :param color: Color that the tag should be set to
        :param parent_etag: Etag of the parent to be set to
        :param sort: Integer corresponding to the sort type for the tag
            0: Sort By List
            1: Sort By Time
            2: Sort By Title
            3: Sort By Tag
            4: Sort By Priority
        :return: Etag of the newly updated tag
        """
        # Check if params were passed
        if new_name is None and color is None and parent_etag is None and sort is None:
            raise ValueError(f"Fields To Update Must Be Passed")

        # Check if the tag object exists
        obj = self._client.get_by_etag(etag, search_key='tags')
        if not obj:
            raise ValueError(f"Tag '{etag}' Does Not Exist To Update")

        # Updating the name -> Renaming requires a unique endpoint to do separate to color or parent
        if new_name is not None:
            new_etag = self._update_name(new_name, obj)
            obj = self._client.get_by_etag(new_etag, search_key='tags')  # Get the updated obj

        # Updating the color and sort
        if color is not None or sort is not None:
            new_etag = self._update_color_and_sort(color, sort, obj)
            obj = self._client.get_by_etag(new_etag, search_key='tags')  # Get the updated obj

        # Updating the parent
        if parent_etag is not None:
            new_etag = self._update_parent(parent_etag, obj)

        return new_etag

    def _update_name(self, new_name: str, obj: dict) -> str:
        """
        Updates the name of a tag object that already exists
        :param new_name:
        :param etag:
        :return:
        """
        url = self._client.BASE_URL + 'tag/rename'
        payload = {
            'name': obj['name'],
            'newName': new_name
        }
        response = self._client.http_put(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        # Response from TickTick does not return the new etag of the object, we must find it ourselves
        new_etag = self._client.get_etag(name=new_name, search_key='tags')
        # Return the etag of the updated object
        return new_etag[0]

    def _update_color_and_sort(self, color: str, sort_type: int, obj: dict) -> str:
        """
        Updates the color of a tag object that already exists
        :param color: New color to set
        :param sort_type: Integer value of the sort type
        :param obj: Object to change
        :return: Etag of the updated tag object
        """
        if sort_type is not None:
            sort_type = _sort_string_value(sort_type)
        else:
            sort_type = 'project'

        obj['sortType'] = sort_type

        if color is not None:
            if not check_hex_color(color):
                raise ValueError(f"Hex Color String '{color}' Is Not Valid")
            obj['color'] = color

        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'update': [obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return response['id2etag'][obj['name']]

    def _update_parent(self, parent_etag: str, obj: dict) -> str:
        """
        Updates
        :param parent_etag:
        :param obj:
        :return:
        """
        # Check if the parent_etag exists
        parent_obj = self._client.get_by_etag(parent_etag)
        if not parent_obj:
            raise ValueError(f"'Parent '{parent_etag}' Does Not Exist")
        parent_name = parent_obj['name']
        obj['parent'] = parent_name
        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'update': [parent_obj, obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return response['id2etag']

    def merge(self, kept_tag, *args):
        """
        Merges the tasks of the passed tags into kept_tag and deletes all the tags except kept_tag
        :param kept_tag:
        :param args:
        :return:
        """
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
