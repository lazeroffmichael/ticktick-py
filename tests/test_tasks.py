"""
Testing module for task functionality
"""
import pytest
import uuid
import datetime
from ticktick.helpers.time_methods import convert_iso_to_tick_tick_format


def test_time_checks_start_after_end(client):
    """Tests exception raised if start date after end date"""
    start = datetime.datetime(2022, 1, 5)
    end = datetime.datetime(2022, 1, 2)
    with pytest.raises(ValueError):
        client.task._time_checks(start_date=start, end_date=end)


def test_invalid_time_zone(client):
    """Tests exception raised if time zone not valid"""
    tz = 'Yeah this not right'
    with pytest.raises(ValueError):
        client.task._time_checks(time_zone=tz)


def test_time_checks_proper_parse_start(client):
    """Tests proper parsing of date with only start_date"""
    start = datetime.datetime(2022, 1, 5)
    dates = client.task._time_checks(start)
    assert dates['startDate'] == convert_iso_to_tick_tick_format(start, tz=client.time_zone)
    assert dates['dueDate'] == convert_iso_to_tick_tick_format(start, tz=client.time_zone)
    assert dates['isAllDay']


def test_time_checks_proper_parse_end(client):
    end = datetime.datetime(2022, 1, 5)
    dates = client.task._time_checks(end)
    assert dates['startDate'] == convert_iso_to_tick_tick_format(end, tz=client.time_zone)
    assert dates['dueDate'] == convert_iso_to_tick_tick_format(end, tz=client.time_zone)
    assert dates['isAllDay']


def test_time_checks_proper_parse_start_not_all_day(client):
    """Tests proper date parse of not all day"""
    start = datetime.datetime(2022, 1, 5, 14, 56, 34)
    dates = client.task._time_checks(start)
    assert dates['startDate'] == convert_iso_to_tick_tick_format(start, tz=client.time_zone)
    assert dates['dueDate'] == convert_iso_to_tick_tick_format(start, tz=client.time_zone)
    assert not dates['isAllDay']


def test_time_checks_proper_parse_end_not_all_day(client):
    end = datetime.datetime(2022, 1, 5, 16, 56, 45)
    dates = client.task._time_checks(end)
    assert dates['startDate'] == convert_iso_to_tick_tick_format(end, tz=client.time_zone)
    assert dates['dueDate'] == convert_iso_to_tick_tick_format(end, tz=client.time_zone)
    assert not dates['isAllDay']


def test_time_all_day_range(client):
    start = datetime.datetime(2022, 1, 5)
    end = datetime.datetime(2022, 1, 8)
    expected = datetime.datetime(2022, 1, 9)
    dates = client.task._time_checks(start, end)
    assert dates['startDate'] == convert_iso_to_tick_tick_format(start, tz=client.time_zone)
    assert dates['dueDate'] == convert_iso_to_tick_tick_format(expected, tz=client.time_zone)
    assert dates['isAllDay']


def test_time_all_day_range_end_of_month(client):
    start = datetime.datetime(2022, 1, 28)
    end = datetime.datetime(2022, 1, 31)
    expected = datetime.datetime(2022, 2, 1)
    dates = client.task._time_checks(start, end)
    assert dates['startDate'] == convert_iso_to_tick_tick_format(start, tz=client.time_zone)
    assert dates['dueDate'] == convert_iso_to_tick_tick_format(expected, tz=client.time_zone)
    assert dates['isAllDay']


def test_time_all_day_range_end_of_year(client):
    start = datetime.datetime(2022, 12, 28)
    end = datetime.datetime(2022, 12, 31)
    expected = datetime.datetime(2023, 1, 1)
    dates = client.task._time_checks(start, end)
    assert dates['startDate'] == convert_iso_to_tick_tick_format(start, tz=client.time_zone)
    assert dates['dueDate'] == convert_iso_to_tick_tick_format(expected, tz=client.time_zone)
    assert dates['isAllDay']


def test_task_field_checks_invalid_name(client):
    """Invalid name test"""
    name = 56
    with pytest.raises(TypeError):
        client.task._task_field_checks(task_name=name)


