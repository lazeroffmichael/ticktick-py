"""Testing module for list related operations"""
import pytest
import json


class TestLists:

    def test_create_list_success(self, client):
        """Tests creating a list and having it populate the class list dictionary"""
        name = 'Created List from Python'
        color = "#e070ff"
        task = client.list_create(name, color)
        get_object = client.get_by_id(task, search_key='lists')
        assert get_object['name'] == name
        client.list_delete(task)

    def test_update_success(self, client):
        """Tests updating an already existing list"""
        name = 'dnioanfknravndiojfioreajfior'
        task = client.list_create(name)
        get_object = client.get_by_id(task, search_key='lists')
        assert get_object['name'] == name
        update_name = 'jiocajiofhraoiv'
        get_object['name'] = update_name
        task2 = client.list_update(get_object['id'])
        get_object2 = client.get_by_id(task2, search_key='lists')
        assert get_object2['name'] == update_name
        assert get_object['id'] == get_object2['id']
        assert get_object['id'] == task2
        client.list_delete(task2)

    def test_create_list_type_note_success(self, client):
        """Tests creating a list with type note"""
        name = 'Test Note Type List'
        color = "#b20000"
        list_type = 'NOTE'
        task = client.list_create(name, color, list_type)
        my_object = client.get_by_id(task, search_key='lists')
        assert my_object
        client.list_delete(task)

    def test_create_list_duplicate_failure(self, client):
        """Tests no list creation if the same name already exists"""
        name = 'hhdfhaovnoanrvoi'
        duplicate_name = name
        task = client.list_create(name)
        with pytest.raises(ValueError):
            client.list_create(duplicate_name)
        client.list_delete(task)

    def test_delete_list_pass(self, client):
        """Tests list is properly deleted"""
        # Get id for 'Created List From Python'
        name = 'konvoanfopkndlkva'
        name2 = 'nkojvon;slkvn;sfnv'
        task1 = client.list_create(name)
        task2 = client.list_create(name2)
        # Delete List
        task1 = client.list_delete(task1)
        task2 = client.list_delete(task2)
        obj1 = client.get_by_id(task1)
        obj2 = client.get_by_id(task2)
        assert not obj1
        assert not obj2

    def test_delete_list_fail(self, client):
        """Tests deletion will not occur if list name does not exist"""
        list_id = 'Yeah this project does not exist'
        with pytest.raises(KeyError):
            client.list_delete(list_id)

    def test_wrong_list_type(self, client):
        """Tests wrong list type entered"""
        type = "Wrong list"
        with pytest.raises(ValueError):
            client.list_create('List Name', list_type=type)

    def test_wrong_hex_string_input(self, client):
        """Tests wrong input for hex color"""
        fail = "Yeah this not right"
        with pytest.raises(ValueError):
            client.list_create('', color_id=fail)

    def test_wrong_hex_string_input_2(self, client):
        """Tests another wrong input for hex color"""
        fail = "#DD730CDD"
        with pytest.raises(ValueError):
            client.list_create('', color_id=fail)

    def test_archive_list_success(self, client):
        # Create a test list
        name = 'Test Archive List'
        task = client.list_create(name)
        # Archive the test list
        archive = client.list_archive(task)
        for list_id in client.state['lists']:
            if task == list_id['id']:
                assert list_id['closed'] is True
        # Delete the test list
        client.list_delete(archive)

    def test_archive_list_failure(self, client):
        name = 'Fake Archive List'
        with pytest.raises(KeyError):
            client.list_archive(name)

    def test_create_list_folder(self, client):
        """List should be created and exist in client.list_groups"""
        name = 'Test Group List'
        response = client.list_create_folder(name)
        obj = client.get_by_id(response)
        assert obj

    def test_delete_list_folder(self, client):
        """Test Deletion of an already created folder"""
        name1 = 'Test Group List'
        folder_id = client.get_id(name=name1, search_key='list_folders')

        response = client.list_delete_folder(folder_id[0])
        obj = client.get_by_id(response)
        assert obj

    def test_delete_list_folder_fail(self, client):
        """Test failed deletion of a non existent folder"""
        folder_id = 'nope no folder with this id'
        with pytest.raises(KeyError):
            client.list_delete_folder(folder_id)

    def test_non_deletion_of_grouped_tasks(self, client):
        """Asserts that if a parent folder is deleted the lists are not deleted"""
        parent = client.list_create_folder('nfkladjf;fioaoivnm')
        child1 = client.list_create('nfkdsanc;ioajf', group_id=parent)
        child2 = client.list_create('nfkreanfviorenvklfs', group_id=parent)
        deleted_parent = client.list_delete_folder(parent)
        obj = client.get_by_id(child1)
        obj2 = client.get_by_id(child2)
        assert obj and obj2
        client.list_delete(obj['id'])
        client.list_delete(obj2['id'])




