"""
Testing module for task functionality
"""
import pytest
import uuid
import datetime
from ticktick.helpers.time_methods import convert_iso_to_tick_tick_format


def test_create_task_just_title(client):
    """Tests task creation with just title"""
    title = str(uuid.uuid4())
    task = client.task.create(title)
    assert task
    assert task['projectId'] == client.state['inbox_id']
    # Tests deletion
    deleted = client.task.delete(task['id'])
    assert deleted
    found = client.get_by_id(task['id'])
    assert not found
    assert deleted not in client.state['tasks']


def test_create_task_title_not_string(client):
    """Tests a value error is raised if the title is not a string"""
    with pytest.raises(ValueError):
        client.task.create(1234)
    with pytest.raises(ValueError):
        client.task.create(uuid.uuid4())


def test_start_date_after_end_date(client):
    """Tests an exception is raised if start date is after end date"""
    start = datetime.datetime(2022, 1, 5)
    end = datetime.datetime(2022, 1, 2)
    with pytest.raises(ValueError):
        client.task.create('hello', start_date=start, end_date=end)


def test_create_task_start_date_with_time_zone(client):
    """Tests passing a timezone different to the account"""
    start = datetime.datetime(2022, 12, 31, 14, 30)
    task = client.task.create('hello', start_date=start, time_zone='America/Louisville')
    #  This timezone is GMT - 5
    assert not task['isAllDay']
    assert task['timeZone'] == 'America/Louisville'
    assert task['startDate'] == '2022-12-31T19:30:00.000+0000'
    assert task['dueDate'] == '2022-12-31T19:30:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_start_date_with_time_zone_2(client):
    """Tests another timezone"""
    tz = 'Pacific/Fakaofo'
    start = datetime.datetime(2022, 12, 31, 14, 30)
    task = client.task.create('hello', start_date=start, time_zone=tz)
    assert not task['isAllDay']
    assert task['timeZone'] == tz
    assert task['startDate'] == '2022-12-31T01:30:00.000+0000'
    assert task['dueDate'] == '2022-12-31T01:30:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_with_no_time_zone_given(client):
    """Tests creation with the timezone found in the profile"""
    # If your timezone is not US Pacific - this test will fail
    start = datetime.datetime(2022, 12, 31)
    task = client.task.create('hello', start_date=start)
    assert task['isAllDay']
    assert task['startDate'] == '2022-12-31T08:00:00.000+0000'
    assert task['dueDate'] == '2022-12-31T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_start_date_only_all_day(client):
    """Tests using only a start date that is all day"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2022, 12, 31)
    task = client.task.create('hello', start_date=start, time_zone=tz)
    assert task['isAllDay']
    assert task['startDate'] == '2022-12-31T08:00:00.000+0000'
    assert task['dueDate'] == '2022-12-31T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_start_date_only_not_all_day(client):
    """Tests using a start date that is not all day"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2022, 12, 31, 14, 30, 45, 32)
    task = client.task.create('hello', start_date=start, time_zone=tz)
    assert not task['isAllDay']
    assert task['startDate'] == '2022-12-31T22:30:45.000+0000'
    assert task['dueDate'] == '2022-12-31T22:30:45.000+0000'
    client.task.delete(task['id'])


def test_create_task_end_date_only_all_day(client):
    """Tests using an end  date that is all day"""
    tz = 'America/Los_Angeles'
    end = datetime.datetime(2022, 12, 31)
    task = client.task.create('hello', end_date=end, time_zone=tz)
    assert task['isAllDay']
    assert task['startDate'] == '2022-12-31T08:00:00.000+0000'
    assert task['dueDate'] == '2022-12-31T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_end_date_only_not_all_day(client):
    """Tests creating a task using only end_date"""
    tz = 'America/Los_Angeles'
    end = datetime.datetime(2022, 12, 31, 14, 30, 45, 32)
    task = client.task.create('hello', end_date=end, time_zone=tz)
    assert not task['isAllDay']
    assert task['startDate'] == '2022-12-31T22:30:45.000+0000'
    assert task['dueDate'] == '2022-12-31T22:30:45.000+0000'
    client.task.delete(task['id'])