def test_task_field_checks_invalid_priority(client):
    """Invalid Priority test"""
    priority = 45
    priority1 = 'Yeah this not right'
    with pytest.raises(TypeError):
        client.task._task_field_checks(task_name='', priority=priority)
    with pytest.raises(TypeError):
        client.task._task_field_checks(task_name='', priority=priority1)


def test_task_field_checks_invalid_project(client):
    """Invalid list id"""
    with pytest.raises(ValueError):
        client.task._task_field_checks(task_name='', project='yeah no')


def test_task_fields_checks_invalid_tags(client):
    """Tests invalid tags"""
    tag1 = 45
    with pytest.raises(ValueError):
        client.task._task_field_checks(task_name='', tags=tag1)
    tag2 = {67}
    with pytest.raises(ValueError):
        client.task._task_field_checks(task_name='', tags=tag2)
    tag3 = [3]
    with pytest.raises(ValueError):
        client.task._task_field_checks(task_name='', tags=tag3)


def test_task_fields_content_invalid(client):
    """Tests invalid content"""
    content = {67}
    with pytest.raises(ValueError):
        client.task._task_field_checks(task_name='', content=content)


def test_task_fields_proper_return(client):
    """Tests proper return of checked values"""
    task_name = 'hello'
    priority = 'low'
    list_id = client.inbox_id
    tags = ['yup']
    content = 'yessir'
    start = datetime.datetime(2022, 12, 28)
    end = datetime.datetime(2022, 12, 31)
    expected = datetime.datetime(2023, 1, 1)
    items = client.task._task_field_checks(task_name=task_name,
                                           priority=priority,
                                           project=list_id,
                                           tags=tags,
                                           content=content,
                                           start_date=start,
                                           end_date=end)
    assert items['title'] == task_name
    assert items['priority'] == client.task.PRIORITY_DICTIONARY[priority]
    assert items['projectId'] == list_id
    assert items['tags'] == tags
    assert items['content'] == content
    assert items['startDate'] == convert_iso_to_tick_tick_format(start, tz=client.time_zone)
    assert items['dueDate'] == convert_iso_to_tick_tick_format(expected, tz=client.time_zone)
    assert items['isAllDay']


def test_builder(client):
    task_name = 'hello'
    priority = 'low'
    list_id = client.inbox_id
    tags = ['yup']
    content = 'yessir'
    start = datetime.datetime(2022, 12, 28)
    end = datetime.datetime(2022, 12, 31)
    expected = datetime.datetime(2023, 1, 1)
    items = client.task.builder(name=task_name,
                                priority=priority,
                                project=list_id,
                                tags=tags,
                                content=content,
                                start=start,
                                end=end)
    assert items['title'] == task_name
    assert items['priority'] == client.task.PRIORITY_DICTIONARY[priority]
    assert items['projectId'] == list_id
    assert items['tags'] == tags
    assert items['content'] == content
    assert items['startDate'] == convert_iso_to_tick_tick_format(start, tz=client.time_zone)
    assert items['dueDate'] == convert_iso_to_tick_tick_format(expected, tz=client.time_zone)
    assert items['isAllDay']


def test_create_batch_raise_not_list(client):
    obj = {'title': 'yum'}
    with pytest.raises(TypeError):
        client.task.create(obj)
    obj = {}
    with pytest.raises(TypeError):
        client.task.create(obj)


def test_create_batch_success(client):
    #TODO Fix
    name = 'Test Create Batch'
    start_date = datetime.datetime(2022, 1, 28)
    end_date = datetime.datetime(2022, 1, 31)
    priority = 'HigH'
    tags = [str(uuid.uuid4()).upper()]
    content = 'yessir'
    task1 = client.task.builder(name=name,
                                start=start_date,
                                end=end_date,
                                priority=priority,
                                tags=tags,
                                content=content)
    name2 = 'Test Create Batch 2'
    start_date2 = datetime.datetime(2022, 12, 28)
    end_date2 = datetime.datetime(2022, 12, 31)
    priority2 = 'Medium'
    tags2 = [str(uuid.uuid4())]
    content2 = 'yessir'
    task2 = client.task.builder(name=name2,
                                start=start_date2,
                                end=end_date2,
                                priority=priority2,
                                tags=tags2,
                                content=content2)

    the_batch = [task1, task2]

    tasks = client.task.create(the_batch)
    deleted = client.task.delete([tasks[0]['id'], tasks[1]['id']])
    tags = client.tag.delete([deleted[0]['tags'][0], deleted[1]['tags'][0]])


