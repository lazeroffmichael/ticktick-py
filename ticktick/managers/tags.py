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
    """
    Handles all interactions for tags.
    """
    SORT_DICTIONARY = {0: 'project',
                       1: 'dueDate',
                       2: 'title',
                       3: 'priority'}

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token
        self.headers = self._client.HEADERS

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
        Creates and returns a local tag object. Helper method for [create][managers.tags.TagsManager.create]
        to make batch creating projects easier.

        !!! note
            The parent tag must already exist prior to calling this method.

        Arguments:
            label: Desired label of the tag - tag labels cannot be repeated.
            color: Hex color string. A random color will be generated if no color is specified.
            parent: The label of the parent tag if desired (include capitals in the label if it exists).
            sort: The desired sort type of the tag. Valid integer values are present in the [sort dictionary](tags.md#sort-dictionary). The default
                sort value will be by 'project'

        Returns:
            A dictionary containing all the fields necessary to create a tag remotely.

        Raises:
            TypeError: If any of the types of the arguments are wrong.
            ValueError: Tag label already exists.
            ValueError: Parent tag does not exist.
            ValueError: The hex string color inputted is invalid.

        !!! example
            ```python
            tag_name = 'Books'  # The name for our tag
            parent_name = 'Productivity'  # The desired parent tag -> this should already exist.
            color_code = '#1387c4'
            sort_type = 1  # Sort by `dueDate`
            tag_object = client.tag.builder(tag_name, parent=parent_name, color=color_code, sort=sort_type)
            ```

            ??? success "Result"
                The required fields to create a tag object are created and returned in a dictionary.

                ```python
                {'label': 'Fiction', 'color': '#1387c4', 'parent': 'books', 'sortType': 'dueDate', 'name': 'fiction'}
                ```
        """
        # Perform checks
        return self._check_fields(label, color=color, parent_label=parent, sort=sort)

    def create(self,
               label,
               color: str = 'random',
               parent: str = None,
               sort: int = None
               ):
        """
        Creates a tag remotely. Supports single tag creation or batch tag creation.

        !!! tip
            Allows creation with a label that may normally not be allowed by `TickTick` for tags.

            Normal `TickTick` excluded characters are: \\ / " # : * ? < > | Space

        Arguments:
            label (str or list):
                **Single Tag (str)**: The desired label of the tag. Tag labels cannot be repeated.

                **Multiple Tags (list)**: A list of tag objects created using the [builder][managers.tags.TagsManager.builder] method.
            color: Hex color string. A random color will be generated if no color is specified.
            parent: The label of the parent tag if desired (include capitals in if it exists).
            sort: The desired sort type of the tag. Valid integer values are present in the [sort dictionary](tags.md#sort-dictionary). The default
                sort value will be by 'project'

        Returns:
            dict or list:
            **Single Tag (dict)**: The created tag object dictionary.

            **Multiple Tags (list)**: A list of the created tag object dictionaries.

        Raises:
            TypeError: If any of the types of the arguments are wrong.
            ValueError: Tag label already exists.
            ValueError: Parent tag does not exist.
            ValueError: The hex string color inputted is invalid.
            RuntimeError: The tag(s) could not be created.

        !!! example "Single Tag"

            === "Just A Label"
                ```python
                tag = client.tag.create('Fun')
                ```

                ??? success "Result"
                    The tag object dictionary is returned.

                    ```python
                    {'name': 'fun', 'label': 'Fun', 'sortOrder': 0, 'sortType': 'project', 'color': '#9b69f3', 'etag': '7fc8zb58'}
                    ```
                    Our tag is created.

                    ![image](https://user-images.githubusercontent.com/56806733/104658773-5bbb5500-5678-11eb-9d44-27214203d70e.png)

            === "Specify a Color"
                A random color can be generated using [generate_hex_color][helpers.hex_color.generate_hex_color].
                However, just not specifying a color will automatically generate a random color (as seen in the previous tab)
                You can always specify the color that you want.

                ```python
                tag = client.tag.create('Fun', color='#86bb6d')
                ```

                ??? success "Result"
                    The tag object dictionary is returned and our project is created with the color specified.

                    ```python
                    {'name': 'fun', 'label': 'Fun', 'sortOrder': 0, 'sortType': 'project', 'color': '#86bb6d', 'etag': '8bzzdws3'}
                    ```
                    ![image](https://user-images.githubusercontent.com/56806733/104659184-0c295900-5679-11eb-9f3c-2cd154c0500c.png)

            === "Specifying a Parent Tag"
                Tags can be nested one level. To create a tag that is nested, include the label of the parent tag.
                The parent tag should already exist.

                ```python
                tag = client.tag.create('Fun', parent='Hobbies')
                ```

                ??? success "Result"
                    The tag object dictionary is returned and our tag is created nested under the parent tag.

                    ```python
                    {'name': 'fun', 'label': 'Fun', 'sortOrder': 0, 'sortType': 'project', 'color': '#d2a6e4', 'etag': 'nauticx1', 'parent': 'hobbies'}
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104659785-24e63e80-567a-11eb-9a62-01ebca55e649.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104659814-33ccf100-567a-11eb-8dca-c91aea68b4c7.png)

            === "Sort Type"
                You can specify the sort type of the created tag using integer values from the [sort dictionary](#sort-dictionary).

                ```python
                tag = client.tag.create('Fun', sort=2)  # Sort by `title`
                ```

                ??? success "Result"
                    The tag object dictionary is returned and our tag has the specified sort type.

                    ```python
                    {'name': 'fun', 'label': 'Fun', 'sortOrder': 0, 'sortType': 'title', 'color': '#e7e7ba', 'etag': 'n4k3pezc'}
                    ```

                    ![image](https://user-images.githubusercontent.com/56806733/104660156-e4d38b80-567a-11eb-8c61-8fb874a515a2.png)

        !!! example "Multiple Tag Creation (batch)"
            To create multiple tags, build the tag objects first using the [builder][managers.projects.ProjectManager.builder] method. Pass
            in a list of the project objects to create them remotely.

            ```python
            parent_tag = client.tag.create('Hobbies')  # Create a parent tag.
            # We will create tag objects using builder that will be nested under the parent tag
            fun_tag = client.tag.builder('Fun', sort=2, parent='Hobbies')
            read_tag = client.tag.builder('Read', color='#d2a6e4', parent='Hobbies')
            movie_tag = client.tag.builder('Movies', parent='Hobbies')
            # Create the tags
            tag_list = [fun_tag, read_tag, movie_tag]
            created_tags = client.tag.create(tag_list)
            ```

            ??? success "Result"
                The tag object dictionaries are returned in a list.

                ```python
                [{'name': 'fun', 'label': 'Fun', 'sortOrder': 0, 'sortType': 'title', 'color': '#172d1c', 'etag': '1tceclp4', 'parent': 'hobbies'},

                {'name': 'read', 'label': 'Read', 'sortOrder': 0, 'sortType': 'project', 'color': '#d2a6e4', 'etag': 'ykdem8dg', 'parent': 'hobbies'},

                {'name': 'movies', 'label': 'Movies', 'sortOrder': 0, 'sortType': 'project', 'color': '#94a5f8', 'etag': 'o0nifkbv', 'parent': 'hobbies'}]
                ```

                ![image](https://user-images.githubusercontent.com/56806733/104660625-cb7f0f00-567b-11eb-8649-68646870ccfa.png)
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
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
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
            if len(items) == 1:
                return items[0]
            else:
                return items

    def rename(self, old: str, new: str) -> dict:
        """
        Renames a tag.

        Arguments:
            old: Current label of the tag to be changed.
            new: Desired new label of the tag.

        Returns:
            The tag object with the updated label.

        Raises:
            TypeError: If `old` and `new` are not strings.
            ValueError: If the `old` tag label does not exist.
            ValueError: If the `new` tag label already exists.
            RuntimeError: If the renaming was unsuccessful.

        !!! example "Changing a Tag's Label"

            Pass in the current label of the tag, and the desired new label of the tag.

            ```python
            # Lets assume that we have a tag that already exists named "Movie"
            old_label = "Movie"
            new_label = "Movies"
            updated_tag = client.tag.rename(old_label, new_label)
            ```

            ??? success "Result"
                The updated tag object dictionary is returned.

                ```python
                {'name': 'movies', 'label': 'Movies', 'sortOrder': 0, 'sortType': 'project', 'color': '#134397', 'etag': 'qer1jygy'}
                ```

                **Before**

                ![image](https://user-images.githubusercontent.com/56806733/104661255-fcac0f00-567c-11eb-9f10-69af8b50e0b4.png)

                **After**

                ![image](https://user-images.githubusercontent.com/56806733/104661299-19e0dd80-567d-11eb-825f-758d83178295.png)
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
        response = self._client.http_put(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        self._client.sync()
        # Response from TickTick does not return the new etag of the object, we must find it ourselves
        new_obj = self._client.get_by_fields(name=temp_new, search='tags')
        # Return the etag of the updated object
        return self._client.get_by_etag(new_obj['etag'], search='tags')

    def color(self, label: str, color: str) -> dict:
        """
        Change the color of a tag. For batch changing colors, see [update][managers.tags.TagsManager.update].

        Arguments:
            label: The label of the tag to be changed.
            color: The new desired hex color string.

        Returns:
            The updated tag dictionary object.

        Raises:
            TypeError: If `label` or `color` are not strings.
            ValueError: If the tag `label` does not exist.
            ValueError: If `color` is not a valid hex color string.
            RuntimeError: If changing the color was not successful.

        !!! example "Changing a Tag's Color"
            ```python
            # Lets assume that we have a tag named "Movies" that we want to change the color for.
            new_color = '#134397'
            movies_updated = client.tag.color('Movies', new_color)
            ```

            ??? success "Result"
                The updated tag dictionary object is returned.

                ```python
                {'name': 'movies', 'label': 'Movies', 'sortOrder': 0, 'sortType': 'project', 'color': '#134397', 'etag': 'wwb49yfr'}
                ```

                **Before**

                ![image](https://user-images.githubusercontent.com/56806733/104661749-0eda7d00-567e-11eb-836f-3a8851bcf9a5.png)

                **After**

                ![image](https://user-images.githubusercontent.com/56806733/104661860-55c87280-567e-11eb-93b5-054fa4f1104a.png)
        """
        if not isinstance(label, str) or not isinstance(color, str):
            raise TypeError('Label and Color Must Be Strings')

        # Get the object
        label = label.lower()
        obj = self._client.get_by_fields(name=label, search='tags')
        if not obj:
            raise ValueError(f"Tag '{label}' Does Not Exist To Update")

        # Check the color
        if not check_hex_color(color):
            raise ValueError(f"Hex Color String '{color}' Is Not Valid")

        obj['color'] = color  # Set the color

        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'update': [obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        self._client.sync()
        return self._client.get_by_etag(response['id2etag'][obj['name']])

    def sorting(self, label: str, sort: int) -> dict:
        """
        Change the sort type of a tag. For batch changing sort types, see [update][managers.tags.TagsManager.update].

        Arguments:
            label: The label of the tag to be changed.
            sort: The new sort type specified by an integer 0-3. See [sort dictionary](tags.md#sort-dictionary).

        Returns:
            The updated tag dictionary object.

        Raises:
            TypeError: If `label` is not a string or if `sort` is not an int.
            ValueError: If the tag `label` does not exist.
            RuntimeError: If the updating was unsuccessful.

        !!! example "Changing the Sort Type"

            ```python
            # Lets assume that we have a tag named "Movies" with the sort type "project"
            changed_sort_type = client.tag.sorting("Movies", 1)  # Sort by 'dueDate'
            ```

            ??? success "Result"
                The updated task dictionary object is returned.

                ```python
                {'name': 'movies', 'label': 'Movies', 'sortOrder': 0, 'sortType': 'dueDate', 'color': '#134397', 'etag': 'fflj8iy0'}
                ```

                **Before**

                ![image](https://user-images.githubusercontent.com/56806733/104663625-3f241a80-5682-11eb-93a7-73d280c59b3e.png)

                **After**

                ![image](https://user-images.githubusercontent.com/56806733/104663663-5531db00-5682-11eb-9440-5673a70840b4.png)
        """
        if not isinstance(label, str) or not isinstance(sort, int):
            raise TypeError('Label Must Be A String and Sort Must Be An Int')

        # Get the object
        label = label.lower()
        obj = self._client.get_by_fields(name=label, search='tags')
        if not obj:
            raise ValueError(f"Tag '{label}' Does Not Exist To Update")
        sort = self._sort_string_value(sort)  # Get the sort string for the value

        obj['sortType'] = sort  # set the object field

        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'update': [obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        self._client.sync()
        return self._client.get_by_etag(response['id2etag'][obj['name']])

    def nesting(self, child: str, parent: str) -> dict:
        """
        Update tag nesting. Move an already created tag to be nested underneath a parent tag - or ungroup an already
        nested tag.

        !!! warning "Nesting Tags More Than One Level Does Not Work"
            !!! example

                === "Nesting Explanation"
                    ```md
                    Parent Tag -> Level Zero
                        Child Tag 1 -> Level One: This is the most nesting that is allowed by TickTick for tags.
                            Child Tag 2 -> Level Two: Not allowed
                    ```

        Arguments:
            child: Label of the tag to become the child
            parent: Label of the tag that will become the parent.

        Returns:
            The updated tag object dictionary.

        Raises:
            TypeError: If `child` and `parent` are not strings
            ValueError: If `child` does not exist to update.
            ValueError: If `parent` does not exist.
            RuntimeError: If setting the parent was unsuccessful.

        !!! example "Nesting"

            === "Nesting A Tag"
                To nest a tag underneath another tag, pass in the labels of the child and parent.

                ```python
                # Lets assume that we have a tag named "Movies"
                # We have another tag named "Hobbies" that we want to make the parent to "Movies"
                child = "Movies"
                parent = "Hobbies"
                nesting_update = client.tag.nesting(child, parent)
                ```

                ??? success "Result"
                    The updated child tag dictionary object is returned.

                    ```python
                    {'name': 'movies', 'label': 'Movies', 'sortOrder': 0, 'sortType': 'dueDate', 'color': '#134397', 'etag': 'ee34aft9', 'parent': 'hobbies'}
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104665300-da6abf00-5685-11eb-947f-889187cec008.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104665366-f706f700-5685-11eb-93eb-9316befec5fc.png)

            === "Changing The Parent Of An Already Nested Tag"
                If the tag is already nested, changing the parent is still no different.

                ```python
                # We have a tag named "Movies" that is already nested underneath "Hobbies"
                # We want to nest "Movies" underneath the tag "Fun" instead.
                child = "Movies"
                parent = "Fun"
                nesting_update = client.tag.nesting(child, parent)
                ```

                ??? success "Result"
                    The updated child tag dictionary object is returned.

                    ```python
                    {'name': 'movies', 'label': 'Movies', 'sortOrder': 0, 'sortType': 'dueDate', 'color': '#134397', 'etag': '91qpuq71', 'parent': 'fun'}
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104665599-ab088200-5686-11eb-8b36-5ee873289db7.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104665821-35e97c80-5687-11eb-8098-426816970f3e.png)

            === "Un-grouping A Child Tag"
                If the tag is nested and you want to ungroup it, pass in `None` for `parent`.

                ```python
                # We have a tag named "Movies" that is nested underneath "Fun"
                # We don't want to have "Movies" nested anymore.
                child = "Movies"
                parent = None
                nesting_update = client.tag.nesting(child, parent)
                ```

                ??? success "Result"
                    The updated child tag dictionary object is returned.

                    ```python
                    {'name': 'movies', 'label': 'Movies', 'sortOrder': 0, 'sortType': 'dueDate', 'color': '#134397', 'etag': 'jcoc94p6'}
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104666038-be681d00-5687-11eb-8490-83c370977267.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104666080-dcce1880-5687-11eb-9ca8-5abcdb4109ba.png)
        """
        if not isinstance(child, str):
            raise TypeError('Inputs Must Be Strings')

        if parent is not None:
            if not isinstance(parent, str):
                raise TypeError('Inputs Must Be Strings')

        # Get the object
        child = child.lower()
        obj = self._client.get_by_fields(name=child, search='tags')
        if not obj:
            raise ValueError(f"Tag '{child}' Does Not Exist To Update")

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

        url = self._client.BASE_URL + 'batch/tag'
        payload = {
            'update': [pobj, obj]
        }
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        self._client.sync()
        return self._client.get_by_etag(response['id2etag'][obj['name']], search='tags')

    def update(self, obj):
        """
        Generic update method. Supports single and batch tag update.

        !!! important
            Updating tag properties like `parent` and renaming tags must be completed through
            their respective class methods to work: [nesting][managers.tags.TagsManager.nesting]
            and [renaming][managers.tags.TagsManager.rename]. These updates use different
            endpoints to the traditional updating.

        !!! important
            You are able to batch update sorting and color of tag objects through this method. If you only
            need to update single tags, it is recommended you use the class methods: [sorting][managers.tags.TagsManager.sorting]
            and [color][managers.tags.TagsManager.color]

        !!! info
            More information on Tag Object properties [here](tags.md#example-ticktick-tag-dictionary)

        Arguments:
            obj (dict or list):
                **Single Tag (dict)**: The tag dictionary object to update.

                **Multiple Tags (list)**: The tag dictionaries to update in a list.

        Returns:
            dict or list:
            **Single Tag (dict)**: The updated tag dictionary object.

            **Multiple Tags (list)**: The updated tag dictionaries in a list.

        Raises:
            TypeError: If `obj` is not a dict or list.
            RuntimeError: If the updating was unsuccessful.

        !!! example "Updating Tags"
            === "Single Tag Update"
                Change a field directly in the task object then pass it to the method. See above
                for more information about what can actually be successfully changed through this method.

                ```python
                # Lets say we have a tag named "Fun" that we want to change the color of.
                # We can change the color by updating the field directly.
                fun_tag = client.get_by_fields(label='Fun', search='tags')  # Get the tag object
                new_color = '#d00000'
                fun_tag['color'] = new_color  # Change the color
                updated_fun_tag = client.tag.update(fun_tag)  # Pass the object to update.
                ```

                ??? success "Result"
                    The updated tag dictionary object is returned.

                    ```python
                    {'name': 'fun', 'label': 'Fun', 'sortOrder': 2199023255552, 'sortType': 'project', 'color': '#d00000', 'etag': 'i85c8ijo'}
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104669635-4aca0e00-568f-11eb-8bc6-9572a432b623.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104669824-ac8a7800-568f-11eb-93d6-ac40235bcd3f.png)

            === "Multiple Tag Update"
                Changing the fields is the same as with updating a single tag, except you will need
                to pass the objects in a list to the method.

                ```python
                # Lets update the colors for three tags: "Fun", "Hobbies", and "Productivity"
                fun_tag = client.get_by_fields(label="Fun", search='tags')
                hobbies_tag = client.get_by_fields(label="Hobbies", search='tags')
                productivity_tag = client.get_by_fields(label="Productivity", search='tags')
                fun_color_new = "#951a63"
                hobbies_color_new = "#0f8a1f"
                productivity_color_new = "#493293"
                # Change the fields directly
                fun_tag['color'] = fun_color_new
                hobbies_tag['color'] = hobbies_color_new
                productivity_tag['color'] = productivity_color_new
                # The objects must be passed in a list
                update_tag_list = [fun_tag, hobbies_tag, productivity_tag]
                updated_tags = client.tag.update(update_tag_list)
                ```

                ??? success "Result"
                    The updated task dictionary objects are returned in a list.

                    ```python
                    [{'name': 'fun', 'label': 'Fun', 'sortOrder': -1099511627776, 'sortType': 'project', 'color': '#951a63', 'etag': 'n543ajq2'},

                    {'name': 'hobbies', 'label': 'Hobbies', 'sortOrder': -549755813888, 'sortType': 'project', 'color': '#0f8a1f', 'etag': 'j4nspkg4'},

                    {'name': 'productivity', 'label': 'Productivity', 'sortOrder': 0, 'sortType': 'project', 'color': '#493293', 'etag': '34qz9bzq'}]
                    ```

                    **Before**

                    ![image](https://user-images.githubusercontent.com/56806733/104670498-cd070200-5690-11eb-9fdd-0287fa6c7e7b.png)

                    **After**

                    ![image](https://user-images.githubusercontent.com/56806733/104670531-dc864b00-5690-11eb-844a-899031335922.png)

        """
        batch = False  # Bool signifying batch create or not
        if isinstance(obj, list):
            # Batch tag creation triggered
            obj_list = obj  # Assuming all correct objects
            batch = True
        else:
            if not isinstance(obj, dict):
                raise TypeError('Required Positional Argument Must Be A Dict or List of Tag Objects')

        if not batch:
            obj_list = [obj]

        url = self._client.BASE_URL + 'batch/tag'
        payload = {'update': obj_list}
        response = self._client.http_post(url, json=payload, cookies=self._client.cookies, headers=self.headers)
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

    def merge(self, label, merged: str):
        """

        Merges the tasks of the passed tags into the argument `merged` and deletes all the tags except `merged`
        Args can be individual label strings, or a list of strings

        Arguments:
            label (str or list):
                **Single Tag (str)**: The label string of the tag to merge.

                **Multiple Tags (list)**: The label strings of the tags to merge in a list.
            merged: The label of the tag that will remain after the merge.

        Returns:
            dict: The tag dictionary object that remains after the merge.

        Raises:
            TypeError: If `merged` is not a str or if `label` is not a str or list.
            ValueError: If any of the labels do not exist.
            RuntimeError: If the merge could not be successfully completed.

        !!! example "Merging Tags"
            === "Merging Two Tags"
                Merging two tags requires the label of the tag that you want kept after the merge, and the
                label of the tag that will be merged.

                Lets assume that we have two tags: "Work" and "School". I want to merge the tag "School"
                into "Work". What should happen is that any tasks that are tagged "School", will be updated
                to have the tag "Work", and the "School" tag will be deleted.

                ```python
                merged_tags = client.tag.merge("School", "Work")
                ```

                ??? success "Result"
                    The tag that remains after the merge is returned.

                    ```python
                    {'name': 'work', 'label': 'Work', 'sortOrder': 2199023255552, 'sortType': 'project', 'color': '#3876E4', 'etag': 'eeh8zrup'}
                    ```

                    **Before**

                    "School" has two tasks that have it's tag.

                    ![image](https://user-images.githubusercontent.com/56806733/104680244-45c38980-56a4-11eb-968d-884160c77247.png)

                    "Work" has no tasks.

                    ![image](https://user-images.githubusercontent.com/56806733/104680366-90dd9c80-56a4-11eb-975f-5e769e9ea491.png)

                    **After**

                    "School" has been deleted. The tasks that used to be tagged with "School" are now
                    tagged with "Work".

                    ![image](https://user-images.githubusercontent.com/56806733/104680576-0c3f4e00-56a5-11eb-9536-ef3a7fcf20ec.png)

            === "Merging Three Or More Tags"
                Merging multiple tags into a single tag requires passing the labels of the tags to merge in a list.

                Lets assume that we have three tags: "Work", "School", and "Hobbies" . I want to merge the tag "School"
                and the tag "Hobbies" into "Work". What should happen is that any tasks that are tagged with "School" or "Hobbies", will be updated
                to have the tag "Work", and the "School" and "Hobbies" tags will be deleted.

                ```python
                merge_tags = ["School", "Hobbies"]
                result = client.tag.merge(merge_tags, "Work")
                ```

                ??? success "Result"
                    The tag that remains after the merge is returned.

                    ```python
                    {'name': 'work', 'label': 'Work', 'sortOrder': 2199023255552, 'sortType': 'project', 'color': '#3876E4', 'etag': 'ke23lp06'}
                    ```

                    **Before**

                    "School" has two tasks.

                    ![image](https://user-images.githubusercontent.com/56806733/104681135-7ad0db80-56a6-11eb-81dd-03e4a151cfd9.png)

                    "Hobbies" has two tasks.

                    ![image](https://user-images.githubusercontent.com/56806733/104681104-67257500-56a6-11eb-99b0-57bbb876a59e.png)

                    "Work" has one task.

                    ![image](https://user-images.githubusercontent.com/56806733/104681164-89b78e00-56a6-11eb-99a8-c85ef418d2a0.png)

                    **After**

                    "Work" has five tasks now, and the tags "School" and "Hobbies" have been deleted.

                    ![image](https://user-images.githubusercontent.com/56806733/104681239-b7043c00-56a6-11eb-9b45-5522b9c69cb0.png)
        """
        # Make sure merged is a string
        if not isinstance(merged, str):
            raise ValueError('Merged Must Be A String')

        # Make sure label is a string or list
        if not isinstance(label, str) and not isinstance(label, list):
            raise ValueError(f"Label must be a string or a list.")

        # Lowercase merged
        merged = merged.lower()
        # Make sure merged exists
        kept_obj = self._client.get_by_fields(name=merged, search='tags')
        if not kept_obj:
            raise ValueError(f"Kept Tag '{merged}' Does Not Exist To Merge")

        merge_queue = []
        # Verify all args are valid, and add them to a list
        if isinstance(label, str):
            string = label.lower()
            # Make sure it exists
            retrieved = self._client.get_by_fields(name=string, search='tags')
            if not retrieved:
                raise ValueError(f"Tag '{label}' Does Not Exist To Merge")
            merge_queue.append(retrieved)
        else:
            for item in label:  # Loop through the items in the list and check items are a string and exist
                # Make sure the item is a string
                if not isinstance(item, str):
                    raise ValueError(f"Item '{item}' Must Be A String")
                string = item.lower()
                # Make sure it exists
                found = self._client.get_by_fields(name=string, search='tags')
                if not found:
                    raise ValueError(f"Tag '{item}' Does Not Exist To Merge")
                merge_queue.append(found)

        for labels in merge_queue:
            # Merge
            url = self._client.BASE_URL + 'tag/merge'
            payload = {
                'name': labels['name'],
                'newName': kept_obj['name']
            }
            self._client.http_put(url, json=payload, cookies=self._client.cookies, headers=self.headers)
        self._client.sync()

        return kept_obj

    def delete(self, label):
        """
        Delete tag(s). Supports single tag deletion and "mock" batch tag deletion.

        !!! info
            Batch deleting for tags is not supported by TickTick. However, passing in
            a list of labels to delete will "mock" batch deleting - but individual requests
            will have to be made for each deletion.

        Arguments:
            label (str or list):
                **Single Tag (str)**: The label of the tag.

                **Multiple Tags (list)**: A list of tag label strings.

        Returns:
            dict or list:
            **Single Tag (dict)**: The dictionary object of the deleted tag.

            **Multiple Tags (list)**: The dictionary objects of the deleted tags in a list.

        Raises:
            TypeError: If `label` is not a string or list.
            ValueError: If a label does not exist.
            RuntimeError: If the tag could not be deleted successfully.

        !!! example "Tag Deletion"
            === "Single Tag Deletion"
                Deleting a single tag requires passing in the label string of the tag.

                ```python
                # Lets delete a tag named "Fun"
                delete_tag = client.tag.delete("Fun")
                ```

                ??? success "Result"
                    The dictionary object of the deleted tag returned.

                    ```python
                    {'name': 'fun', 'label': 'Fun', 'sortOrder': -3298534883328, 'sortType': 'project', 'color': '#A9949E', 'etag': '32balm5l'}
                    ```

                    **Before**

                    "Fun" Tag Exists

                    ![image](https://user-images.githubusercontent.com/56806733/104668024-2c164800-568c-11eb-853e-5b7eba1f4528.png)

                    **After**

                    "Fun" Tag Does Not Exist

                    ![image](https://user-images.githubusercontent.com/56806733/104667768-ac887900-568b-11eb-9bfb-597c752e4c3b.png)

            === "Multiple Tag Deletion"
                Deleting multiple tags requires passing the label strings of the tags in a list.

                ```python
                # Lets delete tags named "Fun", "Movies", and "Hobbies"
                delete_labels = ["Fun", "Movies", "Hobbies"]
                deleted_tags = client.tag.delete(delete_labels)
                ```

                ??? success "Result"

                    The dictionary object of the deleted tags returned in a list.

                    ```python
                    [{'name': 'fun', 'label': 'Fun', 'sortOrder': -3848290697216, 'sortType': 'project', 'color': '#FFD966', 'etag': '56aa6dva'},

                    {'name': 'movies', 'label': 'Movies', 'sortOrder': -2748779069440, 'sortType': 'dueDate', 'color': '#134397', 'etag': 's0czro3e'},

                    {'name': 'hobbies', 'label': 'Hobbies', 'sortOrder': -2199023255552, 'sortType': 'project', 'color': '#ABA6B5', 'etag': 'shu2xbvq'}]
                    ```

                    **Before**

                    All three tags exist.

                    ![image](https://user-images.githubusercontent.com/56806733/104668135-61bb3100-568c-11eb-8707-314deb42cd1d.png)

                    **After**

                    All three tags don't exist.

                    ![image](https://user-images.githubusercontent.com/56806733/104668185-7b5c7880-568c-11eb-8da0-aaee68d53500.png)

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
            response = self._client.http_delete(url, params=params, cookies=self._client.cookies, headers=self.headers)
            # Find the tag in the tags list and delete it, then return the deleted object
            objects.append(self._client.delete_from_local_state(search='tags', etag=tag_obj['etag']))
        self._client.sync()
        if len(objects) == 1:
            return objects[0]
        else:
            return objects
