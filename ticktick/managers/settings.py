import base64

class SettingsManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token
        self.headers = self._client.HEADERS

    def get_templates(self):
        # GET https://api.ticktick.com/api/v2/templates

        url = self._client.BASE_URL + 'templates'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def get_user_settings(self):
        # GET https://api.ticktick.com/api/v2/user/preferences/settings?includeWeb=true

        url = self._client.BASE_URL + 'user/preferences/settings?includeWeb=true'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def set_user_settings(self, setting, newValue):
        # PUT https://api.ticktick.com/api/v2/user/preferences/settings?includeWeb=true

        possible_settings = [
            'id',
            'timeZone',
            'locale',
            'isTimeZoneOptionEnabled',
            'startDayOfWeek',
            'defaultRemindTime',
            'dailyRemindTime',
            'showMeridiem',
            'defaultPriority',
            'defaultDueDate',
            'defaultReminds',
            'defaultADReminders',
            'defaultTimeMode',
            'defaultTimeDuration',
            'defaultToAdd',
            'sortTypeOfAllProject',
            'sortTypeOfInbox',
            'sortTypeOfAssignMe',
            'sortTypeOfToday',
            'sortTypeOfTomorrow,'
            'sortTypeOfWeek',
            'theme',
            'removeDate',
            'removeTag',
            'showPomodoro',
            'showCompleted',
            'posOfOverdue',
            'showFutureTask',
            'showChecklist',
            'webCalendarViewType',
            'swipeConf',
            'collapsedTime',
            'enableCountdown',
            'smartProjects',
            'isNotificationEnabled',
            'tabBars',
            'weekNumbersEnabled',
            'notificationOptions',
            'inboxColor',
            'templateEnabled',
            'calendarViewConf':
            'startWeekOfYear',
            'isEmailEnabled',
            'notificationEnabled',
            'nlpEnabled',
            'nlpenabled',
            'dateKeptInText',
            'lunarEnabled',
            'holidayEnabled',
            'pomodoroEnabled
        ]

        if(
            setting == (
                'pomodoroEnabled' or
                'holidayEnabled' or
                'lunarEnabled' or
                'dateKeptInText' or
                'nlpenabled' or
                'nlpEnabled' or
                'notificationEnabled' or
                'isEmailEnabled' or
                'templateEnabled' or
                'weekNumbersEnabled' or
                'isNotificationEnabled' or
                'enableCountdown' or
                'showChecklist' or
                'showFutureTask' or
                'showCompleted' or
                'showPomodoro' or
                'removeTag' or 
                'removeDate' or
                'showMeridiem' or 
                'isTimeZoneOptionEnabled'
            )
        ):
            if(type(newValue) != bool): 
                raise TypeError('This setting must be a boolean value!')

            current_user_settings = self.get_user_settings()
            current_user_settings[setting] = newValue
        elif(setting in possible_settings):
            raise ValueError('That setting is not yet supported!')
        else:
            raise ValueError('That setting is not valid!')

        url = self._client.BASE_URL + 'user/preferences/settings?includeWeb=true'
        payload = {
            'postData': current_user_settings,
            'hasPostData': True,
            'postDataEntries': [
                {
                    'bytes': str(base64.b64encode(current_user_settings.encode("utf-8")))
                }
            ]
        }
        response = self._client.http_put(url=url, json=payload, cookies=self._client.cookies, headers=self.headers)

        return response

    def get_profile(self):
        # GET https://api.ticktick.com/api/v2/user/profile

        url = self._client.BASE_URL + 'user/profile'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def get_daily_reminder_settings(self):
        # GET https://api.ticktick.com/api/v2/user/preferences/dailyReminder

        url = self._client.BASE_URL + 'user/preferences/dailyReminder'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def get_pomo_preferences(self):
        # GET https://api.ticktick.com/api/v2/user/preferences/pomodoro
        url = self._client.BASE_URL + 'user/preferences/pomodoro'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def get_habit_preferences(self):
        # GET https://api.ticktick.com/api/v2/user/preferences/habit?platform=web
        url = self._client.BASE_URL + 'user/preferences/habit?platform=web'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def get_app_preferences(self):
        # GET https://api.ticktick.com/api/v2/user/preferences/apps
        url = self._client.BASE_URL + 'user/preferences/apps'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def get_ical_link(self):
        # GET https://api.ticktick.com/api/v2/calendar/feeds/code
        url = self._client.BASE_URL + 'calendar/feeds/code'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def get_mailbox_link(self):
        # GET https://api.ticktick.com/api/v2/settings/mail/task/code
        url = self._client.BASE_URL + 'settings/mail/task/code'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def get_subscription_status(self):
        # GET https://api.ticktick.com/api/v2/subsribce
        url = self._client.BASE_URL + 'subsribce'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def update_preferences(self):
        # POST https://api.ticktick.com/api/v2/preferences/ext
        """
        postData: '{"matrix":{"mtime":1640792902971,"quadrants":[{"id":"quadrant1","name":null,"rule":"{\\"and\\":[{\\"or\\":[\\"overdue\\",\\"today\\",\\"tomorrow\\"],\\"conditionName\\":\\"dueDate\\",\\"conditionType\\":1},{\\"or\\":[5,3],\\"conditionName\\":\\"priority\\",\\"conditionType\\":1}],\\"type\\":0,\\"version\\":1}","sortOrder":0,"sortType":"dueDate"},{"id":"quadrant2","name":null,"rule":"{\\"and\\":[{\\"or\\":[\\"nodue\\",\\"2dayslater\\"],\\"conditionName\\":\\"dueDate\\",\\"conditionType\\":1},{\\"or\\":[5,3],\\"conditionName\\":\\"priority\\",\\"conditionType\\":1}],\\"type\\":0,\\"version\\":1}\\n","sortOrder":1,"sortType":"dueDate"},{"id":"quadrant3","name":null,"rule":"{\\"and\\":[{\\"or\\":[\\"overdue\\",\\"today\\",\\"tomorrow\\"],\\"conditionName\\":\\"dueDate\\",\\"conditionType\\":1},{\\"or\\":[1,0],\\"conditionName\\":\\"priority\\",\\"conditionType\\":1}],\\"type\\":0,\\"version\\":1}","sortOrder":2,"sortType":"dueDate"},{"id":"quadrant4","name":null,"rule":"{\\"and\\":[{\\"or\\":[\\"nodue\\",\\"2dayslater\\"],\\"conditionName\\":\\"dueDate\\",\\"conditionType\\":1},{\\"or\\":[1,0],\\"conditionName\\":\\"priority\\",\\"conditionType\\":1}],\\"type\\":0,\\"version\\":1}\\n","sortOrder":3,"sortType":"dueDate"}],"show_completed":true,"version":1},"desktop_conf":{"mtime":1640936330047,"tabs":["matrix"]},"mtime":1640936330047}',
        hasPostData: true,
        postDataEntries: [
            {
                bytes: 'eyJtYXRyaXgiOnsibXRpbWUiOjE2NDA3OTI5MDI5NzEsInF1YWRyYW50cyI6W3siaWQiOiJxdWFkcmFudDEiLCJuYW1lIjpudWxsLCJydWxlIjoie1wiYW5kXCI6W3tcIm9yXCI6W1wib3ZlcmR1ZVwiLFwidG9kYXlcIixcInRvbW9ycm93XCJdLFwiY29uZGl0aW9uTmFtZVwiOlwiZHVlRGF0ZVwiLFwiY29uZGl0aW9uVHlwZVwiOjF9LHtcIm9yXCI6WzUsM10sXCJjb25kaXRpb25OYW1lXCI6XCJwcmlvcml0eVwiLFwiY29uZGl0aW9uVHlwZVwiOjF9XSxcInR5cGVcIjowLFwidmVyc2lvblwiOjF9Iiwic29ydE9yZGVyIjowLCJzb3J0VHlwZSI6ImR1ZURhdGUifSx7ImlkIjoicXVhZHJhbnQyIiwibmFtZSI6bnVsbCwicnVsZSI6IntcImFuZFwiOlt7XCJvclwiOltcIm5vZHVlXCIsXCIyZGF5c2xhdGVyXCJdLFwiY29uZGl0aW9uTmFtZVwiOlwiZHVlRGF0ZVwiLFwiY29uZGl0aW9uVHlwZVwiOjF9LHtcIm9yXCI6WzUsM10sXCJjb25kaXRpb25OYW1lXCI6XCJwcmlvcml0eVwiLFwiY29uZGl0aW9uVHlwZVwiOjF9XSxcInR5cGVcIjowLFwidmVyc2lvblwiOjF9XG4iLCJzb3J0T3JkZXIiOjEsInNvcnRUeXBlIjoiZHVlRGF0ZSJ9LHsiaWQiOiJxdWFkcmFudDMiLCJuYW1lIjpudWxsLCJydWxlIjoie1wiYW5kXCI6W3tcIm9yXCI6W1wib3ZlcmR1ZVwiLFwidG9kYXlcIixcInRvbW9ycm93XCJdLFwiY29uZGl0aW9uTmFtZVwiOlwiZHVlRGF0ZVwiLFwiY29uZGl0aW9uVHlwZVwiOjF9LHtcIm9yXCI6WzEsMF0sXCJjb25kaXRpb25OYW1lXCI6XCJwcmlvcml0eVwiLFwiY29uZGl0aW9uVHlwZVwiOjF9XSxcInR5cGVcIjowLFwidmVyc2lvblwiOjF9Iiwic29ydE9yZGVyIjoyLCJzb3J0VHlwZSI6ImR1ZURhdGUifSx7ImlkIjoicXVhZHJhbnQ0IiwibmFtZSI6bnVsbCwicnVsZSI6IntcImFuZFwiOlt7XCJvclwiOltcIm5vZHVlXCIsXCIyZGF5c2xhdGVyXCJdLFwiY29uZGl0aW9uTmFtZVwiOlwiZHVlRGF0ZVwiLFwiY29uZGl0aW9uVHlwZVwiOjF9LHtcIm9yXCI6WzEsMF0sXCJjb25kaXRpb25OYW1lXCI6XCJwcmlvcml0eVwiLFwiY29uZGl0aW9uVHlwZVwiOjF9XSxcInR5cGVcIjowLFwidmVyc2lvblwiOjF9XG4iLCJzb3J0T3JkZXIiOjMsInNvcnRUeXBlIjoiZHVlRGF0ZSJ9XSwic2hvd19jb21wbGV0ZWQiOnRydWUsInZlcnNpb24iOjF9LCJkZXNrdG9wX2NvbmYiOnsibXRpbWUiOjE2NDA5MzYzMzAwNDcsInRhYnMiOlsibWF0cml4Il19LCJtdGltZSI6MTY0MDkzNjMzMDA0N30='
            }
        ],
        """
        pass

    def get_user_binding_info(self):
        # GET https://api.ticktick.com/api/v2/user/userBindingInfo
        url = self._client.BASE_URL + 'user/userBindingInfo'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    def get_user_sessions(self, lang_code='en_US'):
        # GET https://api.ticktick.com/api/v2/user/sessions?lang={lang_code}
        url = self._client.BASE_URL + 'user/sessions?lang={lang_code}'
        response = self._client.http_get(url, cookies=self._client.cookies, headers=self.headers)

        return response

    # Other endpoints 
        # OPTIONS user/preferences/pluginSettings
        # OPTIONS user/preferences/featurePrompt
        # OPTIONS user/isJustRegistered
        # OPTIONS templates
        # OPTIONS user/sessions?lang={lang_code}
        # OPTIONS user/userBindingInfo
        # OPTIONS preferences/ext

