"""
Testing Module For TagManager
"""
import uuid
import pytest

from ticktick.helpers.hex_color import generate_hex_color


def test_tag_create(client):
    """Tests a successful creation of a tag"""
    name = str(uuid.uuid4())
    tag_create = client.tag.create(name)
    tag_obj = client.get_by_etag(tag_create)  # Find the tag
    assert tag_obj
    client.tag.delete(tag_create)  # Delete the tag


def test_tag_delete(client):
    """Tests a successful deletion of a tag"""
    name = str(uuid.uuid4())
    tag_create = client.tag.create(name)
    # Find the tag
    tag_obj = client.get_by_etag(tag_create)
    assert tag_obj
    # Delete the tag
    tag_delete = client.tag.delete(tag_create)
    find = client.get_by_etag(tag_delete)
    assert not find


def test_tag_delete_fail(client):
    """Tests a failed deletion of a tag"""
    name = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.tag.delete(name)


def test_tag_create_with_duplicate_name_fail(client):
    """Tests attempting to create a tag with a name that already exists"""
    name = str(uuid.uuid4())
    etag = client.tag.create(name)  # Create tag
    with pytest.raises(ValueError):
        client.tag.create(name)  # Creating a tag with a duplicate name should raise error
    client.tag.delete(etag)  # Delete tag


def test_tag_create_with_color(client):
    """Tests creating a tag with color"""
    name = str(uuid.uuid4())
    color = "#b20000"
    tag_etag = client.tag.create(name, color_id=color)
    tag_obj = client.get_by_etag(tag_etag)
    assert tag_obj
    assert tag_obj['color'] == color
    client.tag.delete(tag_etag)


def test_tag_create_with_color_fail(client):
    """Tests a failed created of tag with color"""
    name = str(uuid.uuid4())
    color = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.tag.create(name, color_id=color)


def test_tag_create_with_parent_etag(client):
    """Tests a successful creation of a tag that has a parent tag"""
    parent = str(uuid.uuid4())
    child = str(uuid.uuid4())
    # Create parent task
    parent_etag = client.tag.create(parent)
    # Create child task
    child_etag = client.tag.create(child, parent_etag=parent_etag)
    # Obtain the object of the child task
    child_obj = client.get_by_etag(child_etag)
    # Obtain the object of the parent task
    parent_obj = client.get_by_etag(parent_etag)
    assert child_obj['parent'] == parent_obj['name']
    client.tag.delete(parent_etag)
    # Assert that child still exists
    child_obj = client.get_by_etag(child_etag)
    assert child_obj
    client.tag.delete(child_etag)


def test_tag_create_with_parent_etag_fail(client):
    """Tests trying to create a tag with a parent tag that doesn't exist"""
    child = str(uuid.uuid4())
    # Creating the child task with parent_etag that doesn't exist should raise error
    with pytest.raises(ValueError):
        client.tag.create(child, parent_etag=str(uuid.uuid4()))


def test_tag_create_with_sort_pass(client):
    """Tests creating a tag with sort value specified"""
    sort_values = {0: 'project',
                   1: 'dueDate',
                   2: 'title',
                   3: 'priority'}
    for digit in sort_values:
        name = str(uuid.uuid4())
        etag = client.tag.create(name, sort_type=digit)  # Create the tag
        obj = client.get_by_etag(etag)
        assert obj['sortType'] == sort_values[digit]  # Make sure sort type matches
        client.tag.delete(etag)


def test_tag_create_with_sort_fail(client):
    """Tests failure to create a tag with a bad sort value"""
    sort_value = 56  # Invalid
    with pytest.raises(ValueError):
        etag = client.tag.create(str(uuid.uuid4()), sort_type=sort_value)


