"""
Testing Module For TagManager
"""
import uuid
import pytest
import time

from ticktick.helpers.hex_color import generate_hex_color


def test_check_fields_labels(client):
    """Tests exception raised for all bad inputs in _check_fields"""
    # Test label already exists
    fake_tag = {'name': 'howdy', 'label': 'HOWDY'}
    label = 'HOWDY'
    client.state['tags'].append(fake_tag)
    with pytest.raises(ValueError):
        client.tag._check_fields(label)
    # Delete the object
    client.delete_from_local_state(label=label, search='tags')
    # Test label is not a string
    fake_tag = 56
    with pytest.raises(ValueError):
        client.tag._check_fields(fake_tag)


def test_check_fields_color_id(client):
    """Tests exception raised for all bad color inputs"""
    label = 56
    with pytest.raises(ValueError):
        client.tag._check_fields(color=label)  # Label not a string

    fake_color = '#454590hfkahf'
    with pytest.raises(ValueError):
        client.tag._check_fields(color=fake_color)  # color not valid


def test_check_parent_name(client):
    """Tests bad parent inputs"""
    label = 56
    with pytest.raises(ValueError):
        client.tag._check_fields(color=label)  # Label not a string
    label = 'HOWDY'
    # Exception raised if parent doesn't exist
    with pytest.raises(ValueError):
        client.tag._check_fields(parent_label=label)


def test_check_sort(client):
    """Tests check sort bad inputs"""
    sort = 'nope'
    with pytest.raises(ValueError):
        client.tag._check_fields(sort=sort)

    sort = 5
    with pytest.raises(ValueError):
        client.tag._check_fields(sort=sort)


def test_builder_success_just_name(client):
    """Tests tag builder object with just name"""
    name = 'HOWDY'
    obj = client.tag.builder(name)
    assert obj['label'] == name
    assert obj['name'] == name.lower()


def test_builder_success_name_and_color(client):
    """Tests builder object with name and color"""
    name = 'HOWDY'
    color = generate_hex_color()
    obj = client.tag.builder(name, color=color)
    assert obj['label'] == name
    assert obj['name'] == name.lower()
    assert obj['color'] == color


def test_builder_success_name_parent_color(client):
    """Tests builder object with name, color, and parent"""
    fake_tag = {'name': 'howdy', 'label': 'HOWDY'}
    parent_label = 'HOWDY'
    new_label = 'Yessirski'
    color = generate_hex_color()
    client.state['tags'].append(fake_tag)
    obj = client.tag.builder(new_label, color=color, parent=parent_label)
    assert obj['label'] == new_label
    assert obj['name'] == new_label.lower()
    assert obj['color'] == color
    assert obj['parent'] == fake_tag['name']
    client.delete_from_local_state(label=parent_label, search='tags')


def test_builder_success_all(client):
    """Tests builder object success with all fields"""
    fake_tag = {'name': 'howdy', 'label': 'HOWDY'}
    parent_label = 'HOWDY'
    new_label = 'Yessirski'
    color = generate_hex_color()
    client.state['tags'].append(fake_tag)
    sort = 2
    obj = client.tag.builder(new_label, color=color, parent=parent_label, sort=sort)
    assert obj['label'] == new_label
    assert obj['name'] == new_label.lower()
    assert obj['color'] == color
    assert obj['parent'] == fake_tag['name']
    assert obj['sortType'] == client.tag.SORT_DICTIONARY[sort]
    client.delete_from_local_state(label=parent_label, search='tags')


def test_tag_create(client):
    """Tests a successful creation of a tag"""
    name = str(uuid.uuid4()).upper()
    tag_ = client.tag.create(name)
    assert tag_
    client.tag.delete(name)  # Delete the tag


def test_tag_create_with_forbidden_characters(client):
    """Tests creating a tag with characters normally not allowed by TickTick"""
    name = "\ \ /  # : * ? < > | Space"
    tag = client.tag.create(name)
    assert tag
    client.tag.delete(name)


def test_tag_delete(client):
    """Tests a successful deletion of a tag"""
    name = str(uuid.uuid4())
    tag_ = client.tag.create(name)
    assert tag_
    # Delete the tag
    tag_delete = client.tag.delete(name)
    find = client.get_by_etag(tag_delete['etag'])
    assert not find


def test_tag_delete_with_task(client):
    """Tests that a tag is removed properly from a task"""
    # TODO: Implement
    pass


def test_tag_delete_fail(client):
    """Tests a failed deletion of a tag"""
    name = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.tag.delete(name)


