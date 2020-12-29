"""
Testing Module For TagManager
"""
import uuid
import pytest
import time

from ticktick.helpers.hex_color import generate_hex_color


def test_tag_create(client):
    """Tests a successful creation of a tag"""
    name = str(uuid.uuid4())
    tag_ = client.tag.create(name)
    assert tag_
    client.tag.delete(name)  # Delete the tag


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
    assert 1 == 0


def test_tag_delete_fail(client):
    """Tests a failed deletion of a tag"""
    name = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.tag.delete(name)


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
    parent = str(uuid.uuid4())
    child = str(uuid.uuid4())
    # Create parent tag
    parent_ = client.tag.create(parent)
    # Create child tag
    child_ = client.tag.create(child, parent_name=parent_['name'])
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
        client.tag.create(child, parent_name=str(uuid.uuid4()))


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
    parent_name = str(uuid.uuid4())
    parent_ = client.tag.create(parent_name)  # Parent tag
    child_name = str(uuid.uuid4())
    color = generate_hex_color()
    # Task with all fields
    child_ = client.tag.create(child_name, color=color, parent_name=parent_name, sort=2)
    assert child_['name'] == child_name
    assert child_['color'] == color
    assert child_['sortType'] == 'title'
    assert child_['parent'] == parent_['name']
    client.tag.delete(child_name)
    client.tag.delete(parent_name)


def test_tag_update_name(client):
    """Tests updating an existing tags name"""
    parent = str(uuid.uuid4())
    # Create tag
    parent_ = client.tag.create(parent)
    # Update the name of the tag
    new_name = str(uuid.uuid4())
    new_ = client.tag.update(old_name=parent, new_name=new_name)
    # Assert that new_
    assert new_
    assert new_['name'] == new_name
    # Assert that the original object etag does not exist
    old_obj = client.get_by_etag(parent_['etag'])
    assert not old_obj
    # Delete the tag
    client.tag.delete(new_name)


def test_tag_update_name_fail(client):
    """Tests updating an existing tags name fail because of a fake etag"""
    fake_name = str(uuid.uuid4())
    new_name = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.tag.update(old_name=fake_name, new_name=new_name)


def test_update_color_success(client):
    """Tests updating an existing tag with a new color"""
    name = str(uuid.uuid4())
    tag = client.tag.create(name)  # Create new tag
    color = generate_hex_color()  # New color
    new_ = client.tag.update(name, color=color)
    assert new_['color'] == color
    client.tag.delete(name)  # Delete the tag


def test_update_color_fail(client):
    """Tests failure to update if the color id is not valid"""
    name = str(uuid.uuid4())
    tag = client.tag.create(name)
    color = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.tag.update(name, color=color)
    client.tag.delete(name)


def test_update_parent_success(client):
    """Tests updating parent success"""
    """Tests updating parent success"""
    parent_name = str(uuid.uuid4())
    child_name = str(uuid.uuid4())
    parent_etag = client.tag.create(parent_name)  # Create the parent tag
    child_etag = client.tag.create(child_name)  # Create the child tag
    # Update the child tag
    updated = client.tag.update(child_name, parent_name=parent_name)
    assert updated['parent'] == parent_name
    client.tag.delete(child_name)
    client.tag.delete(parent_name)


def test_update_parent_fail(client):
    """Tests updating with a parent that doesn't exist raises an exception"""
    child_name = str(uuid.uuid4())
    child_etag = client.tag.create(child_name)
    parent_name = str(uuid.uuid4())  # Not an actual etag
    with pytest.raises(ValueError):
        client.tag.update(child_name, parent_name=parent_name)
    client.tag.delete(child_name)


def test_update_sort_pass(client):
    """Tests updating the sort works with valid ints (0-4)"""
    sort_values = {0: 'project',
                   1: 'dueDate',
                   2: 'title',
                   3: 'priority'}
    for digit in sort_values:
        name = str(uuid.uuid4())
        obj = client.tag.create(name)  # Create tag
        updated = client.tag.update(name, sort=digit)  # Update the tag
        assert updated['sortType'] == sort_values[digit]
        client.tag.delete(name)  # Delete the tag


def test_update_all_pass(client):
    """Tests updating all fields at once works"""
    parent_name = str(uuid.uuid4())
    parent_obj = client.tag.create(parent_name)  # Create parent tag
    color = generate_hex_color()
    sort = 3
    child_name = str(uuid.uuid4())
    updated_name = str(uuid.uuid4())
    child_obj = client.tag.create(child_name, sort=2)
    updated_obj = client.tag.update(child_name,
                                    new_name=updated_name,
                                    color=color,
                                    sort=sort,
                                    parent_name=parent_name)
    assert updated_obj['name'] == updated_name
    assert updated_obj['color'] == color
    assert updated_obj['sortType'] == 'priority'
    assert updated_obj['parent'] == parent_name
    client.tag.delete(updated_name)
    client.tag.delete(parent_name)


def test_merge_success_two_tags(client):
    """Tests successful merge of the tasks of two tags"""
    name1 = str(uuid.uuid4())
    name2 = str(uuid.uuid4())
    tag1 = client.tag.create(name1)  # Create tag
    tag2 = client.tag.create(name2)  # Create tag
    # Merge tag1 <-- tag2
    merge = client.tag.merge(name1, name2)
    # Make sure that name2 doesn't exist anymore
    tag2 = client.get_by_fields(name=name2)
    assert not tag2
    client.tag.delete(name1)  # Delete the remaining tag


def test_merge_success_four_tags(client):
    """Tests the successful merge of the tasks of four tags"""
    assert 8 == 0
