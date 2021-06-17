!!! info
    Task methods are accessed through the `task` [public member](api.md#functionality) of your [`TickTickClient`](api.md) instance.

    ```python
    # Assumes that 'client' is the name that references the TickTickClient instance.

    task = client.task.method()
    ```

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
## Subtask Items

| Name          | Description                                                                              | Schema             |
|---------------|------------------------------------------------------------------------------------------|--------------------|
| id            | Subtask identifier                                                                       | string             |
| title         | Subtask title                                                                            | string             |
| status        | The completion status of subtask Value : Normal: 0, Completed: 1                         | integer (int32)    |
| completedTime | Subtask completed time in "yyyy-MM-dd'T'HH:mm:ssZ" Example : "2019-11-13T03:00:00+0000"  | string (date-time) |
| isAllDay      | All day                                                                                  | boolean            |
| sortOrder     | Subtask sort order Example : 234444                                                      | integer (int64)    |
| startDate     | Subtask start date time in "yyyy-MM-dd'T'HH:mm:ssZ" Example : "2019-11-13T03:00:00+0000" | string (date-time) |
| timeZone      | Subtask timezone Example : "America/Los_Angeles"                                         | string             |

## Task Items

| Name          | Description                                                                          | Schema                  |
|---------------|--------------------------------------------------------------------------------------|-------------------------|
| id            | Task identifier                                                                      | string                  |
| projectId     | Task project id                                                                      | string                  |
| title         | Task title                                                                           | string                  |
| allDay        | All day                                                                              | boolean                 |
| completedTime | Task completed time in "yyyy-MM-dd'T'HH:mm:ssZ" Example : "2019-11-13T03:00:00+0000" | string (date-time)      |
| content       | Task content                                                                         | string                  |
| desc          | Task description of checklist                                                        | string                  |
| dueDate       | Task due date time in "yyyy-MM-dd'T'HH:mm:ssZ" Example : "2019-11-13T03:00:00+0000"  | string (date-time)      |
| items         | Subtasks of Task                                                                     | < ChecklistItem > array |
| priority      | Task priority Value : None:0, Low:1, Medium:3, High5                                 | integer (int32)         |
| reminders     | List of reminder triggers Example : [ "TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S" ]         | < string > array        |
| repeat        | Recurring rules of task Example : "RRULE:FREQ=DAILY;INTERVAL=1"                      | string                  |
| sortOrder     | Task sort order Example : 12345                                                      | integer (int64)         |
| startDate     | Start date time in "yyyy-MM-dd'T'HH:mm:ssZ" Example : "2019-11-13T03:00:00+0000"     | string (date-time)      |
| status        | Task completion status Value : Normal: 0, Completed: 1                               | integer (int32)         |
| timeZone      | Task timezone Example : "America/Los_Angeles"                                        | string                  |

::: managers.tasks