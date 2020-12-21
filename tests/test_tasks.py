"""
Testing module for task functionality
"""
import pytest
from datetime import datetime


class TestTasks:

    def test_create_task_just_name(self, client):
        name = 'iovhaoh48hh94u90q09h4hgihfkanvl'
        task = client.task_create(name)
        for tk in client.state['tasks']:
            if tk['id'] == task:
                created = True

        assert created

    def test_delete_task(self, client):
        name = 'iovhaoh48hh94u90q09h4hgihfkanvl'
        # Find the task
        task_find = client.get_id(title=name)
        delete = client.task_delete(task_find[0])
        # Make sure the id doesn't exist
        make_sure = client.get_by_id(delete)
        assert not make_sure

    def test_create_task_no_name(self, client):
        """Should raise exception"""
        with pytest.raises(Exception):
            client.task_create()

    def test_create_task_all_fields_no_parent(self, client):
        name = 'giorahgoi4hginfkvnczlmvnkf'
        date = datetime(2098, 12, 12)
        priority = 3
        # Lets create a project for it to go in other than inbox
        project = client.list_create('kanoiejfoaqjkndlkvn,cnv')
        # Lets add a tag
        tag = ['459043u09']
        # Lets add a description
        description = "This is a created task"
        task_create = client.task_create(name,
                                         date=date,
                                         priority=priority,
                                         project_id=project,
                                         content=description)
        # Find the task and make sure all fields match
        for task in client.state['tasks']:
            if (task['title'] == name and task['dueDate'] == date and
                    task['priority'] == priority and task['id'] == task_create and
                    task['projectId'] == project and task['content'] == description):
                match = True

        assert match