def test_tag_batch_create(client):
    """Tests batch tag creation success"""
    label1 = str(uuid.uuid4()).upper()
    label2 = str(uuid.uuid4()).upper()
    label3 = str(uuid.uuid4()).upper()
    tag1 = client.tag.builder(label=label1)
    tag2 = client.tag.builder(label=label2)
    tag3 = client.tag.builder(label=label3)
    tags = [tag1, tag2, tag3]
    obj = client.tag.create(tags)
    assert len(obj) == 3
    # Assert that the objects are returned in the same order as passed
    assert label1 == obj[0]['label']
    assert label2 == obj[1]['label']
    assert label3 == obj[2]['label']
    client.tag.delete(obj[0]['name'])
    client.tag.delete(obj[1]['name'])
    client.tag.delete(obj[2]['name'])


def test_tag_create_with_duplicate_name_fail(client):
    """Tests attempting to create a tag with a name that already exists"""
    name = str(uuid.uuid4())
    tag_ = client.tag.create(name)  # Create tag
    with pytest.raises(ValueError):
        client.tag.create(name)  # Creating a tag with a duplicate name should raise error
    client.tag.delete(name)  # Delete tag


def test_tag_create_with_color(client):
    """Tests creating a tag with color"""
    name = str(uuid.uuid4())
    color = "#b20000"
    tag_ = client.tag.create(name, color=color)
    assert tag_
    assert tag_['color'] == color
    client.tag.delete(name)


def test_tag_create_with_color_fail(client):
    """Tests a failed created of tag with color"""
    name = str(uuid.uuid4())
    color = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.tag.create(name, color=color)


def test_tag_create_with_parent_etag(client):
    """Tests a successful creation of a tag that has a parent tag"""
    # TODO: Make this batched creation
    parent = str(uuid.uuid4())
    child = str(uuid.uuid4())
    # Create parent tag
    parent_ = client.tag.create(parent)
    # Create child tag
    child_ = client.tag.create(child, parent=parent_['name'])
    assert child_['parent'] == parent_['name']
    client.tag.delete(parent_['name'])
    # Assert that child still exists
    child_obj = client.get_by_etag(child_['etag'])
    assert child_obj
    client.tag.delete(child)


def test_tag_create_with_parent_etag_fail(client):
    """Tests trying to create a tag with a parent tag that doesn't exist"""
    child = str(uuid.uuid4())
    # Creating the child task with parent_etag that doesn't exist should raise error
    with pytest.raises(ValueError):
        client.tag.create(child, parent=str(uuid.uuid4()))


def test_tag_create_with_sort_pass(client):
    """Tests creating a tag with sort value specified"""
    sort_values = {0: 'project',
                   1: 'dueDate',
                   2: 'title',
                   3: 'priority'}
    for digit in sort_values:
        name = str(uuid.uuid4())
        obj = client.tag.create(name, sort=digit)  # Create the tag
        assert obj['sortType'] == sort_values[digit]  # Make sure sort type matches
        client.tag.delete(name)


def test_tag_create_with_sort_fail(client):
    """Tests failure to create a tag with a bad sort value"""
    sort_value = 56  # Invalid
    with pytest.raises(ValueError):
        client.tag.create(str(uuid.uuid4()), sort=sort_value)


def test_tag_create_with_all_fields(client):
    """Tests creating a tag with all fields"""
    # TODO: Batch create here
    parent_name = str(uuid.uuid4())
    parent_ = client.tag.create(parent_name)  # Parent tag
    child_name = str(uuid.uuid4())
    color = generate_hex_color()
    # Task with all fields
    child_ = client.tag.create(child_name, color=color, parent=parent_name, sort=2)
    assert child_['name'] == child_name
    assert child_['color'] == color
    assert child_['sortType'] == 'title'
    assert child_['parent'] == parent_['name']
    client.tag.delete(child_name)
    client.tag.delete(parent_name)


def test_rename_both_not_strings(client):
    old = 475893758925
    new = 75892970594825
    with pytest.raises(ValueError):
        client.tag.rename(old, new)


def test_rename_old_doesnt_exist(client):
    old = str(uuid.uuid4()).upper()
    new = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.tag.rename(old, new)


def test_rename_new_already_exists(client):
    name1 = str(uuid.uuid4()).upper()
    name2 = str(uuid.uuid4())
    tag1 = client.tag.builder(name1)
    tag2 = client.tag.builder(name2)
    objs = client.tag.create([tag1, tag2])
    with pytest.raises(ValueError):
        client.tag.rename(name1, name2)
    client.tag.delete(name1)
    client.tag.delete(name2)


