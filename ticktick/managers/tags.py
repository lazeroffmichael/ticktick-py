from ticktick.helpers.hex_color import check_hex_color, generate_hex_color
from ticktick.managers.check_logged_in import logged_in


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

    @logged_in
    def create(self,
               name: str,
               color: str = 'random',
               parent_name: str = None,
               sort: int = None
               ) -> dict:
        """
        Creates a tag
        Allows creation with a name that may normally not be allowed by TickTick for tags
        Normal TickTick excluded characters are: \\ / " # : * ? < > | Space
        :param name: Name of the tag
        :param color: Hex id string of the tag (6 characters) -> Default is random color
            To Specify No Color: None
        :param parent_name: Etag of the already existing tag that will become the parent
        :param sort: Int corresponding to a specific sort type
            0: Sort By List
            1: Sort By Time
            2: Sort By Title
            3: Sort By Tag
            4: Sort By Priority
        :return: Etag of the created tag
        """
        # Tag names should not be repeated, so make sure passed name does not exist
        tag_list = self._client.get_by_fields(search='tags', name=name)
        if tag_list:
            raise ValueError(f"Invalid Tag Name '{name}' -> It Already Exists")

        # Check color_id
        if color == 'random':
            color = generate_hex_color()  # Random color will be generated
        elif color is not None:
            if not check_hex_color(color):
                raise ValueError('Invalid Hex Color String')

        # Check parent_etag
        if parent_name is not None:
            parent = self._client.get_by_fields(search='tags', name=parent_name)
            if not parent:
                raise ValueError(f"Invalid Parent Name '{parent_name}' -> Does Not Exist")

        # Check sort_type
        if sort is None:
            sort = 'project'
        else:
            sort = _sort_string_value(sort)

        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'add': [{
                'name': name,
                'parent': parent_name,
                'color': color,
                'sortType': sort
            }]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return self._client.get_by_etag(self._client.parse_etag(response), search='tags')

    @logged_in
    def update(self,
               old_name: str,
               new_name: str = None,
               color: str = None,
               parent_name: str = None,
               sort: int = None):
        """
        Updates the tag with the passed etag based on the passed parameters
        :param old_name: Etag of the tag to be updated
        :param new_name: Name that the tag should be set to
        :param color: Color that the tag should be set to
        :param parent_name: Etag of the parent to be set to
        :param sort: Integer corresponding to the sort type for the tag
            0: Sort By List
            1: Sort By Time
            2: Sort By Title
            3: Sort By Tag
            4: Sort By Priority
        :return: Etag of the newly updated tag
        """
        # Check if params were passed
        if new_name is None and color is None and parent_name is None and sort is None:
            raise ValueError(f"Fields To Update Must Be Passed")

        # Check if the tag object exists
        obj = self._client.get_by_fields(name=old_name, search='tags')
        if not obj:
            raise ValueError(f"Tag '{old_name}' Does Not Exist To Update")
        obj = obj[0]
        # Updating the name -> Renaming requires a unique endpoint to do separate to color or parent
        if new_name is not None:
            new_etag = self._update_name(new_name, obj)
            obj = self._client.get_by_etag(new_etag, search='tags')

        # Updating the color and sort
        if color is not None or sort is not None:
            new_etag = self._update_color_and_sort(color, sort, obj)
            obj = self._client.get_by_etag(new_etag, search='tags')  # Get the updated obj

        # Updating the parent
        if parent_name is not None:
            new_etag = self._update_parent(parent_name, obj)

        return self._client.get_by_etag(new_etag, search='tags')

    @logged_in
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
        new_obj = self._client.get_by_fields(name=new_name, search='tags')
        # Return the etag of the updated object
        return new_obj[0]['etag']

    @logged_in
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

    @logged_in
    def _update_parent(self, parent_: str, obj: dict) -> str:
        """
        Updates
        :param parent_:
        :param obj:
        :return:
        """
        # Check if the parent_etag exists
        parent_obj = self._client.get_by_fields(name=parent_, search='tags')
        if not parent_obj:
            raise ValueError(f"'Parent '{parent_}' Does Not Exist")
        parent_obj = parent_obj[0]
        obj['parent'] = parent_
        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'update': [parent_obj, obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return response['id2etag'][obj['name']]

    @logged_in
    def merge(self, kept_tag: str, *args):
        """
        Merges the tasks of the passed tags into kept_tag and deletes all the tags except kept_tag
        :param kept_tag: Etag of remaining tag after the merge
        :param args: Etags of the tags to be merged
        :return: Etag of the remaining tag
        """
        # Make sure kept_tag exists
        kept_obj = self._client.get_by_fields(name=kept_tag, search='tags')
        if not kept_obj:
            raise ValueError(f"Kept Tag '{kept_tag}' Does Not Exist To Merge")
        kept_obj = kept_obj[0]

        # Make sure args is not empty
        if not args:
            raise ValueError(f"Must Provide At Least One Tag To Merge")

        # For each tag to merge
        #   Check If Exists
        #   Merge with kept_tag
        for obj in args:
            # Make sure it exists
            retrieved = self._client.get_by_fields(name=obj, search='tags')
            if not retrieved:
                raise ValueError(f"Tag '{obj}' Does Not Exist To Merge")
            retrieved = retrieved[0]

            # Merge
            url = self._client.BASE_URL + 'tag/merge'
            payload = {
                'name': retrieved['name'],
                'newName': kept_obj['name']
            }
            self._client.http_put(url, json=payload, cookies=self._client.cookies)
            self._client.sync()

        return kept_obj

    @logged_in
    def delete(self, name: str) -> dict:
        """
        Deletes the tag with the passed etag if it exists
        :param name: Name of the tag
        :return: Tag object deleted
        """
        # Determine if the tag exists

        tag_obj = self._client.get_by_fields(name=name, search='tags')
        if not tag_obj:
            raise ValueError(f"Tag '{name}' Does Not Exist To Delete")
        tag_obj = tag_obj[0]  # We can assume that only one tag has the name

        url = self._client.BASE_URL + 'tag'
        params = {
            'name': tag_obj['name']
        }
        response = self._client.http_delete(url, params=params, cookies=self._client.cookies)
        # Find the tag in the tags list and delete it, then return the deleted object
        return self._client.delete_from_local_state(search='tags', etag=tag_obj['etag'])