def test_create_task_just_title(client):
    """Tests task creation with just title"""
    title = str(uuid.uuid4())
    task = client.task.create(title)
    assert task
    assert task['projectId'] == client.inbox_id
    # Tests deletion
    deleted = client.task.delete(task['id'])
    assert deleted
    found = client.get_by_id(task['id'])
    assert not found
    assert deleted not in client.state['tasks']


def test_create_task_title_not_string(client):
    #TODO Fix
    """Tests a value error is raised if the title is not a string"""
    with pytest.raises(TypeError):
        client.task.create(1234)
    with pytest.raises(TypeError):
        client.task.create(uuid.uuid4())


def test_start_date_after_end_date(client):
    """Tests an exception is raised if start date is after end date"""
    start = datetime.datetime(2022, 1, 5)
    end = datetime.datetime(2022, 1, 2)
    with pytest.raises(ValueError):
        client.task.create('hello', start=start, end=end)


def test_create_task_start_date_with_time_zone(client):
    """Tests passing a timezone different to the account"""
    start = datetime.datetime(2022, 12, 31, 14, 30)
    task = client.task.create('hello', start=start, tz='America/Louisville')
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
    task = client.task.create('hello', start=start, tz=tz)
    assert not task['isAllDay']
    assert task['timeZone'] == tz
    assert task['startDate'] == '2022-12-31T01:30:00.000+0000'
    assert task['dueDate'] == '2022-12-31T01:30:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_with_no_time_zone_given(client):
    """Tests creation with the timezone found in the profile"""
    # If your timezone is not US Pacific - this test will fail
    start = datetime.datetime(2022, 12, 31)
    task = client.task.create('hello', start=start)
    assert task['isAllDay']
    assert task['startDate'] == '2022-12-31T08:00:00.000+0000'
    assert task['dueDate'] == '2022-12-31T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_start_date_only_all_day(client):
    """Tests using only a start date that is all day"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2022, 12, 31)
    task = client.task.create('hello', start=start, tz=tz)
    assert task['isAllDay']
    assert task['startDate'] == '2022-12-31T08:00:00.000+0000'
    assert task['dueDate'] == '2022-12-31T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_start_date_only_not_all_day(client):
    """Tests using a start date that is not all day"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2022, 12, 31, 14, 30, 45, 32)
    task = client.task.create('hello', start=start, tz=tz)
    assert not task['isAllDay']
    assert task['startDate'] == '2022-12-31T22:30:45.000+0000'
    assert task['dueDate'] == '2022-12-31T22:30:45.000+0000'
    client.task.delete(task['id'])


def test_create_task_end_date_only_all_day(client):
    """Tests using an end  date that is all day"""
    tz = 'America/Los_Angeles'
    end = datetime.datetime(2022, 12, 31)
    task = client.task.create('hello', end=end, tz=tz)
    assert task['isAllDay']
    assert task['startDate'] == '2022-12-31T08:00:00.000+0000'
    assert task['dueDate'] == '2022-12-31T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_end_date_only_not_all_day(client):
    """Tests creating a task using only end_date"""
    tz = 'America/Los_Angeles'
    end = datetime.datetime(2022, 12, 31, 14, 30, 45, 32)
    task = client.task.create('hello', end=end, tz=tz)
    assert not task['isAllDay']
    assert task['startDate'] == '2022-12-31T22:30:45.000+0000'
    assert task['dueDate'] == '2022-12-31T22:30:45.000+0000'
    client.task.delete(task['id'])


