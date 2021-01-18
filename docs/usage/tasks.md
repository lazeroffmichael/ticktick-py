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
    ??? summary "Descriptions"
        It is possible that not all possible fields are present in the table.

        |       Property      |                                 Description                                |                                                           Example Value                                                           |  Type  |             Useful Values            |
        |:-------------------:|:--------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------------------------------------:|:------:|:------------------------------------:|
        |         `id`        |                             The ID of the task                             |                                                     '5ffe93f3b04b35082bbce7b0'                                                    |  `str` |                  N/A                 |
        |     `projectId`     |                         The project ID for the task                        |                                                     '5ffe96c88f08237f3d16fa57'                                                    |  `str` |                  N/A                 |
        |     `sortOrder`     |              A sort ID relative to other tasks in the Project              |                                                           -1099511627776                                                          |  `int` |  Lower sortOrder == Higher Position  |
        | `title`             | The name of the task                                                       | 'Deposit Funds'                                                                                                                   | `str`  | N/A                                  |
        | `content`           | Text that will go underneath the title of the object.                      | 'This is a description"                                                                                                           | `str`  |                  N/A                 |
        | `desc`              | N/A                                                                        | ''                                                                                                                                | `str`  | N/A                                  |
        | `startDate`         | The start date or time for the object.                                     | '2021-01-12T08:00:00.000+0000'                                                                                                    | `str`  | N/A                                  |
        | `dueDate`           | The end date for the object.                                               | '2021-01-12T08:00:00.000+0000'                                                                                                    | `str`  | N/A                                  |
        | `timeZone`          | Time zone for the object                                                   | 'America/Los_Angeles'                                                                                                             | `str`  | N/A                                  |
        | `isFloating`        | If the object should keep the same time regardless of change in time zone. | False                                                                                                                             | `bool` | N/A                                  |
        | `isAllDay`          | Specifies if the task has a specific time/duration.                        | True                                                                                                                              | `bool` | N/A                                  |
        | `reminders`         | Reminders for the task                                                     | [{'id': '5ffe9ebcb04b35082bbce88f',  'trigger': 'TRIGGER:P0DT9H0M0S'}]                                                            | `list` | N/A                                  |
        | `repeatFirstDate`   | First repeat date                                                          | '2021-01-12T08:00:00.000+0000'                                                                                                    | `str`  | N/A                                  |
        | `exDate`            | N/A                                                                        | []                                                                                                                                | `list` | N/A                                  |
        | `priority`          | Priority value                                                             | 1                                                                                                                                 | `int`  | 0 = None, 1 = Low, 3 = Med, 5 = High |
        | `status`            | Whether the task is complete or not                                        | 0                                                                                                                                 | `int`  | 0 = Not Complete, 2 = Complete       |
        | `items`             | If the task is a CHECKLIST - item dictionaries are stored in this list.    | []                                                                                                                                | `list` | N/A                                  |
        | `progress`          | Progress amount.                                                           | 70                                                                                                                                | `int`  | 0-100                                |
        | `modifiedTime`      | Time last modified.                                                        | '2021-01-13T07:18:21.000+0000'                                                                                                    | `str`  | N/A                                  |
        | `deleted`           | If the task is deleted.                                                    | 0                                                                                                                                 | `int`  | N/A                                  |
        | `createdTime`       | Creation time.                                                             | 2021-01-13T06:32:19.000+0000                                                                                                      | `str`  | N/A                                  |
        | `etag`              | Etag identifier.                                                           | 'ji35exmv'                                                                                                                        | `str`  | N/A                                  |
        | `creator`           | Creator identifier.                                                        | 447666584                                                                                                                         | `int`  | N/A                                  |
        | `tags`              | Name of the tags in a list.                                                | ['friends', 'party']                                                                                                              | `list` | The tags will be lowercase.          |
        | `pomodoroSummaries` | Pomodoro summary for the task.                                             | [{'userId': 447666584, 'count': 1, 'estimatedPomo': 0, 'duration': 25}]                                                           | `list` | N/A                                  |
        | `focusSummaries`    | Focus summary for the task.                                                | [{'userId': 447666584, 'pomoCount': 1, 'estimatedPomo': 0, 'estimatedDuration': 0, 'pomoDuration': 1500, 'stopwatchDuration': 0}] | `list` | N/A                                  |
        | `columnId`          | If in a project with kanban view, this identifies which section it is in.  | '11b745ecab9f0799bf53eb70'                                                                                                        | `str`  | N/A                                  |
        | `childIds`          | The ID's of any subtasks.                                                  | ['5ffe97edb04b35082bbce832']                                                                                                      | `list` | N/A                                  |
        | `kind`              | Determines if the task has a normal description, or item list description. | 'TEXT'                                                                                                                            | `str`  | 'TEXT' or 'CHECKLIST'                |

    ```python
    {'id': '5ffe93f3b04b35082bbce7b0',
    'projectId': '5ffe96c88f08237f3d16fa57',
    'sortOrder': -1099511627776,
    'title': 'Deposit Funds',
    'content': '',
    'desc': '',
    'startDate': '2021-01-12T08:00:00.000+0000',
    'dueDate': '2021-01-12T08:00:00.000+0000',
    'timeZone': 'America/Los_Angeles',
    'isFloating': False,
    'isAllDay': True,
    'reminders': [],
    'exDate': [],
    'priority': 1,
    'status': 0,
    'items': [{'id': '5ffe972eb04b35082bbce831',
               'status': 0,
               'title': 'Hellooo',
               'sortOrder': 0,
               'startDate': None,
               'isAllDay': False,
               'timeZone': 'America/Los_Angeles',
               'snoozeReminderTime': None,
               'completedTime': None}],
    'progress': 0,
    'modifiedTime': '2021-01-13T06:49:17.508+0000',
    'etag': 'ji35exmv',
    'deleted': 0,
    'createdTime': '2021-01-13T06:32:19.000+0000',
    'creator': 447666584,
    'tags': ['friends', 'party'],
    'pomodoroSummaries': [],
    'columnId': '11b745ecab9f0799bf53eb70',
    'childIds': ['5ffe97edb04b35082bbce832'],
    'kind': 'CHECKLIST'
     }
    ```


::: managers.tasks