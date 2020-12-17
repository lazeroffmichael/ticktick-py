"""Testing module for list related operations"""
import pytest


class TestLists:

    def test_create_list_success(self, client):
        """Tests creating a list and having it populate the class list dictionary"""
        name = 'Created List from Python'
        color = "#e070ff"
        assert name in client.create_list(name, color)
        assert name in client.lists

    def test_create_list_type_note_success(self, client):
        """Tests creating a list with type note"""
        name = 'Test Note Type List'
        color = "#b20000"
        assert name in client.create_list(name, color)
        assert name in client.lists

    def test_create_list_duplicate_failure(self, client):
        """Tests no list creation if the same name already exists"""
        duplicate_name = 'Created List from Python'
        with pytest.raises(ValueError):
            client.create_list(duplicate_name)

    def test_get_lists(self, client):
        """Tests getting lists works"""
        returned_list = client.get_lists()
        assert returned_list != ''

    def test_get_lists_id_and_name(self, client):
        """Tests proper parsing of the class.list dictionary"""
        name = 'Created List from Python'
        returned_dictionary = client.get_lists_name_and_id()
        assert name in returned_dictionary

    def test_delete_list_pass(self, client):
        """Tests list is properly deleted"""
        # Get id for 'Created List From Python'
        name = 'Created List from Python'
        name2 = 'Test Note Type List'
        # Delete List
        client.delete_list(name)
        client.delete_list(name2)
        assert name not in client.lists
        assert name2 not in client.lists

    def test_delete_list_fail(self, client):
        """Tests deletion will not occur if list name does not exist"""
        name = 'Yeah this project does not exist'
        with pytest.raises(KeyError):
            client.delete_list(name)

    def test_wrong_list_type(self, client):
        """Tests wrong list type entered"""
        type = "Wrong list"
        with pytest.raises(ValueError):
            client.create_list('List Name', list_type=type)

    def test_wrong_hex_string_input(self, client):
        """Tests wrong input for hex color"""
        fail = "Yeah this not right"
        with pytest.raises(ValueError):
            client.create_list('', color_id=fail)

    def test_wrong_hex_string_input_2(self, client):
        """Tests another wrong input for hex color"""
        fail = "#DD730CDD"
        with pytest.raises(ValueError):
            client.create_list('', color_id=fail)

    def test_archive_list_success(self, client):
        # Create a test list
        name = 'Test Archive List'
        client.create_list(name)
        # Archive the test list
        client.archive_list(name)

        pass

    def test_archive_list_failure(self, client):
        pass