def test_create_task_both_dates_all_day(client):
    """Tests creating a task using both start and end dates"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2023, 1, 4)
    end = datetime.datetime(2023, 1, 7)
    task = client.task.create('hello', start=start, end=end, tz=tz)
    assert task['isAllDay']
    assert task['startDate'] == '2023-01-04T08:00:00.000+0000'
    assert task['dueDate'] == '2023-01-08T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_both_dates_all_day_last_day_of_month(client):
    """Tests creating an all day task spanning multiple days on the last day of month"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2023, 1, 28)
    end = datetime.datetime(2023, 1, 31)
    task = client.task.create('hello', start=start, end=end, tz=tz)
    assert task['isAllDay']
    assert task['startDate'] == '2023-01-28T08:00:00.000+0000'
    assert task['dueDate'] == '2023-02-01T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_both_dates_all_day_last_day_of_year(client):
    """Tests creating an all day task spanning multiple days on the last day of the year"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2023, 12, 28)
    end = datetime.datetime(2023, 12, 31)
    task = client.task.create('hello', start=start, end=end, tz=tz)
    assert task['isAllDay']
    assert task['startDate'] == '2023-12-28T08:00:00.000+0000'
    assert task['dueDate'] == '2024-01-01T08:00:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_both_dates_not_all_day(client):
    """Tests creating a task for a duration of time"""
    tz = 'America/Los_Angeles'
    start = datetime.datetime(2023, 1, 4, 14, 30)
    end = datetime.datetime(2023, 12, 31, 8, 30)
    task = client.task.create('hello', start=start, end=end, tz=tz)
    assert not task['isAllDay']
    assert task['startDate'] == '2023-01-04T22:30:00.000+0000'
    assert task['dueDate'] == '2023-12-31T16:30:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_both_dates_not_all_day_different_tz(client):
    """Tests creating a duration task for a different timezone"""
    tz = 'Kwajalein'
    start = datetime.datetime(2023, 1, 4, 14, 30)
    end = datetime.datetime(2023, 12, 31, 8, 30)
    task = client.task.create('hello', start=start, end=end, tz=tz)
    assert not task['isAllDay']
    assert task['startDate'] == '2023-01-04T02:30:00.000+0000'
    assert task['dueDate'] == '2023-12-30T20:30:00.000+0000'
    client.task.delete(task['id'])


def test_create_task_not_datetime_dates(client):
    # TODO Fix
    with pytest.raises(TypeError):
        task1 = client.task.create('hello', start='yeah this not a datetime')
    with pytest.raises(TypeError):
        task2 = client.task.create('hello', end='yeah this not a datetime')
    with pytest.raises(TypeError):
        task3 = client.task.create('hello', start='nope', end='yeah this not a datetime')


def test_create_task_title_and_priority_fail(client):
    """Tests task creation for title and priority"""
    title = str(uuid.uuid4())
    priority = 3  # Medium
    with pytest.raises(Exception):
        client.task.create(title, priority=priority)


def test_create_task_title_and_priority_string_fail(client):
    #TODO Fix
    """Tests task creation fail with a string input"""
    title = str(uuid.uuid4())
    priority = 'nope'
    with pytest.raises(TypeError):
        client.task.create(title, priority=priority)


def test_create_task_priority_normal_pass(client):
    """Tests task creation with priority for normal priority strings"""
    priorities = {'none': 0, 'low': 1, 'medium': 3, 'high': 5}
    for task in priorities:
        created = client.task.create(name=str(uuid.uuid4()), priority=task)
        assert created['priority'] == priorities[task]
        client.task.delete(created['id'])


def test_create_task_priority_different_cases(client):
    """Tests task creation with priority for different case priority strings"""
    priorities = {'none': 0, 'low': 1, 'medium': 3, 'high': 5}
    cases = {'NoNe', 'NONE', 'LoW', 'MeDIUM', 'HIGH'}
    for task in cases:
        created = client.task.create(name=str(uuid.uuid4()), priority=task)
        assert created['priority'] == priorities[task.lower()]
        client.task.delete(created['id'])


def test_create_task_different_list(client):
    """Tests task creation with set project id"""
    list_title = str(uuid.uuid4())
    list_ = client.project.create(list_title)  # Create list
    task_title = str(uuid.uuid4())
    task = client.task.create(task_title, project=list_['id'], priority='medium')  # Create task in list
    assert task
    assert task['projectId'] == list_['id']  # Assert list id property matches
    client.project.delete(list_['id'])  # Deleting the list deletes the task


def test_create_task_different_list_fail(client):
    """Tests exception thrown if list doesn't exist"""
    with pytest.raises(ValueError):
        client.task.create(str(uuid.uuid4()), project=str(uuid.uuid4()))


