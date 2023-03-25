"""
Integration tests for the habits
"""
from freezegun import freeze_time


class TestCreate:

    @freeze_time("2023-01-01 03:00:00")
    def test_no_parameters(self, client):
        prev_state = client.state.copy()
        response = client.habit.create()

        assert len(response[0]) == 2
        assert len(response[1]) == 1
        assert len(response[1][0]) == 23
        assert response[1][0]['id'] is not None
        assert response[1][0]['createdTime'] == '2023-01-01T03:00:00+0000'
        assert response[1][0]['modifiedTime'] == '2023-01-01T03:00:00+0000'
        habit_id = response[1][0]['id']
        assert client.state != prev_state
        deletion_response = client.habit.delete(habit_id)
        assert len(deletion_response) == 2
        assert client.state == prev_state
