!!! important
    `Projects` within `TickTick` are known as `Lists`. However, in the API `Lists` are referred to as `Projects` to limit
    confusion with the `list` built in type.

!!! info
    Project methods are accessed through the `project` [public member](api.md#functionality) of your [`TickTickClient`](api.md) instance.

    ```python
    # Assumes that 'client' is the name that references the TickTickClient instance.

    project = client.project.method()
    ```

!!! question "Question About Logging In or Other Functionality Available?"
    [API and Important Information](api.md)

!!! tip
    All supported methods are documented below with usage examples, take a look!

    ** All usage examples assume that `client` is the name referencing the [`TickTickClient`](api.md) instance**

## Example TickTick Project Dictionary

!!! info "Members"
    ??? summary "Descriptions"
        It is possible that not all possible fields are present in the table.

        |        Property       |                         Description                         |          Example Value         |  Type  |                     Useful Values                    |
        |:---------------------:|:-----------------------------------------------------------:|:------------------------------:|:------:|:----------------------------------------------------:|
        |          `id`         |                    The ID of the project                    |   '5ffe93f3b04b35082bbce7b0'   |  `str` |                          N/A                         |
        |         `name`        |                   The name of the project                   |            'Hobbies'           |  `str` |                          N/A                         |
        |       `isOwner`       |       Whether you are the owner of the project or not.      |              True              | `bool` |                          N/A                         |
        |        `color`        |             The hex color code for the project.             |            '#6fcbdf'           |  `str` |                          N/A                         |
        |        `inAll`        |                             N/A                             |              True              | `bool` |                          N/A                         |
        |      `sortOrder`      |       A sort ID relative to other tasks in the project      |         -1099511627776         |  `int` |          Lower sortOrder == Higher Position          |
        |       `sortType`      |                   Sort type of the project                  |            `dueDate`           |  `str` |  `dueDate`, `sortOrder`, `title`, `tag`, `priority`  |
        |      `userCount`      |          How many users have access to the project.         |                1               |  `int` |                          N/A                         |
        |         `etag`        |                       Etag identifier.                      |           'ji35exmv'           |  `str` |                          N/A                         |
        |     `modifiedTime`    |                     Time last modified.                     | '2021-01-13T07:18:21.000+0000' |  `str` |                          N/A                         |
        |        `closed`       |                       Archive status.                       |              False             | `bool` | `none` and `False` = Not Archived, `True` = Archived |
        |        `muted`        |      Whether the project is 'hidden' (no notifications)     |              False             | `bool` |                          N/A                         |
        |     `transferred`     |    Possibly if the ownership of the project has changed.    |              None              | `bool` |                          N/A                         |
        |       `groupId`       |            ID of the project folder if it exists.           |   '5ffe11b7b04b356ce74d49da'   |  `str` |                          N/A                         |
        |       `viewMode`      |                  View mode of the project.                  |            'kanban'            |  `str` |                  `kanban` or `list`                  |
        | `notificationOptions` |                             N/A                             |              None              |   N/A  |                          N/A                         |
        |        `teamId`       |                       ID of your team.                      |            342537403           |  `int` |                          N/A                         |
        |      `permission`     |                             N/A                             |              None              |   N/A  |                          N/A                         |
        |         `kind`        | If the project is a normal `TASK` project or `NOTE` project |             'TASK'             |  `str` |                   'TASK' or 'NOTE'                   |

    ```python
    {'id': '5ffe24a18f081003f3294c44',
    'name': 'Reading',
    'isOwner': True,
    'color': '#6fcbdf',
    'inAll': True,
    'sortOrder': 0,
    'sortType': None,
    'userCount': 1,
    'etag': 'qbj4z0gl',
    'modifiedTime': '2021-01-12T22:37:21.823+0000',
    'closed': None,
    'muted': False,
    'transferred': None,
    'groupId': '5ffe11b7b04b356ce74d49da',
    'viewMode': None,
    'notificationOptions': None,
    'teamId': None,
    'permission': None,
    'kind': 'TASK'}
    ```

## Example TickTick Project Folder (group) Dictionary

!!! info "Members"
    ??? summary "Descriptions"
        It is possible that not all possible fields are present in the table.

        |   Property  |                    Description                   |        Example Value       |  Type  |                   Useful Values                   |
        |:-----------:|:------------------------------------------------:|:--------------------------:|:------:|:-------------------------------------------------:|
        |     `id`    |           The ID of the project folder           | '5ffe93f3b04b35082bbce7b0' |  `str` |                        N/A                        |
        |    `etag`   |                 Etag identifier.                 |         'ji35exmv'         |  `str` |                        N/A                        |
        |    `name`   |          The name of the project folder          |          'Hobbies'         |  `str` |                        N/A                        |
        |  `showAll`  |                        N/A                       |            True            | `bool` |                        N/A                        |
        | `sortOrder` | A sort ID relative to other tasks in the project |       -1099511627776       |  `int` |         Lower sortOrder == Higher Position        |
        |  `deleted`  |   Whether the project folder is deleted or not.  |              0             |  `int` |                        N/A                        |
        |   `userId`  |              User ID of the creator              |          586938759         |  `int` |                        N/A                        |
        |  `sortType` |             Sort type of the project folder      |          `dueDate`         |  `str` | `dueDate`, `project`, `title`, `tag`, `priority`  |
        |   `teamId`  |                 ID of your team.                 |          342537403         |  `int` |                        N/A                        |


    ```python
    {'id': '600008f2b04b355792c7a42d',
    'etag': 'yeozz5v8',
    'name': 'Test',
    'showAll': True,
    'sortOrder': -6786182545408,
    'deleted': 0,
    'userId': 586934829,
    'sortType': 'project',
    'teamId': None}
    ```

::: managers.projects