def test_create_task_both_dates_all_day(client):
    """Tests creating a task using both start and end dates"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2023, 1, 4)
    end = datetime.datetime(2023, 1, 7)
    task = client.task.create('hello', start_date=start, end_date=end, time_zone=tz)
    assert task['isAllDay']
    assert task['startDate'] == '2023-01-04T08:00:00.000+0000'
    assert task['dueDate'] == '2023-01-08T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_both_dates_all_day_last_day_of_month(client):
    """Tests creating an all day task spanning multiple days on the last day of month"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2023, 1, 28)
    end = datetime.datetime(2023, 1, 31)
    task = client.task.create('hello', start_date=start, end_date=end, time_zone=tz)
    assert task['isAllDay']
    assert task['startDate'] == '2023-01-28T08:00:00.000+0000'
    assert task['dueDate'] == '2023-02-01T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_both_dates_all_day_last_day_of_year(client):
    """Tests creating an all day task spanning multiple days on the last day of the year"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2023, 12, 28)
    end = datetime.datetime(2023, 12, 31)
    task = client.task.create('hello', start_date=start, end_date=end, time_zone=tz)
    assert task['isAllDay']
    assert task['startDate'] == '2023-12-28T08:00:00.000+0000'
    assert task['dueDate'] == '2024-01-01T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_both_dates_not_all_day(client):
    """Tests creating a task for a duration of time"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2023, 1, 4, 14, 30)
    end = datetime.datetime(2023, 12, 31, 8, 30)
    task = client.task.create('hello', start_date=start, end_date=end, time_zone=tz)
    assert not task['isAllDay']
    assert task['startDate'] == '2023-01-04T22:30:00.000+0000'
    assert task['dueDate'] == '2023-12-31T16:30:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_both_dates_not_all_day_different_tz(client):
    """Tests creating a duration task for a different timezone"""
    tz = 'Kwajalein'
    start = datetime.datetime(2023, 1, 4, 14, 30)
    end = datetime.datetime(2023, 12, 31, 8, 30)
    task = client.task.create('hello', start_date=start, end_date=end, time_zone=tz)
    assert not task['isAllDay']
    assert task['startDate'] == '2023-01-04T02:30:00.000+0000'
    assert task['dueDate'] == '2023-12-30T20:30:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_not_datetime_dates(client):
    with pytest.raises(ValueError):
        task1 = client.task.create('hello', start_date='yeah this not a datetime')
    with pytest.raises(ValueError):
        task2 = client.task.create('hello', end_date='yeah this not a datetime')
    with pytest.raises(ValueError):
        task3 = client.task.create('hello', start_date='nope', end_date='yeah this not a datetime')


def test_create_task_title_and_priority_fail(client):
    """Tests task creation for title and priority"""
    title = str(uuid.uuid4())
    priority = 3  # Medium
    with pytest.raises(Exception):
        client.task.create(title, priority=priority)


def test_create_task_title_and_priority_string_fail(client):
    """Tests task creation fail with a string input"""
    title = str(uuid.uuid4())
    priority = 'nope'
    with pytest.raises(ValueError):
        client.task.create(title, priority=priority)


def test_create_task_priority_normal_pass(client):
    """Tests task creation with priority for normal priority strings"""
    priorities = {'none': 0, 'low': 1, 'medium': 3, 'high': 5}
    for task in priorities:
        created = client.task.create(task_name=str(uuid.uuid4()), priority=task)
        assert created['priority'] == priorities[task]
        client.task.delete(created['id'])


def test_create_task_priority_different_cases(client):
    """Tests task creation with priority for different case priority strings"""
    priorities = {'none': 0, 'low': 1, 'medium': 3, 'high': 5}
    cases = {'NoNe', 'NONE', 'LoW', 'MeDIUM', 'HIGH'}
    for task in cases:
        created = client.task.create(task_name=str(uuid.uuid4()), priority=task)
        assert created['priority'] == priorities[task.lower()]
        client.task.delete(created['id'])


def test_create_task_different_list(client):
    """Tests task creation with set project id"""
    list_title = str(uuid.uuid4())
    list_ = client.list.create(list_title)  # Create list
    task_title = str(uuid.uuid4())
    task = client.task.create(task_title, list_id=list_['id'], priority='medium')  # Create task in list
    assert task
    assert task['projectId'] == list_['id']  # Assert list id property matches
    client.list.delete(list_['id'])  # Deleting the list deletes the task


def test_create_task_different_list_fail(client):
    """Tests exception thrown if list doesn't exist"""
    with pytest.raises(ValueError):
        client.task.create(str(uuid.uuid4()), list_id=str(uuid.uuid4()))


def test_create_task_with_explicit_inbox(client):
    """Tests successful creation if inbox id is passed"""
    task = client.task.create(str(uuid.uuid4()), list_id=client.state['inbox_id'])
    assert task
    assert task['projectId'] == client.state['inbox_id']
    client.task.delete(task['id'])


def test_create_task_tags_fail(client):
    """Tests passing something other than a list as tags"""
    tag = 0
    name = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.task.create(name, tags=tag)


def test_create_task_tags_fail_not_strings_in_list(client):
    """Tests passing items that are not strings in the list"""
    tag = ['yup', 'this one is valid', 5]
    name = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.task.create(name, tags=tag)


def test_create_task_tags_fail_dictionary(client):
    """Tests passing tags as a dictionary and raising exception"""
    tag = {'yup', 'this one is valid', 5}
    name = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.task.create(name, tags=tag)


def test_create_task_with_tag_single_string(client):
    """Tests creating a task with a single tag as a string"""
    tag = str(uuid.uuid4())
    name = str(uuid.uuid4())
    task = client.task.create(name, tags=tag)
    assert task['tags'] == [tag]
    client.task.delete(task['id'])
    client.tag.delete(tag)


