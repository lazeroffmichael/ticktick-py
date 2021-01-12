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
                raise TypeError(f"Label Must Be A String")
            # Tag names should not be repeated, so make sure passed name does not exist
            tag_list = self._client.get_by_fields(search='tags', name=label.lower())  # Name is lowercase version of label
            if tag_list:
                raise ValueError(f"Invalid Tag Name '{label}' -> It Already Exists")

        # Check color_id
        if not isinstance(color, str):
            raise TypeError(f"Color Must Be A Hex Color String")

        if color.lower() == 'random':
            color = generate_hex_color()  # Random color will be generated
        elif color is not None:
            if not check_hex_color(color):
                raise ValueError('Invalid Hex Color String')

        # Check parent_name
        if parent_label is not None:
            if not isinstance(parent_label, str):
                raise TypeError(f"Parent Name Must Be A String")
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
                raise TypeError('Required Positional Argument Must Be A String or List of Tag Objects')
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
            raise TypeError('Old and New Must Be Strings')

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
            raise TypeError('Label and Color Must Be Strings')

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
            raise TypeError('Label Must Be A String and Sort Must Be An Int')

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
    def parent(self, label: str, parent: str):
        """
        Moves the tag to the designated parent, or ungroups it if parent is None
        NOTE: Cannot nest tags more than one level. If you try to nest a tag under a tag
        that is already nested, the parent will no longer be nested anymore.
        :param label: Label of the tag to be changed
        :param parent: Label of the parent tag
        :return: Updated tag object
        """
        if not isinstance(label, str):
            raise TypeError('Inputs Must Be Strings')

        if parent is not None:
            if not isinstance(parent, str):
                raise TypeError('Inputs Must Be Strings')

        # Get the object
        label = label.lower()
        obj = self._client.get_by_fields(name=label, search='tags')
        if not obj:
            raise ValueError(f"Tag '{label}' Does Not Exist To Update")
        obj = obj[0]

        # Four Cases
        # Case 1: No Parent -> Want a Parent
        # Case 2: No Parent -> Doesn't Want a Parent
        # Case 3: Has Parent -> Wants a Different Parent
        # Case 4: Has Parent -> Doesn't Want a Parent

        # Case 1: Determine if the object has a parent
        try:
            if obj['parent']:
                # It has a parent
                if parent is not None:  # Case 3
                    # check if the parent is already the same, if it is just return
                    if obj['parent'] == parent.lower():
                        return obj
                    else:
                        new_p = parent.lower()
                        obj['parent'] = new_p
                else:
                    new_p = obj['parent']  # Case 4
                    obj['parent'] = ''
            elif obj['parent'] is None:
                raise ValueError('Parent Does Not Exist')

        except KeyError:
            # It does not have a parent
            if parent is not None:  # Wants a different parent
                new_p = parent.lower()  # -> Case 1
                obj['parent'] = new_p
            else:  # Doesn't want a parent -> Case 2
                return obj  # We don't have to do anything if no parent and doesn't want a parent

        # Have to find the project
        pobj = self._client.get_by_fields(name=new_p, search='tags')
        if not pobj:
            raise ValueError(f"Tag '{parent}' Does Not Exist To Set As Parent")
        pobj = pobj[0]  # Parent object found correctly

        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'update': [pobj, obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()
        return self._client.get_by_etag(response['id2etag'][obj['name']], search='tags')

    @logged_in
    def update(self, obj):
        """
        Generic update method -> Change tag objects locally and pass them to this function to update
        Note: Updating through this may not work as intended, its suggested you use the other class
        methods to update a tags properties
        :param obj: Tag object or list of tag objects that you want to update
        :return: The updated tag object
        """
        batch = False  # Bool signifying batch create or not
        if isinstance(obj, list):
            # Batch tag creation triggered
            obj_list = obj  # Assuming all correct objects
            batch = True
        else:
            if not isinstance(obj, dict):
                raise TypeError('Required Positional Argument Must Be A String or List of Tag Objects')

        if not batch:
            obj_list = [obj]

        url = self._client.BASE_URL + 'batch/tag'
        payload = {'update': obj_list}
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies)
        self._client.sync()

        if not batch:
            return self._client.get_by_etag(self._client.parse_etag(response), search='tags')
        else:
            etag = response['id2etag']
            etag2 = list(etag.keys())  # Tag names are out of order
            labels = [x['name'] for x in obj_list]  # Tag names are in order
            items = [''] * len(obj_list)  # Create enough spots for the objects
            for tag in etag2:
                index = labels.index(tag)  # Object of the index is here
                actual_etag = etag[tag]  # Get the actual etag
                found = self._client.get_by_etag(actual_etag, search='tags')
                items[index] = found  # Place at the correct index
            return items

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
    def delete(self, label) -> dict:
        """
        Deletes the tag with the passed etag if it exists
        Label str of list of label strings
        :param label: Name of the tag
        :return: Tag object deleted
        """
        # Determine if the tag exists
        if not isinstance(label, str) and not isinstance(label, list):
            raise TypeError('Label Must Be A String or List Of Strings')

        url = self._client.BASE_URL + 'tag'
        if isinstance(label, str):
            label = [label]  # If a singular string we are going to add it to a list

        objects = []
        for lbl in label:
            if not isinstance(lbl, str):
                raise TypeError(f"'{lbl}' Must Be A String")
            lbl = lbl.lower()
            tag_obj = self._client.get_by_fields(name=lbl, search='tags')  # Get the tag object
            if not tag_obj:
                raise ValueError(f"Tag '{lbl}' Does Not Exist To Delete")
            # We can assume that only one tag has the name
            params = {
                'name': tag_obj['name']
            }
            response = self._client.http_delete(url, params=params, cookies=self._client.cookies)
            # Find the tag in the tags list and delete it, then return the deleted object
            objects.append(self._client.delete_from_local_state(search='tags', etag=tag_obj['etag']))
        if len(objects) == 1:
            return objects[0]
        else:
            return objects
