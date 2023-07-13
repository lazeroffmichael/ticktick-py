class PomoManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = ''

    def start(self):
        pass

    def statistics(self):
        # GET https://api.ticktick.com/api/v2/statistics/general
        pass

    def batch(self, function, startTime, endTime, tasks=''):
        # POST https://api.ticktick.com/api/v2/batch/pomodoro (add)
        """
        postData: '{"add":[{"local":true,"id":"61cf865fac8b5d1bb443fb0a","startTime":"2021-12-31T22:38:23.372+0000","status":1,"endTime":"2021-12-31T23:08:24.367+0000","tasks":[]}]}',
        hasPostData: true,
        postDataEntries: [
            {
                bytes: 'eyJhZGQiOlt7ImxvY2FsIjp0cnVlLCJpZCI6IjYxY2Y4NjVmYWM4YjVkMWJiNDQzZmIwYSIsInN0YXJ0VGltZSI6IjIwMjEtMTItMzFUMjI6Mzg6MjMuMzcyKzAwMDAiLCJzdGF0dXMiOjEsImVuZFRpbWUiOiIyMDIxLTEyLTMxVDIzOjA4OjI0LjM2NyswMDAwIiwidGFza3MiOltdfV19'
            }
        ],
        """
        pass

    def add(self, startTime, endTime, tasks=''):
        self.batch(function='add', startTime=startTime, endTime=endTime, tasks=tasks)
        pass

    def statistics_specific(startDate, endDate):
        # GET https://api.ticktick.com/api/v2/pomodoros/statistics/20211229/20211230
        pass

    def timeline():
        # GET https://api.ticktick.com/api/v2/pomodoros/timeline
        pass