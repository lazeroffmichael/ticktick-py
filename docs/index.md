# ticktick-py
## Unofficial TickTick API Client for Python 3
> Designed for [TickTick.com](<https://www.ticktick.com/>) API v2

## Description
`ticktick-py` is an unofficial API library for interacting with [TickTick.com](<https://www.ticktick.com/>). It allows
users a way to interact with their [TickTick](<https://www.ticktick.com/>) account using [Python](https://www.python.org/). Currently,
as of **1/14/2021**, there is no official API for [TickTick](<https://www.ticktick.com/>).

## Features

The API automatically fetches all the tasks, tags, lists, and more linked to your profile and stores them in a dictionary named [`state`](usage/api/#state).

 - [Tasks](usage/tasks.md)
    - Batch create, update, and delete tasks
    - Acquire all your uncompleted tasks
    - Move tasks easily between projects
    - Acquire all completed tasks in a certain date range
 - [Tags](usage/tags.md)
    - Batch create, update, and delete tags
    - Create tags with parameters that are not usually allowed: `\\ / " # : * ? < > | Space`
 - [Projects](usage/projects.md)
    - Batch create, update, and delete 'lists' (projects)
    - Batch archive projects

## Quick Guide 

### Initializing Your Session

``` python
from ticktick import api
client = api.TickTickClient('username', 'password')  # Enter correct username and password
```

Once you have initialized your session, all interactions will occur through the reference, in this case: ```client```

### Example: Creating A Task

Lets create a task in our ```inbox``` titled "Get Groceries", with the date as 5/6/2021 at 2:30PM:

``` python
from datetime import datetime  # Dates are supported through the datetime module

name = 'Get Groceries'
date = datetime(2021, 5, 6, 14, 30)
groceries = client.task.create(name, start=date)  # Create the task with the parameters.
```

### Result

A dictionary for the newly created task is returned.

```python
print(groceries)
{'id': '5ff24e4b8f08904035b304d9', 'projectId': 'inbox416323287', 'sortOrder': -1099511627776, 
'title': 'Get Groceries', 'content': '', 'startDate': '2021-05-06T21:30:00.000+0000', 
'dueDate': '2021-05-06T21:30:00.000+0000', 'timeZone': 'America/Los_Angeles', 
'isFloating': False, 'isAllDay': False, 'reminders': [], 'priority': 0, 'status': 0, 
'items': [], 'modifiedTime': '2021-01-03T23:07:55.004+0000', 'etag': 'ol2zesef', 'deleted': 0, 
'createdTime': '2021-01-03T23:07:55.011+0000', 'creator': 359368200, 'kind': 'TEXT'}
```

**Created Task In `TickTick`**

![image](https://user-images.githubusercontent.com/56806733/104566369-5f13f980-5602-11eb-904e-c6ac3e4984fb.png)

Most methods will return the object that was changed. Consult the [usage](usage/api.md) documentation for more information on specific methods.

##Installation
Note: `ticktick-py` requires [Python 3.6](https://www.python.org/downloads/) or above.

```md
pip install ticktick-py
```

## Future Plans

- **General**
    - Enhanced Team Support
- **Tasks**
    - Notification and Repeats For Tasks
    - Get and Restore From Trash  
- **Projects**
    - Smart List Support
    - Column Creation For Kanban View
- **Pomo and Focus**  
    - Getting the focus / pomo statistics for your profile  
    - Starting and stopping the focus / pomo timer    
- **Habits**  
    - Get, create, archive, delete, and complete habits