def test_tag_create_with_all_fields(client):
    """Tests creating a tag with all fields"""
    parent_name = str(uuid.uuid4())
    parent_etag = client.tag.create(parent_name)  # Parent tag
    child_name = str(uuid.uuid4())
    color = generate_hex_color()
    # Task with all fields
    child_etag = client.tag.create(child_name, color_id=color, parent_etag=parent_etag, sort_type=2)
    child_obj = client.get_by_etag(child_etag)
    assert child_obj['name'] == child_name
    assert child_obj['color'] == color
    assert child_obj['sortType'] == 'title'
    parent_obj = client.get_by_etag(parent_etag)
    assert child_obj['parent'] == parent_obj['name']
    client.tag.delete(child_etag)
    client.tag.delete(parent_etag)


def test_tag_update_name(client):
    """Tests updating an existing tags name"""
    parent = str(uuid.uuid4())
    # Create tag
    parent_etag = client.tag.create(parent)
    # Update the name of the tag
    new_name = str(uuid.uuid4())
    new_etag = client.tag.update(parent_etag, new_name=new_name)
    # Get the newly updated object
    updated_obj = client.get_by_etag(new_etag)
    # Assert that updated_obj exists
    assert updated_obj
    assert updated_obj['name'] == new_name
    # Assert that the original object etag does not exist
    old_obj = client.get_by_etag(parent_etag)
    assert not old_obj
    # Delete the tag
    client.tag.delete(new_etag)


def test_tag_update_name_fail(client):
    """Tests updating an existing tags name fail because of a fake etag"""
    fake_etag = str(uuid.uuid4())
    new_name = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.tag.update(fake_etag, new_name=new_name)


def test_update_color_success(client):
    """Tests updating an existing tag with a new color"""
    name = str(uuid.uuid4())
    etag = client.tag.create(name)  # Create new tag
    color = generate_hex_color()  # New color
    new_etag = client.tag.update(etag, color=color)
    color_obj = client.get_by_etag(new_etag)
    assert color_obj['color'] == color
    with pytest.raises(ValueError):  # Since the etag has been replaced, this should raise an error
        client.tag.delete(etag)
    client.tag.delete(new_etag)  # Delete the tag


def test_update_color_fail(client):
    """Tests failure to update if the color id is not valid"""
    name = str(uuid.uuid4())
    etag = client.tag.create(name)
    color = str(uuid.uuid4())
    with pytest.raises(ValueError):
        client.tag.update(etag, color=color)
    client.tag.delete(etag)


def test_update_parent_success(client):
    """Tests updating parent success"""
    parent_name = str(uuid.uuid4())
    child_name = str(uuid.uuid4())
    parent_etag = client.tag.create(parent_name)  # Create the parent tag
    child_etag = client.tag.create(child_name)  # Create the child tag
    # Update the child tag
    updated = client.tag.update(child_etag, parent_etag=parent_etag)
    # Get the object
    updated_obj = client.get_by_etag(updated[child_name])
    assert updated_obj['parent'] == parent_name
    client.tag.delete(updated[child_name])
    client.tag.delete(updated[parent_name])


def test_update_parent_fail(client):
    """Tests updating with a parent that doesn't exist raises an exception"""
    child_name = str(uuid.uuid4())
    child_etag = client.tag.create(child_name)
    parent_etag = str(uuid.uuid4())  # Not an actual etag
    with pytest.raises(ValueError):
        client.tag.update(child_etag, parent_etag=parent_etag)
    client.tag.delete(child_etag)


def test_update_sort_pass(client):
    """Tests updating the sort works with valid ints (0-4)"""
    sort_values = {0: 'project',
                   1: 'dueDate',
                   2: 'title',
                   3: 'priority'}
    for digit in sort_values:
        etag = client.tag.create(str(uuid.uuid4()))  # Create tag
        updated = client.tag.update(etag, sort=digit)  # Update the tag
        updated_obj = client.get_by_etag(updated)  # Get the object
        assert updated_obj['sortType'] == sort_values[digit]
        client.tag.delete(updated)  # Delete the tag

