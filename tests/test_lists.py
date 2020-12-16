import pytest


class TestLists:

    def test_get_lists(self, client):
        returned_list = client.get_lists()
        assert returned_list != ''

    def test_create_list_success(self, client):
        name = 'Created List from Python'
        assert client.create_list(name) != ''
        assert name in client.lists

    def test_create_list_duplicate_failure(self, client):
        duplicate_name = 'Created List from Python'
        with pytest.raises(ValueError):
            client.create_list(duplicate_name)

    def test_get_lists_id_and_name(self, client):
        name = 'Created List from Python'
        returned_dictionary = client.get_lists_name_and_id()
        assert name in returned_dictionary

    def test_delete_list(self, client):
        # Get id for 'Created List From Python'
        name = 'Created List from Python'
        main_dict = client.get_lists_name_and_id()
        project_id = main_dict[name]
        # Delete List
        client.delete_list(project_id)
        main_dict = client.get_lists_name_and_id()
        assert name not in main_dict
