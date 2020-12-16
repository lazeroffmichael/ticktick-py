"""Testing module for list related operations"""
import pytest


class TestLists:

    def test_create_list_success(self, client):
        """Tests creating a list and having it populate the class list dictionary"""
        name = 'Created List from Python'
        assert name in client.create_list(name)
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
        # Delete List
        client.delete_list(name)
        assert name not in client.lists

    def test_delete_list_fail(self, client):
        """Tests deletion will not occur if list name does not exist"""
        name = 'Yeah this project does not exist'
        with pytest.raises(KeyError):
            client.delete_list(name)
