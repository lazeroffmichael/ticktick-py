![unit-tests](https://github.com/lazeroffmichael/ticktick-py/workflows/unit-tests/badge.svg)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://lazeroffmichael.github.io/ticktick-py/)

# ticktick-py
## Unofficial TickTick API Client for Python 3

## Description
`ticktick-py` is an unofficial API library for interacting with [TickTick.com](<https://www.ticktick.com/>). 
It allows
users a way to interact with their [TickTick](<https://www.ticktick.com/>) account 
using [Python](https://www.python.org/). 

## Features

The library automatically fetches all the tasks, tags, lists, and more linked to your profile and stores them in a 
dictionary named [`state`](usage/api/#state).

 - [Tasks](usage/tasks.md)
    - Create, Update, and Delete Tasks
    - Acquire all your uncompleted tasks
    - Move tasks easily between projects
    - Acquire all completed tasks in a certain date range
 - [Tags](usage/tags.md)
    - Batch create, update, and delete tags
    - Create tags with parameters that are not usually allowed: `\\ / " # : * ? < > | Space`
 - [Projects](usage/projects.md)
    - Batch create, update, and delete 'lists' (projects)
    - Batch archive projects

### Example: Creating A Task

Lets create a task in our ```inbox``` titled "Get Groceries"

``` python
name = 'Get Groceries'                      # Task Name
local_task = client.task.builder(name)      # Create a dictionary for the task
groceries = client.task.create(local_task)  # Actually create the task
```

### Result

A simplified dictionary for the newly created task is returned.

```python
print(groceries)

{'id': '60c6a40b8f083f896c9444a0', 'projectId': 'inbox115781412', 'title': 'Get Groceries', 'timeZone': '', 
 'reminders': [], 'priority': 0, 'status': 0, 'sortOrder': -3298534883328, 'items': []}
```
You can retrieve the full dictionary with every parameter by using the [`get_by_id`][api.TickTickClient.get_by_id] 
method. 

```python
full_task = client.get_by_id(groceries['id'])
print(full_task)

{'id': '60c6a40b8f083f896c9444a0', 'projectId': 'inbox115781412', 'sortOrder': -3298534883328, 
 'title': 'Get Groceries', 'timeZone': '', 'isFloating': False, 'reminder': '', 'reminders': [], 
 'priority': 0, 'status': 0, 'items': [], 'modifiedTime': '2021-06-14T00:34:19.907+0000', 'etag': 't8xnwewi', 
 'deleted': 0, 'createdTime': '2021-06-14T00:34:19.907+0000', 'creator': 113581412, 'tags': [], 'kind': 'TEXT'}
```

**Created Task In `TickTick`**

![image](https://user-images.githubusercontent.com/56806733/121826787-7c5ef980-cc6e-11eb-8483-745df39e973b.png)

Most methods will return the object that was changed. Consult the [usage](usage/api.md) documentation for more information on specific methods.

    
## Installation

Note: `ticktick-py` requires [Python 3.6](https://www.python.org/downloads/) or above.

```md
pip install ticktick-py
```

## Get Started 

### Register A New TickTick App

The library now uses TickTick's OpenAPI scheme when possible. This requires registering
a new app through TickTick's developer documentation.

[OpenAPI Documentation](https://developer.ticktick.com/docs#/openapi)

Click on `Manage Apps` in the top right corner. You will be prompted to login with your 
normal TickTick credentials if you are not already logged in. 

![image](https://user-images.githubusercontent.com/56806733/121824548-c4c3ea80-cc61-11eb-8160-698b6ae5c9f6.png)

Register a new app by clicking the `+App Name` button.

![image](https://user-images.githubusercontent.com/56806733/121824646-87139180-cc62-11eb-9911-fc8bc4d6c3d6.png)

`Name` is the only required parameter here. Once created you should see the app and be able to edit it. 

![image](https://user-images.githubusercontent.com/56806733/121825007-e377b080-cc64-11eb-957c-cedf3ef8f7fd.png)

There should now be a generated `Client ID` and `Client Secret` parameters. It is recommended you save these to your
environment, and make sure you do not share your actual `Client Secret`. 

![image](https://user-images.githubusercontent.com/56806733/121825074-584aea80-cc65-11eb-8262-8dde4d9481a1.png)

For `OAuth Redirect URL` enter any URL you would like to be redirected to upon giving permissions to your account. 
It does not have to be an actually live URL - this local host URL is fine for most purposes. It is also recommended you 
save this URL to your environment.

![image](https://user-images.githubusercontent.com/56806733/121825203-e1fab800-cc65-11eb-9a2d-38d0787c5b1b.png)

Once you have registered the app, you can now proceed with the rest of the setup. 

### Required Imports

``` python
from ticktick.oauth2 import OAuth2        # OAuth2 Manager
from ticktick.api import TickTickClient   # Main Interface
```

### Setup

``` python
auth_client = OAuth2(client_id=client_id,
                     client_secret=client_secret,
                     redirect_uri=uri)

client = TickTickClient(username, password, auth_client)
```

The first time the OAuth2 object runs, you will need to manually accept permissions. A webbrowser will automatically
open.

![image](https://user-images.githubusercontent.com/56806733/121825814-479c7380-cc69-11eb-8b0d-a2ff6ef1e8bd.png)

The default permissions are to Read and Write tasks (and are the only options right now). You can change the permissions
by specifying the `scope` parameter when creating your OAuth2 instance. More information can be found in the 
[OAuth2 documention](usage/oauth2.md).

In the console you will be prompted to enter the URL that you were redirected to. It will be your specified OAuth URL 
with some added parameters.

```
Enter the URL you were redirected to:
>? http://127.0.0.1:8080/?code=RK3dSi&state=None
```

That is it! Your token information is cached in a file (default is `.token-oauth`) so you will only have to manually 
allow access the first time, and whenever the token expires. As of now it seems tokens expire after about 6 months.

## Future Plans

- **General**
    - Enhanced Team Support
- **Tasks**
    - Get and Restore From Trash  
- **Projects**
    - Smart List Support
    - Column Creation For Kanban View
- **Pomo and Focus**  
    - Getting the focus / pomo statistics for your profile  
    - Starting and stopping the focus / pomo timer    
- **Habits**  
    - Get, create, archive, delete, and complete habits
