### 2.0.1 - 6/24/21
- Changed Retry from urllib3 library to come directly from the package instead of through Requests package
- Updated package requirements in requirements.txt

### 2.0.0 - 6/16/21
- Major Change: Implemented TickTick OpenAPI Scheme

#### Tasks
- create() -> Batch Task Creation No Longer Supported
- update() -> Batch Task Update No Longer Supported
- delete() -> Now Takes Full Task Dictionaries Instead Of Just Task ID's

#### Under The Hood Changes
- Major Test Refactoring -> Separate Unit and Integration Tests
- Cache Handler For Open API Scheme
- Minimizing Type Checks For Methods

### 1.0.2 - 1/18/21
- First Stable Release

### 1.0.0 - 1/18/21
- Initial Release