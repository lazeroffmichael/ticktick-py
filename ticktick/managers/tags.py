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

    SORT_DICTIONARY = {0: 'project',
                       1: 'dueDate',
                       2: 'title',
                       3: 'priority'}

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    def _sort_string_value(self, sort_type: int) -> str:
        """
        Returns the string corresponding to the sort type integer
        :param sort_type:
        :return:
        """
        if sort_type not in {0, 1, 2, 3}:
            raise ValueError(f"Sort Number '{sort_type}' Is Invalid -> Must Be 0, 1, 2 or 3")

        return self.SORT_DICTIONARY[sort_type]

    def _check_fields(self,
                      label: str = None,
                      color: str = 'random',
                      parent_label: str = None,
                      sort: int = None
                      ) -> dict:
        """
        Checks the passed parameters and returns a dictionary of the objects
        :param label: Name of the tag
        :param color: Color of the tag
        :param parent_label: Parent tag name
        :param sort: Sort type of the tag
        :return: Dictionary of the valid objects
        """
        if label is not None:
            # Make sure label is a string
            if not isinstance(label, str):
                raise ValueError(f"Label Must Be A String")
            # Tag names should not be repeated, so make sure passed name does not exist
            tag_list = self._client.get_by_fields(search='tags', name=label.lower())  # Name is lowercase version of label
            if tag_list:
                raise ValueError(f"Invalid Tag Name '{label}' -> It Already Exists")

        # Check color_id
        if not isinstance(color, str):
            raise ValueError(f"Color Must Be A Hex Color String")

        if color.lower() == 'random':
            color = generate_hex_color()  # Random color will be generated
        elif color is not None:
            if not check_hex_color(color):
                raise ValueError('Invalid Hex Color String')

        # Check parent_name
        if parent_label is not None:
            if not isinstance(parent_label, str):
                raise ValueError(f"Parent Name Must Be A String")
            parent_label = parent_label.lower()
            parent = self._client.get_by_fields(search='tags', name=parent_label)
            if not parent:
                raise ValueError(f"Invalid Parent Name '{parent_label}' -> Does Not Exist")

        # Check sort_type
        if sort is None:
            sort = 'project'
        else:
            sort = _sort_string_value(sort)

        # Return our dictionary of checked and changed values
        return {'label': label, 'color': color, 'parent': parent_label, 'sortType': sort, 'name': label.lower()}

    def builder(self,
                label: str,
                color: str = 'random',
                parent: str = None,
                sort: int = None
                ) -> dict:
        """
        Creates and returns a local tag object with the fields. Performs appropriate checks.
        :param label:
        :param color:
        :param parent:
        :param sort:
        :return:
        """
        # Perform checks
        return self._check_fields(label, color=color, parent_label=parent, sort=sort)

    @logged_in
    def create(self,
               label: str,
               color: str = 'random',
               parent: str = None,
               sort: int = None
               ):
        """
        Creates a tag
        Allows creation with a name that may normally not be allowed by TickTick for tags
        Normal TickTick excluded characters are: \\ / " # : * ? < > | Space
        :param label: Name of the tag
        :param color: Hex id string of the tag (6 characters) -> Default is random color
            To Specify No Color: None
        :param parent: Etag of the already existing tag that will become the parent
        :param sort: Int corresponding to a specific sort type
            0: Sort By List
            1: Sort By Time
            2: Sort By Title
            3: Sort By Tag
            4: Sort By Priority
        :return: Tag Object From TickTick or List of Tag Objects
        """
        batch = False  # Bool signifying batch create or not
        if isinstance(label, list):
            # Batch tag creation triggered
            obj = label  # Assuming all correct objects
            batch = True
        else:
            if not isinstance(label, str):
                raise ValueError('Required Positional Argument Must Be A String or List of Tag Objects')
            # Create a single object
            obj = self.builder(label=label, color=color, parent=parent, sort=sort)

        if not batch:
            obj = [obj]

        url = self._client.BASE_URL + 'batch/tag'
        payload = {'add': obj}
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()

        if not batch:
            return self._client.get_by_etag(self._client.parse_etag(response), search='tags')
        else:
            etag = response['id2etag']
            etag2 = list(etag.keys())  # Tag names are out of order
            labels = [x['name'] for x in obj]  # Tag names are in order
            items = [''] * len(obj)  # Create enough spots for the objects
            for tag in etag2:
                index = labels.index(tag)  # Object of the index is here
                actual_etag = etag[tag]  # Get the actual etag
                found = self._client.get_by_etag(actual_etag, search='tags')
                items[index] = found  # Place at the correct index
            return items

    @logged_in
    def rename(self, old: str, new: str) -> dict:
        """
        Renames an existing tag
        :param old: Old name/label of the tag
        :param new: Desired new name of the tag
        :return:
        """
        # Check that both old and new are strings
        if not isinstance(old, str) or not isinstance(new, str):
            raise ValueError('Old and New Must Be Strings')

        # Make sure the old tag exists
        old = old.lower()
        # Check if the tag object exists
        obj = self._client.get_by_fields(name=old, search='tags')
        if not obj:
            raise ValueError(f"Tag '{old}' Does Not Exist To Rename")
        obj = obj[0]

        # Make sure the new tag does not exist
        temp_new = new.lower()
        # Check if the tag object exists
        found = self._client.get_by_fields(name=temp_new, search='tags')
        if found:
            raise ValueError(f"Name '{new}' Already Exists -> Cannot Duplicate Name")

        url = self._client.BASE_URL + 'tag/rename'
        payload = {
            'name': obj['name'],
            'newName': new
        }
        response = self._client.http_put(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        # Response from TickTick does not return the new etag of the object, we must find it ourselves
        new_obj = self._client.get_by_fields(name=temp_new, search='tags')
        # Return the etag of the updated object
        return self._client.get_by_etag(new_obj[0]['etag'], search='tags')

    @logged_in
    def color(self, label: str, color: str) -> dict:
        """
        Sets the color for the tag label passed.
        :param label: Label for the desired tag to be changed
        :param color: 6 Character Hex Color String
        :return: Updated Dictionary Object
        """
        if not isinstance(label, str) or not isinstance(color, str):
            raise ValueError('Label and Color Must Be Strings')

        # Get the object
        label = label.lower()
        obj = self._client.get_by_fields(name=label, search='tags')
        if not obj:
            raise ValueError(f"Tag '{label}' Does Not Exist To Update")
        obj = obj[0]

        # Check the color
        if not check_hex_color(color):
            raise ValueError(f"Hex Color String '{color}' Is Not Valid")

        obj['color'] = color  # Set the color

        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'update': [obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return self._client.get_by_etag(response['id2etag'][obj['name']])

    @logged_in
    def sorting(self, label: str, sort: int) -> dict:
        """
        Sorts the tag based on the passed integer.
        :param label:
        :param sort:
        :return:
        """
        if not isinstance(label, str) or not isinstance(sort, int):
            raise ValueError('Label Must Be A String and Sort Must Be An Int')

        # Get the object
        label = label.lower()
        obj = self._client.get_by_fields(name=label, search='tags')
        if not obj:
            raise ValueError(f"Tag '{label}' Does Not Exist To Update")
        obj = obj[0]
        sort = self._sort_string_value(sort)  # Get the sort string for the value

        obj['sortType'] = sort  # set the object field

        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'update': [obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return self._client.get_by_etag(response['id2etag'][obj['name']])

    @logged_in
    def move(self, label: str, parent: str):
        """
        Moves the tag to the designated parent, or ungroups it.
        :param label:
        :param parent:
        :return:
        """

    @logged_in
    def update(self, #TODO: Make 3 Seperate Functions For These and leave this as generic update
               label: str,
               color: str = None, # name it recolor
               parent_name: str = None, # name it move
               sort: int = None): # name it resort
        """
        Updates the tag with the passed etag based on the passed parameters
        :param label: Label of the tag to be updated
        :param color: Color that the tag should be set to
        :param parent_name: Name of the parent to be set to
        :param sort: Integer corresponding to the sort type for the tag
            0: Sort By List
            1: Sort By Time
            2: Sort By Title
            3: Sort By Tag
            4: Sort By Priority
        :return: Etag of the newly updated tag
        """
        # Check if params were passed
        if color is None and parent_name is None and sort is None:
            raise ValueError(f"Fields To Update Must Be Passed")

        # Check if the tag object exists
        obj = self._client.get_by_fields(name=old_name, search='tags')
        if not obj:
            raise ValueError(f"Tag '{old_name}' Does Not Exist To Update")
        obj = obj[0]
        # Updating the name -> Renaming requires a unique endpoint to do separate to color or parent


        # Updating the color and sort
        if color is not None or sort is not None:
            new_etag = self._update_color_and_sort(color, sort, obj)
            obj = self._client.get_by_etag(new_etag, search='tags')  # Get the updated obj

        # Updating the parent
        if parent_name is not None:
            new_etag = self._update_parent(parent_name, obj)

        return self._client.get_by_etag(new_etag, search='tags')


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
    def merge(self, merged: str, *args):
        """
        Merges the tasks of the passed tags into kept_tag and deletes all the tags except kept_tag
        Args can be individual label strings, or a list of strings
        :param merged: Name of the tag to be kept
        :param args: Etags of the tags to be merged
        :return: Etag of the remaining tag
        """
        # TODO: Make it be able to handle a list
        # Make sure kept_tag is a string
        if not isinstance(merged, str):
            raise ValueError('Merged Must Be A String')

        # Make sure args is not empty
        if not args:
            raise ValueError(f"Must Provide At Least One Tag To Merge")

        # Lowercase merged
        merged = merged.lower()
        # Make sure merged exists
        kept_obj = self._client.get_by_fields(name=merged, search='tags')
        if not kept_obj:
            raise ValueError(f"Kept Tag '{merged}' Does Not Exist To Merge")
        kept_obj = kept_obj[0]

        # Verify all args are valid, and add them to a list
        merge_queue = []
        for obj in args:
            # Case 1 for string
            if isinstance(obj, str):
                string = obj.lower()
                # Make sure it exists
                retrieved = self._client.get_by_fields(name=string, search='tags')
                if not retrieved:
                    raise ValueError(f"Tag '{obj}' Does Not Exist To Merge")
                merge_queue.append(retrieved[0])
            elif isinstance(obj, list):
                for item in obj:  # Loop through the items in the list and check items are a string and exist
                    # Make sure the item is a string
                    if not isinstance(item, str):
                        raise ValueError(f"Item '{item}' Must Be A String")
                    string = item.lower()
                    # Make sure it exists
                    found = self._client.get_by_fields(name=string, search='tags')
                    if not found:
                        raise ValueError(f"Tag '{item}' Does Not Exist To Merge")
                    merge_queue.append(found[0])

            else:
                raise ValueError(f"Task Name Invalid: {obj} -> Must Be String or List Of Strings")

        for labels in merge_queue:
            # Merge
            url = self._client.BASE_URL + 'tag/merge'
            payload = {
                'name': labels['name'],
                'newName': kept_obj['name']
            }
            self._client.http_put(url, json=payload, cookies=self._client.cookies)
            self._client.sync()

        return kept_obj

    @logged_in
    def delete(self, label: str) -> dict:
        """
        Deletes the tag with the passed etag if it exists
        Note: No batch deleting of tags can occur :(
        :param label: Name of the tag
        :return: Tag object deleted
        """
        # Determine if the tag exists
        if not isinstance(label, str):
            raise ValueError('Label Must Be A String')

        label = label.lower()  # Process all labels as lowercase

        tag_obj = self._client.get_by_fields(name=label, search='tags')
        if not tag_obj:
            raise ValueError(f"Tag '{label}' Does Not Exist To Delete")
        tag_obj = tag_obj[0]  # We can assume that only one tag has the name

        url = self._client.BASE_URL + 'tag'
        params = {
            'name': tag_obj['name']
        }
        response = self._client.http_delete(url, params=params, cookies=self._client.cookies)
        # Find the tag in the tags list and delete it, then return the deleted object
        return self._client.delete_from_local_state(search='tags', etag=tag_obj['etag'])
