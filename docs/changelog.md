### 2.0.3 - 7/8/23
- btw04 [PR #43](https://github.com/lazeroffmichael/ticktick-py/pull/43): Fix broken login by adding new header

### 2.0.2 - 12/27/21
- Dependency updates

### 2.0.1 - 6/24/21
- Change Retry class to come from urllib3 library instead of requests 

### 2.0.0 - 6/16/21
- Major Change: Implemented TickTick OpenAPI Scheme

#### Tasks
- create() -> Batch Task Creation No Longer Supported
- update() -> Batch Task Update No Longer Supported
- delete() -> Now Takes Full Task Dictionaries Instead Of Just Task ID's
- Added dates() method

#### Under The Hood Changes
- Major Test Refactoring -> Separate Unit and Integration Tests
- Cache Handler For Open API Scheme
- Minimizing Type Checks For Task Methods

### 1.0.2 - 1/18/21
- First Stable Release

### 1.0.0 - 1/18/21
- Initial Release