def test_create_task_with_explicit_inbox(client):
    """Tests successful creation if inbox id is passed"""
    task = client.task.create(str(uuid.uuid4()), project=client.inbox_id)
    assert task
    assert task['projectId'] == client.inbox_id
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
    #TODO Fix
    """Tests creating a task with a single tag as a string"""
    tag = str(uuid.uuid4())
    name = str(uuid.uuid4())
    task = client.task.create(name, tags=tag)
    assert task['tags'] == [tag]
    assert client.get_by_fields(name=task['tags'][0], search='tags')
    client.task.delete(task['id'])
    client.tag.delete(tag)


def test_create_task_with_tag_spaces(client):
    """Tests creating a tag with spaces in a task"""
    tag = 'This is a tag with spaces'
    name = str(uuid.uuid4())
    task = client.task.create(name, tags=tag)
    assert task['tags'] == [tag]
    client.task.delete(task['id'])
    client.tag.delete(tag.lower())


def test_create_task_with_tags(client):#TODO Fix
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
    client.tag.delete([tag1, tag2])


def test_create_multiple_tasks_with_tags(client):
    """Tests creating multiple tasks with multiple tags"""
    tag1 = str(uuid.uuid4()).upper()
    tag2 = str(uuid.uuid4()).upper()
    tag3 = str(uuid.uuid4()).upper()
    tag4 = str(uuid.uuid4()).upper()
    tag = [tag1, tag2, tag3, tag4]
    title = str(uuid.uuid4()).upper()
    title2 = str(uuid.uuid4()).upper()
    task1 = client.task.builder(title, tags=[tag1, tag2])
    task2 = client.task.builder(title2, tags=[tag1, tag2, tag3, tag4])
    tasks = client.task.create([task1, task2])
    assert len(tasks) == 2
    for t in tasks[0]['tags']:
        assert t in [tag1, tag2]
    for j in tasks[1]['tags']:
        assert j in tag
    # Delete the task
    client.task.delete([tasks[0]['id'], tasks[1]['id']])
    # Delete the tags
    client.tag.delete(tag)


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
    task = client.task.create(str(uuid.uuid4()), start=date)
    assert task['isAllDay']
    client.task.delete(task['id'])


def test_create_task_with_specific_time(client):
    """Tests creating a task with a specific time"""
    date = datetime.datetime(2022, 12, 31, 14, 30)  # 2:30 PM
    task = client.task.create(str(uuid.uuid4()), start=date)
    assert not task['isAllDay']
    client.task.delete(task['id'])


def test_get_from_list(client):
    """Tests getting all the tasks from a list"""
    # Make a fake list
    fake_list_id = str(uuid.uuid4())
    fake_list = {'id': fake_list_id}
    client.state['projects'].append(fake_list)  # Append the fake list
    # Make some fake tasks
    task1_title = str(uuid.uuid4())
    task2_title = str(uuid.uuid4())
    task1 = {'projectId': fake_list_id, 'title': task1_title}
    task2 = {'projectId': fake_list_id, 'title': task2_title}
    # Append fake tasks
    client.state['tasks'].append(task1)
    client.state['tasks'].append(task2)
    tasks = client.task.get_from_project(fake_list_id)
    assert task1 in tasks and task2 in tasks
    # Delete the fake objects
    client.delete_from_local_state(id=fake_list_id, search='projects')
    client.delete_from_local_state(title=task1_title, search='tasks')
    client.delete_from_local_state(title=task2_title, search='tasks')


