
!!! info
    Tag methods are accessed through the `tag` [public member](api.md#functionality) of your [`TickTickClient`](api.md) instance.

    ```python
    # Assumes that 'client' is the name that references the TickTickClient instance.

    tag = client.tag.method()
    ```

!!! question "Question About Logging In or Other Functionality Available?"
    [API and Important Information](api.md)

!!! tip
    All supported methods are documented below with usage examples, take a look!

    ** All usage examples assume that `client` is the name referencing the [`TickTickClient`](api.md) instance**

## Example TickTick Tag Dictionary

!!! info "Members"
    ??? summary "Descriptions"
        It is possible that not all possible fields are present in the table.

        |   Property  |            Description            | Example Value |  Type |                Useful Values               |
        |:-----------:|:---------------------------------:|:-------------:|:-----:|:------------------------------------------:|
        |    `name`   |      The lowercase of `label`     |    'books'    | `str` |                     N/A                    |
        |   `label`   |      The uppercase of `name`      |    'Books'    | `str` |                     N/A                    |
        | `sortOrder` | A sort ID relative to other tags. | 2748779069440 | `int` |                     N/A                    |
        |  `sortType` |      Sort type of the tag         |   `dueDate`   | `str` | `dueDate`, `project`, `title`, `priority`  |
        |   `color`   |       Hex color code string       |    #4AA6EF    | `str` |                     N/A                    |
        |    `etag`   |          Etag identifier.         |   'ji35exmv'  | `str` |                     N/A                    |
        |   `parent`  |   `name` field of the parent tag  |   'friends'   | `str` |                     N/A                    |

    ```python
    {'name': 'test',
    'label': 'Test',
    'sortOrder': 2748779069440,
    'sortType': 'project',
    'color': '#4AA6EF',
    'etag': 'zxdvlhqd',
    'parent': 'friends'}
    ```

## Sort Dictionary

!!! info "SORT_DICTIONARY"
    The sort dictionary maps integers to the different sort types possible for tags.
    It is a public member called SORT_DICTIONARY available through the `tag` [public member](/usage/api/#functionality) of
    the [`TickTickClient`](api.md) instance.

    ??? summary "Descriptions"
        | Value | Sort Type  |
        |-------|------------|
        | 0     | 'project'  |
        | 1     | 'dueDate'  |
        | 2     | 'title'    |
        | 3     | 'priority' |


::: managers.tags