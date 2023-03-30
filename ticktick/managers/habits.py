import secrets
from datetime import datetime, timedelta

from ticktick.helpers import time_methods


class HabitManager:
    HABITS_BASE_URL = 'https://api.ticktick.com/api/v2/habits'
    HABIT_CHECKINS_URL = 'https://api.ticktick.com/api/v2/habitCheckins'
    HABIT_SECTIONS_URL = 'https://api.ticktick.com/api/v2/habitSections'

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = ''

    #   ---------------------------------------------------------------------------------------------------------------
    #   Habit Methods
    def create(self,
               color="#97E38B",
               icon="habit_daily_check_in",
               created_time=datetime.now(),
               encouragement="",
               etag="",
               goal=1,
               modified_time=datetime.now(),
               name="Daily",
               record_enable="false",
               reminders=[],
               repeat_rule="RRULE:FREQ=WEEKLY;BYDAY=SU,MO,TU,WE,TH,FR,SA",
               sort_order=-6597069766656,
               status=0,
               step=0,
               total_checkins=0,
               habit_type="Boolean",
               unit="Count",
               section_id=-1,
               target_days=0,
               target_start_date=time_methods.convert_date_to_stamp(datetime.now()),
               completed_cycles=0,
               ex_dates=[]):

        """
        Creates a new habit

        Arguments:
            name: Name of the new habit
            icon: Use helpers.icons for a list of available icons or txt_CHAR with a single Unicode character as CHAR
            color: Color of the habit icon. Only relevant if icon is a single letter
            reminders: Reminders set for the habit. Example: ["15:00", "16:30", "19:30"]
            repeat_rule: Frequency at which the habit should repeat. Special TickTick Syntax String
            record_enable: Auto-Pop-Up Habit Log when finishing habit for the day
            target_days: Amount of target days
            target_start_date: Date at which the habit day target starts
            habit_type: habit type. Available: 'Boolean' (for on/off habits) or 'Real' (for counting habits)
            goal: Goal amount of the new habit. Only relevant if habit is counting
            unit: Name of the counting unit. Only relevant if habit is counting
            created_time: Internal timestamp for the creation of the habit. Best left unchanged
            encouragement: Encouragement message that displays beneath the habit. Might only be available in the app
            etag: internal tag
            modified_time: Internal timestamp for the modification of the habit. Best left unchanged
            sort_order: Sort order
            section_id: id of the section. -1 for "other"
            status: 0 for active, 1 for archived
            step: TODO: Further research required
            total_checkins: Total amount of checkins. Best left unchanged
            completed_cycles: TODO: Further research required
            ex_dates: TODO: Further research required
        Returns:
              Server response. Successful if id2etag not empty
        """

        generated_id = secrets.token_hex(24)

        payload = {
            "add": [
                {
                    "color": color,
                    "iconRes": icon,
                    "createdTime": str(created_time),
                    "encouragement": encouragement,
                    "etag": etag,
                    "goal": goal,
                    "id": generated_id,
                    "modifiedTime": str(modified_time),
                    "name": name,
                    "recordEnable": record_enable,
                    "reminders": reminders,
                    "repeatRule": repeat_rule,
                    "sortOrder": sort_order,
                    "status": status,
                    "step": step,
                    "totalCheckIns": total_checkins,
                    "type": habit_type,
                    "unit": unit,
                    "sectionId": section_id,
                    "targetDays": target_days,
                    "targetStartDate": target_start_date,
                    "completedCycles": completed_cycles,
                    "exDates": ex_dates
                }
            ],
            "update": [],
            "delete": []
        }

        return self._client.http_post(url=self.HABITS_BASE_URL + "/batch",
                                      cookies=self._client.cookies,
                                      headers=self._client.HEADERS,
                                      json=payload)

    def delete(self, habit_id):
        """
        Deletes a habit

        Arguments:
            habit_id: Which habit to delete

        Returns:
            Server response. Successful if id2etag and id2error empty
        """
        payload = {
            "add": [],
            "update": [],
            "delete": [
                habit_id
            ]
        }
        return self._client.http_post(url=self.HABITS_BASE_URL + "/batch",
                                      cookies=self._client.cookies,
                                      headers=self._client.HEADERS,
                                      json=payload)

    def archive(self, habit_id, archived_time=datetime.now(), archive_status=True):
        """
        Archives the given habit.

        Arguments:
            habit_id: habit id
            archived_time: Internal archive time
            archive_status: Whether to archive or un-archive

        Returns:
              Server response. Successful if id2etag not empty
        """
        habit = self.get_habit(habit_id)
        if archive_status:
            habit['archivedTime'] = archived_time.isoformat()
            habit['status'] = 1
        else:
            habit['status'] = 0
        payload = {
            "add": [],
            "update": [habit],
            "delete": []
        }

        return self._client.http_post(url=self.HABITS_BASE_URL + "/batch",
                                      cookies=self._client.cookies,
                                      headers=self._client.HEADERS,
                                      json=payload)

    def set_checkin(self, habit_id, value, date=datetime.today()):
        """
        Sets the "checkin" (value) of a habit. Creates a new checkin of none exist for the given date.

        Arguments:
            habit_id: id of the habit
            value (int): new value of the checkin. Use 1.0/0.0 for on/off habits
            date (datetime): date at which to change the checkin

        Returns:
              Server response. Successful if id2etag and id2error empty
        """
        checkin_id = self.get_checkin(habit_id, date)
        goal = self.get_goal(habit_id)
        if checkin_id is None:
            checkin_id = habit_id[0:5:1]
            checkin_id = checkin_id + secrets.token_hex(10)[0:19:1]
            payload = {
                "add": [{
                    "checkinStamp": (date.strftime("%Y%m%d")),
                    "opTime": ("%s" % datetime.now().isoformat()),
                    "goal": goal,
                    "habitId": habit_id,
                    "id": str(checkin_id),
                    "status": 0,
                    "value": value
                }],
                "update": [

                ],
                "delete": []
            }
        else:
            habit_id = habit_id['id']
            payload = {
                "add": [],
                "update": [
                    {
                        "checkinStamp": (date.strftime("%Y%m%d")),
                        "opTime": ("%s" % datetime.now().isoformat()),
                        "goal": goal,
                        "habitId": habit_id,
                        "id": str(checkin_id),
                        "status": 0,
                        "value": value
                    }
                ],
                "delete": []
            }

        return self._client.http_post(url=self.HABIT_CHECKINS_URL + "/batch",
                                      cookies=self._client.cookies,
                                      headers=self._client.HEADERS,
                                      json=payload)

    def get_sections(self):
        """
        Returns:
            sections (list): All sections in the format
            {
                "id": "<section_id>",
                "name": "<name> example: _morning",
                "sortOrder": <sort_id>,
                "createdTime": "<created_time>",
                "modifiedTime": "<modified_time>",
                "etag": "<etag>"
            }
        """
        response = self._client.http_get(url=self.HABIT_SECTIONS_URL,
                                         cookies=self._client.cookies,
                                         headers=self._client.HEADERS)
        return list(response)

    def get_all_checkins(self, habit_id, after_date):
        """
        Provides all "checkins" for a given habit after the given date.

        Arguments:
            habit_id: id of habit
            after_date: Exclusive date after which the checkins should be counted.

        Returns format
        {
          "checkins": {
            "<habit_id>": [
              {
                "id": "<checkin_id>",
                "habitId": "<habit_id>",
                "checkinStamp": <date stamp of checkin, example 20230215>,
                "opTime": "<date of checkin (UTC)>",
                "value": <Value of checkin, example 6>,
                "goal": <Goal of checkin, example 10>,
                "status": <status (todo: analyse status meaning)>
              }
            ]
          }
        }
        """

        formatted_date = time_methods.convert_date_to_stamp(after_date)
        payload = {
            "habitIds": [habit_id],
            "afterStamp": formatted_date
        }
        return self._client.http_post(url=self.HABIT_CHECKINS_URL + "/query",
                                      cookies=self._client.cookies,
                                      headers=self._client.HEADERS,
                                      json=payload)

    def get_checkin(self, habit_id, date):
        """
        Returns:
            Checkin of specified habit_id on specified date or None if no checkin exists on given date
        """
        self._client.sync()
        wanted_stamp = time_methods.convert_date_to_stamp(date)
        all_checkins = self.get_all_checkins(habit_id, date - timedelta(1))
        for checkin in all_checkins['checkins'][habit_id]:
            if str(checkin['checkinStamp']) == str(wanted_stamp):
                return checkin

    def get_goal(self, habit_id):
        """
        Returns:
            The (amount) goal of the habit with id habit_id
        """
        return self.get_habit(habit_id)['goal']

    def get_id_by_name(self, name):
        self._client.sync()
        """
        Returns:
            habit_id of first habit with case-sensitive name matching parameter
        """

        for habit in self._client.state['habits']:
            if habit['name'] == name:
                return habit['id']

    def get_habit(self, habit_id):
        """
        Returns:
            habit with id habit_id
        """
        self._client.sync()
        for habit in self._client.state['habits']:
            if habit['id'] == habit_id:
                return habit
        raise ValueError("Habit with id %s not found" % habit_id)

    def get_all(self):
        """
        Gets all current habit-information for the user.

        client.state['habits'] should have this information stored after login,
        use this method to obtain habits when the client state is out of sync!

        Returns:
            Server Response.
        """
        return self._client.http_get(url=self.HABITS_BASE_URL,
                                     cookies=self._client.cookies,
                                     headers=self._client.HEADERS)