def test_get_from_list_single(client):
    # Make a fake list
    fake_list_id = str(uuid.uuid4())
    fake_list = {'id': fake_list_id}
    client.state['projects'].append(fake_list)  # Append the fake list
    # Make some fake tasks
    task1_title = str(uuid.uuid4())
    task1 = {'projectId': fake_list_id, 'title': task1_title}
    client.state['tasks'].append(task1)
    tasks = client.task.get_from_project(fake_list_id)
    assert tasks == task1
    client.delete_from_local_state(id=fake_list_id, search='projects')
    client.delete_from_local_state(title=task1_title, search='tasks')


def test_get_from_list_error(client):
    """Tests exception raised if list doesn't exist"""
    with pytest.raises(ValueError):
        client.task.get_from_project(str(uuid.uuid4()))


def test_move_list_pass(client):
    """Tests moving all the tasks from one list into a new list"""
    list1_name = str(uuid.uuid4())
    list2_name = str(uuid.uuid4())
    list1 = client.project.create(list1_name)
    list2 = client.project.create(list2_name)
    # Tasks will be created in list2
    task1 = client.task.create(str(uuid.uuid4()), project=list2['id'])
    task2 = client.task.create(str(uuid.uuid4()), project=list2['id'])
    # Move the tasks: list2 -> list1
    move = client.task.move_projects(list2['id'], list1['id'])
    for ids in move:
        assert ids['id'] == task1['id'] or ids['id'] == task2['id']
    list2_tasks = client.task.get_from_project(list2['id'])
    assert not list2_tasks  # Assert that all the tasks in list 2 are gone
    list1_tasks = client.task.get_from_project(list1['id'])
    for task in list1_tasks:
        assert task['projectId'] == list1['id']
    # Deleting the lists will delete the tasks
    client.project.delete(list1['id'])
    client.project.delete(list2['id'])


def test_move_from_inbox(client):
    """Tests moving the items from the inbox to another list and back"""
    task = client.task.create(str(uuid.uuid4()))
    list_ = client.project.create(str(uuid.uuid4()))
    move = client.task.move_projects(client.inbox_id, list_['id'])
    inbox_tasks = client.task.get_from_project(client.inbox_id)
    assert not inbox_tasks  # Assert that nothing in inbox
    list_tasks = client.task.get_from_project(list_['id'])
    for task in list_tasks:
        assert task['projectId'] == list_['id']
    # Move back
    move_back = client.task.move_projects(list_['id'], client.inbox_id)
    list_tasks = client.task.get_from_project(list_['id'])
    assert not list_tasks  # Make sure that nothing in new list
    inbox_tasks = client.task.get_from_project(client.inbox_id)
    for task1 in inbox_tasks:
        assert task1['projectId'] == client.inbox_id
    # Delete the created task
    client.task.delete(task['id'])
    client.project.delete(list_['id'])


def test_complete(client):
    ids = [4535345, {}, set(), ()]
    for id in ids:
        with pytest.raises(TypeError):
            client.task.complete(id)


def test_complete_ids_dont_exist(client):
    ids = str(uuid.uuid4())
    ids2 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
    with pytest.raises(ValueError):
        client.task.complete(ids)
    with pytest.raises(ValueError):
        client.task.complete(ids2)


def test_complete_single(client):
    task = 'hullo'
    t = client.task.create(task)
    try:
        response = client.task.complete(t['id'])
        t['status'] = 0
        updated = client.task.update(t)
    except:
        client.task.delete(t['id'])
        assert False
    else:
        client.task.delete(t['id'])
        assert response['status'] == 0


def test_complete_task_multiple(client):
    task1 = client.task.builder('hello')
    task2 = client.task.builder('hello')
    task3 = client.task.builder('hello')
    tasks = client.task.create([task1, task2, task3])
    ids = [x['id'] for x in tasks]
    try:
        complete = client.task.complete(ids)
        tasks[0]['status'] = 0
        tasks[1]['status'] = 0
        tasks[2]['status'] = 0
        updated = client.task.update(tasks)
    except:
        client.task.delete(ids)
        assert False
    else:
        client.task.delete(ids)
        assert not client.get_by_fields(id=tasks[0]['id'], search='tasks')
        assert not client.get_by_fields(id=tasks[1]['id'], search='tasks')
        assert not client.get_by_fields(id=tasks[2]['id'], search='tasks')


