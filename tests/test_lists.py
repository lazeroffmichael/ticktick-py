"""Testing module for list related operations"""
import pytest
import json


class TestLists:

    def test_create_list_success(self, client):
        """Tests creating a list and having it populate the class list dictionary"""
        name = 'Created List from Python'
        color = "#e070ff"
        task = client.list_create(name, color)
        exists = False
        for list_num in client.state['lists']:
            if task == list_num['id']:
                exists = True
        assert exists

    def test_create_list_type_note_success(self, client):
        """Tests creating a list with type note"""
        name = 'Test Note Type List'
        color = "#b20000"
        list_type = 'NOTE'
        task = client.list_create(name, color, list_type)
        exists = False
        for list_num in client.state['lists']:
            if task == list_num['id'] and list_type == 'NOTE':
                exists = True
        assert exists

    def test_create_list_duplicate_failure(self, client):
        """Tests no list creation if the same name already exists"""
        duplicate_name = 'Created List from Python'
        with pytest.raises(ValueError):
            client.list_create(duplicate_name)

    def test_delete_list_pass(self, client):
        """Tests list is properly deleted"""
        # Get id for 'Created List From Python'
        name = 'Created List from Python'
        name2 = 'Test Note Type List'
        id1 = 0
        id2 = 0
        for id_check in client.state['lists']:
            if name == id_check['name']:
                id1 = id_check['id']
            if name2 == id_check['name']:
                id2 = id_check['id']
        # Delete List
        task = client.list_delete(id1)
        task2 = client.list_delete(id2)
        exists = False
        exists2 = False
        for list_num in client.state['lists']:
            if task == list_num['id']:
                exists = True
            if task2 == list_num['id']:
                exists2 = True
        assert not exists
        assert not exists2

    def test_delete_list_fail(self, client):
        """Tests deletion will not occur if list name does not exist"""
        name = 'Yeah this project does not exist'
        with pytest.raises(KeyError):
            client.list_delete(name)

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
        exists = False
        for list_id in client.state['list_folders']:
            if response == list_id['id']:
                exists = True
        assert exists


