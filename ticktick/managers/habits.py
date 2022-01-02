class HabitManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = ''

    #   ---------------------------------------------------------------------------------------------------------------
    #   Habit Methods

    def get_checkins(self):
        # POST habitChekckins/query 
        """
        {
            'postData': '{"habitIds":["",""],"afterStamp":20211224}',
            'hasPostData': True,
            'postDataEntries': [
                {
                    'bytes' b64encode(postData)
                }
            ]
        }
        """
        pass

    def batch_checkins(self, data, function):
        # POST habitCheckins/batch (create)
        """
        postData:  '{
            "add":[
                {
                    "checkinStamp": 20211201,
                    "checkinTime": "2021-12-31T07:30:37.000+0000",
                    "goal":1,
                    "habitId: "safasfas0990",
                    "id": "f90sdag0asd9f0as",
                    "status":2,
                    "value":1
                }
            ],
            "update":[],
            "delete":[]
        }',
        hasPostData: true,
        postDataEntries: [
            {
                bytes: base64encode(postData)
            }
        ]
        """
        # POST habitCheckins/batch (update)
        """
        postData: '{"add":[],"update":[{"checkinStamp":20211201,"checkinTime":"2021-12-31T07:36:45.000+0000","goal":1,"habitId":"6038980b801c81216396971b","id":"61ceb195ac8b5d3c97e7a7de","status":0,"value":0}],"delete":[]}',
        hasPostData: true,
        postDataEntries: [
            {
                bytes: 'eyJhZGQiOltdLCJ1cGRhdGUiOlt7ImNoZWNraW5TdGFtcCI6MjAyMTEyMDEsImNoZWNraW5UaW1lIjoiMjAyMS0xMi0zMVQwNzozNjo0NS4wMDArMDAwMCIsImdvYWwiOjEsImhhYml0SWQiOiI2MDM4OTgwYjgwMWM4MTIxNjM5Njk3MWIiLCJpZCI6IjYxY2ViMTk1YWM4YjVkM2M5N2U3YTdkZSIsInN0YXR1cyI6MCwidmFsdWUiOjB9XSwiZGVsZXRlIjpbXX0='
            }
        ],
        """
        pass

    def add_checkins(self, data):
        self.batch_checkins(data, 'add')
        pass

    def update_checkins(self, data):
        self.batch_checkins(data, 'update')
        pass

    def delete_checkins(self, data):
        self.batch_checkins(data, 'delete')
        pass

    def get_habits(self):
        # GET habits
        pass

    def batch_habits(self, data, function):
        # POST habits/batch (update)
        """
        postData: '{"add":[],"update":[{"color":"#F8D550","iconRes":"habit_early_to_rise","createdTime":"2021-02-26T06:41:15.000+0000","encouragement":"Get up and be amazing","etag":"2peywvxk","goal":1,"id":"6038980b801c81216396971b","modifiedTime":"2021-06-01T15:06:35.000+0000","name":"Early to Rise","recordEnable":false,"reminders":["06:30"],"repeatRule":"RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=SU,MO,TU,WE,TH,FR,SA","sortOrder":-4611686430744248000,"status":0,"step":0,"totalCheckIns":2,"type":"Boolean","unit":"Count","sectionId":"-1","targetDays":0,"targetStartDate":0,"completedCycles":0}],"delete":[]}',
        hasPostData: true,
        postDataEntries: [
            {
            bytes: 'eyJhZGQiOltdLCJ1cGRhdGUiOlt7ImNvbG9yIjoiI0Y4RDU1MCIsImljb25SZXMiOiJoYWJpdF9lYXJseV90b19yaXNlIiwiY3JlYXRlZFRpbWUiOiIyMDIxLTAyLTI2VDA2OjQxOjE1LjAwMCswMDAwIiwiZW5jb3VyYWdlbWVudCI6IkdldCB1cCBhbmQgYmUgYW1hemluZyIsImV0YWciOiIycGV5d3Z4ayIsImdvYWwiOjEsImlkIjoiNjAzODk4MGI4MDFjODEyMTYzOTY5NzFiIiwibW9kaWZpZWRUaW1lIjoiMjAyMS0wNi0wMVQxNTowNjozNS4wMDArMDAwMCIsIm5hbWUiOiJFYXJseSB0byBSaXNlIiwicmVjb3JkRW5hYmxlIjpmYWxzZSwicmVtaW5kZXJzIjpbIjA2OjMwIl0sInJlcGVhdFJ1bGUiOiJSUlVMRTpGUkVRPVdFRUtMWTtJTlRFUlZBTD0xO0JZREFZPVNVLE1PLFRVLFdFLFRILEZSLFNBIiwic29ydE9yZGVyIjotNDYxMTY4NjQzMDc0NDI0ODAwMCwic3RhdHVzIjowLCJzdGVwIjowLCJ0b3RhbENoZWNrSW5zIjoyLCJ0eXBlIjoiQm9vbGVhbiIsInVuaXQiOiJDb3VudCIsInNlY3Rpb25JZCI6Ii0xIiwidGFyZ2V0RGF5cyI6MCwidGFyZ2V0U3RhcnREYXRlIjowLCJjb21wbGV0ZWRDeWNsZXMiOjB9XSwiZGVsZXRlIjpbXX0='
            }
        """
        pass

    def update_habits(self, data):
        self.batch_habits(data, 'update')
        pass

    def add_habits(self, data):
        self.batch_habits(data, 'add')
        pass

    def delete_habits(self, data)
        self.batch_habits(data, 'delete')
        pass

    def get_sections(self):
        # GET habitSections
        pass

    def get_specific_records(self, ids=[], afterstamp=''):
        # GET habitRecords?habitIds=6037eb14801c327339afbd3a&habitIds=603897ae0cda91d09c9f376f&habitIds=6038980b801c81216396971b&habitIds=60389839801c81216396971c&afterStamp=20211230
        pass

# Other endpoints 
    # OPTIONS habitCheckins/query