def test_update_fail(client):
    obj = ['', 453535, (), set()]
    for o in obj:
        with pytest.raises(TypeError):
            client.task.update(o)


def test_update_single(client):
    obj = client.task.create('hello')
    obj['progress'] = 60
    try:
        response = client.task.update(obj)
    except:
        client.task.delete(obj['id'])
        assert False
    else:
        client.task.delete(obj['id'])
        assert response['progress'] == 60


def test_update_multiple(client):
    task3 = client.task.builder('yessir')
    task2 = client.task.builder('yppper')
    task1 = client.task.builder('d3r43r')
    tasks = client.task.create([task1, task2, task3])
    tasks[0]['progress'] = 60
    tasks[1]['progress'] = 60
    tasks[2]['progress'] = 60
    try:
        update = client.task.update(tasks)
    except:
        client.task.delete(tasks[0]['id'])
        client.task.delete(tasks[1]['id'])
        client.task.delete(tasks[2]['id'])
        assert False
    else:
        client.task.delete(tasks[0]['id'])
        client.task.delete(tasks[1]['id'])
        client.task.delete(tasks[2]['id'])
        assert update[0]['progress'] == 60
        assert update[1]['progress'] == 60
        assert update[2]['progress'] == 60


def test_delete_single_fail(client):
    name1 = 324234
    name2 = {}
    with pytest.raises(TypeError):
        client.task.delete(name1)
    with pytest.raises(TypeError):
        client.task.delete(name2)


def test_delete_single_task_doesnt_exist(client):
    name1 = str(uuid.uuid4()).upper()
    with pytest.raises(ValueError):
        client.task.delete(name1)


def test_delete_multi_task_doesnt_exist(client):
    names = [str(uuid.uuid4()).upper(), str(uuid.uuid4()).upper(), str(uuid.uuid4()).upper()]
    for name in names:
        with pytest.raises(ValueError):
            client.task.delete(name)


def test_delete_single_success(client):
    task = client.task.create('hello')
    delete = client.task.delete(task['id'])
    assert not client.get_by_id(task['id'])
    assert not client.get_by_fields(id=task['id'])
    assert delete == task


def test_delete_multiple_success(client):
    task1 = client.task.builder('hello')
    task2 = client.task.builder('hello')
    task3 = client.task.builder('hello')
    tasks = client.task.create([task1, task2, task3])
    delete = [task['id'] for task in tasks]
    deleted = client.task.delete(delete)
    assert not client.get_by_id(delete[0])
    assert not client.get_by_id(delete[1])
    assert not client.get_by_id(delete[2])
    count = 0
    for d in deleted:
        assert delete[count] == d['id']
        count += 1


def test_create_subtask_single(client):
    # Create the parent task
    parent = client.task.create('Parent Task')
    task = client.task.builder('Child Task')
    try:
        subtask = client.task.create_subtask(task, parent['id'])
    except:
        client.task.delete(parent['id'])
        assert False
    else:
        client.task.delete([parent['id'], subtask['id']])
        assert subtask['parentId'] == parent['id']


def test_create_subtask_multiple(client):
    parent = client.task.create('Parent Task')
    task1 = client.task.builder('Child Task 1')
    task2 = client.task.builder('Child Task 2')
    task3 = client.task.builder('Child Task 3')
    tasks = [task1, task2, task3]
    try:
        subtask = client.task.create_subtask(tasks, parent=parent['id'])
    except:
        client.task.delete(parent['id'])
        assert False
    else:
        ids = [x['id'] for x in subtask]
        ids.append(parent['id'])
        client.task.delete(ids)
        assert subtask[0]['parentId'] == parent['id']
        assert subtask[1]['parentId'] == parent['id']
        assert subtask[2]['parentId'] == parent['id']


def test_create_subtask_type_errors(client):
    objs = ''
    with pytest.raises(TypeError):
        client.task.create_subtask(objs, parent='')
    with pytest.raises(TypeError):
        client.task.create_subtask({}, parent=3)
    with pytest.raises(ValueError):
        client.task.create_subtask({}, parent='Yeah this not right')









