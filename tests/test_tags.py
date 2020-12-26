"""
Testing Module For Testing Tag Functionality
"""
import uuid
import pytest


def test_tag_create(client):
    """Tests a successful creation of a tag"""
    name = str(uuid.uuid4())
    tag_create = client.tag.create(name)
    # Find the tag
    tag_obj = client.get_by_etag(tag_create)
    assert tag_obj
    # Delete the tag
    client.tag.delete(tag_create)


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
    child_etag = client.tag.create(child)
    # Obtain the object of the child task
    child_obj = client.get_by_etag(child_etag)
    assert child_obj['parent'] == parent_etag
    client.tag.delete(parent_etag)
    client.tag.delete(child_etag)