def test_create_task_with_tag_spaces(client):
    """Tests creating a tag with spaces in a task"""
    tag = 'This is a tag with spaces'
    name = str(uuid.uuid4())
    task = client.task.create(name, tags=tag)
    assert task['tags'] == [tag.lower()]
    client.task.delete(task['id'])
    client.tag.delete(tag.lower())


def test_create_task_with_tags(client):
    """Tests creating a list with tags"""
    tag1 = str(uuid.uuid4())
    tag2 = str(uuid.uuid4())
    tag = [tag1, tag2]
    title = str(uuid.uuid4())
    task_obj = client.task.create(title, tags=tag)
    assert task_obj
    for task in task_obj['tags']:
        assert task in tag
    # Delete the task
    client.task.delete(task_obj['id'])
    # Delete the tags
    # Find the tag
    client.tag.delete(tag1)
    client.tag.delete(tag2)


def test_create_task_with_content(client):
    """Tests creating a task with content"""
    content = 'Yeah this some content right here'
    name = str(uuid.uuid4())
    obj = client.task.create(name, content=content)
    assert obj['content'] == content
    client.task.delete(obj['id'])


def test_create_task_with_date_all_day(client):
    """Tests creating a task with a date"""
    date = datetime.datetime(2022, 12, 31)
    task = client.task.create(str(uuid.uuid4()), start_date=date)
    assert task['isAllDay']
    client.task.delete(task['id'])


def test_create_task_with_specific_time(client):
    """Tests creating a task with a specific time"""
    date = datetime.datetime(2022, 12, 31, 14, 30)  # 2:30 PM
    task = client.task.create(str(uuid.uuid4()), start_date=date)
    assert not task['isAllDay']
    client.task.delete(task['id'])


def test_create_task_with_start_and_end(client):
    assert 1 == 0


def test_get_from_list(client):
    """Tests getting all the tasks from a list"""
    # Make a fake list
    fake_list_id = str(uuid.uuid4())
    fake_list = {'id': fake_list_id}
    client.state['lists'].append(fake_list)  # Append the fake list
    # Make some fake tasks
    task1_title = str(uuid.uuid4())
    task2_title = str(uuid.uuid4())
    task1 = {'projectId': fake_list_id, 'title': task1_title}
    task2 = {'projectId': fake_list_id, 'title': task2_title}
    # Append fake tasks
    client.state['tasks'].append(task1)
    client.state['tasks'].append(task2)
    tasks = client.task.get_from_list(fake_list_id)
    assert task1 in tasks and task2 in tasks
    # Delete the fake objects
    client.delete_from_local_state(id=fake_list_id, search='lists')
    client.delete_from_local_state(title=task1_title, search='tasks')
    client.delete_from_local_state(title=task2_title, search='tasks')


def test_get_from_list_error(client):
    """Tests exception raised if list doesn't exist"""
    with pytest.raises(ValueError):
        client.task.get_from_list(str(uuid.uuid4()))


def test_move_list_pass(client):
    """Tests moving all the tasks from one list into a new list"""
    list1_name = 'list 1'
    list2_name = 'list 2'
    list1 = client.list.create(list1_name)
    list2 = client.list.create(list2_name)
    # Tasks will be created in list2
    task1 = client.task.create(str(uuid.uuid4()), list_id=list2['id'])
    task2 = client.task.create(str(uuid.uuid4()), list_id=list2['id'])
    # Move the tasks: list2 -> list1
    move = client.task.move_lists(list2['id'], list1['id'])
    list2_tasks = client.task.get_from_list(list2['id'])
    assert not list2_tasks  # Assert that all the tasks in list 2 are gone
    list1_tasks = client.task.get_from_list(list1['id'])
    for task in list1_tasks:
        assert task['projectId'] == list1['id'] and task['projectId'] == move['id']
    # Deleting the lists will delete the tasks
    client.list.delete(list1['id'])
    client.list.delete(list2['id'])


def test_move_from_inbox(client):
    """Tests moving the items from the inbox to another list and back"""
    task = client.task.create(str(uuid.uuid4()))
    list_ = client.list.create(str(uuid.uuid4()))
    move = client.task.move_lists(client.state['inbox_id'], list_['id'])
    inbox_tasks = client.task.get_from_list(client.state['inbox_id'])
    assert not inbox_tasks  # Assert that nothing in inbox
    list_tasks = client.task.get_from_list(list_['id'])
    for task in list_tasks:
        assert task['projectId'] == list_['id']
    # Move back
    move_back = client.task.move_lists(list_['id'], client.state['inbox_id'])
    list_tasks = client.task.get_from_list(list_['id'])
    assert not list_tasks  # Make sure that nothing in new list
    inbox_tasks = client.task.get_from_list(client.state['inbox_id'])
    for task1 in inbox_tasks:
        assert task1['projectId'] == client.state['inbox_id']
    # Delete the created task
    client.task.delete(task['id'])
    client.list.delete(list_['id'])
