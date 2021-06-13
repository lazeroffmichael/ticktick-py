!!! info
    Task methods are accessed through the `task` [public member](api.md#functionality) of your [`TickTickClient`](api.md) instance.

    ```python
    # Assumes that 'client' is the name that references the TickTickClient instance.

    task = client.task.method()
    ```


!!! question "Question About Logging In or Other Functionality Available?"
    [API and Important Information](api.md)

!!! tip
    All supported methods are documented below with usage examples, take a look!

    ** All usage examples assume that `client` is the name referencing the [`TickTickClient`](api.md) instance**

!!! tip "Important!"
        The [`datetime`](https://docs.python.org/3/library/datetime.html) module must be imported to use dates.

        First Way:
            ```python
            import datetime
            date = datetime.datetime(2021, 1, 1)
            ```

        Second Way:
            ```python
            from datetime import datetime
            date = datetime(2021, 1, 1)
            ```

## Example TickTick Task Dictionary

!!! info "Members"
    
    ```python
    {
        "id": "String",
        "projectId": "String",
        "title": "Task Title",
        "content": "Task Content",
        "desc": "Task Description",
        "allDay": True,
        "startDate": "2019-11-13T03:00:00+0000",
        "dueDate": "2019-11-14T03:00:00+0000",
        "timeZone": "America/Los_Angeles",
        "reminders": ["TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S"],
        "repeat": "RRULE:FREQ=DAILY;INTERVAL=1",
        "priority": 1,
        "status": 0,
        "completedTime": "2019-11-13T03:00:00+0000",
        "sortOrder": 12345,
        "items": [{
            "id": "String",
            "status": 1,
            "title": "Subtask Title",
            "sortOrder": 12345,
            "startDate": "2019-11-13T03:00:00+0000",
            "isAllDay": False,
            "timeZone": "America/Los_Angeles",
            "completedTime": "2019-11-13T03:00:00+0000"
        }
    ```



::: managers.tasks