def test_rename_works(client):
    name1 = str(uuid.uuid4())
    name2 = str(uuid.uuid4()).upper()
    tag1 = client.tag.create(name1)
    rename = client.tag.rename(name1, name2)
    assert rename['label'] == name2
    assert rename['name'] == name2.lower()
    # Make sure you can't get from first name
    obj = client.get_by_fields(name=name1, search='tags')
    assert not obj
    client.tag.delete(name2)


def test_recolor_fail(client):
    label = 34343434
    color = 43535345
    with pytest.raises(ValueError):
        client.tag.color(label, color)


def test_recolor_label_doesnt_exist(client):
    label = str(uuid.uuid4()).upper()
    color = generate_hex_color()
    with pytest.raises(ValueError):
        client.tag.color(label, color)


def test_recolor_invalid_color(client):
    label = str(uuid.uuid4()).upper()
    client.tag.create(label)
    color = 'yeah this not a color'
    with pytest.raises(ValueError):
        client.tag.color(label, color)
    client.tag.delete(label)


def test_recolor_works(client):
    label = str(uuid.uuid4()).upper()
    client.tag.create(label)
    color = generate_hex_color()
    obj = client.tag.color(label, color)
    assert obj['label'] == label
    assert obj['name'] == label.lower()
    assert obj['color'] == color
    client.tag.delete(label)


def test_sorting_fail(client):
    label = 'okay'
    sort = 'nope'  # What should cause the fail
    with pytest.raises(ValueError):
        client.tag.sorting(label, sort)


def test_sorting_fail_2(client):
    label = str(uuid.uuid4())
    sort = 3
    with pytest.raises(ValueError):
        client.tag.sorting(label, sort)


def test_sorting_fail_3(client):
    label = str(uuid.uuid4()).upper()
    client.tag.create(label)
    with pytest.raises(ValueError):
        client.tag.sorting(label, 7)
    client.tag.delete(label)


def test_sorting_works(client):
    label = str(uuid.uuid4()).upper()
    tag = client.tag.create(label)
    sort = 3
    obj = client.tag.sorting(label, sort)
    assert obj['sortType'] == client.tag.SORT_DICTIONARY[sort]
    assert obj['label'] == label
    assert obj['name'] == label.lower()
    client.tag.delete(label)

















def test_merge_fail(client):
    name = 56325425
    with pytest.raises(ValueError):
        client.tag.merge(name, str(uuid.uuid4()))


def test_merge_fail_no_args(client):
    name = str(uuid.uuid4()).upper()
    tag = client.tag.create(name)
    with pytest.raises(ValueError):
        client.tag.merge(name)  # Test no args
    arg = 458927358934
    with pytest.raises(ValueError):
        client.tag.merge(name, arg)  # Tests invalid arg (int)
    arg = {458927358934}
    with pytest.raises(ValueError):
        client.tag.merge(name, arg)  # Tests invalid arg (dict)
    arg = (458927358934, 342423424)
    with pytest.raises(ValueError):
        client.tag.merge(name, arg)  # Tests invalid arg (tuple)
    merge = [23245]
    with pytest.raises(ValueError):
        client.tag.merge(name, merge)
    client.tag.delete(name)


def test_merge_success_two_tags(client):
    """Tests successful merge of the tasks of two tags"""
    name1 = str(uuid.uuid4()).upper()
    name2 = str(uuid.uuid4())
    tag1 = client.tag.builder(name1)
    tag2 = client.tag.builder(name2)
    objs = client.tag.create([tag1, tag2])
    # Merge tag1 <-- tag2
    merge = client.tag.merge(name1, name2)
    # Make sure that name2 doesn't exist anymore
    tag2 = client.get_by_fields(name=name2)
    assert not tag2
    client.tag.delete(name1)  # Delete the remaining tag


def test_merge_success_three_tags_in_list(client):
    name1 = str(uuid.uuid4()).upper()
    name2 = str(uuid.uuid4())
    name3 = str(uuid.uuid4()).upper()
    tag1 = client.tag.builder(name1)
    tag2 = client.tag.builder(name2)
    tag3 = client.tag.builder(name3)
    objs = client.tag.create([tag1, tag2, tag3])
    merge = [name2, name3]
    merged = client.tag.merge(name1, merge)
    # Assert name2 and name3 don't exist
    tag2 = client.get_by_fields(label=name2)
    assert not tag2
    tag3 = client.get_by_fields(label=name3)
    assert not tag3
    client.tag.delete(name1)

