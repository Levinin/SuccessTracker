from datetime import date, timedelta
import json
import sqlite3


class TaskTracker:
    def __init__(self):
        self.start_date = None
        self.failed_days = []
        self.save_file_name = 'tracker_data.json'


    def set_start_date(self, start_date):
        self.start_date = start_date

    def increment_failed_day(self, _date: date):
        self.failed_days.append(_date)

    def adjust_failed_day(self):
        self.failed_days = self.failed_days[:-1]

    def calculate_success_percentage(self):
        today = date.today()
        # Success days are all days between start date and today or 100 days, whichever is smaller
        # Calculate the number of days between start date and today
        success_days = (today - self.start_date).days
        # If the number of days is greater than 100, set it to 100
        if success_days > 100:
            success_days = 100

        # Remove any days in the failed days list that are not in the past 100 days
        for day in self.failed_days:
            if day < today - timedelta(days=100):
                self.failed_days.remove(day)

        # Remove the number of failed days from the number of success days
        success_days -= len(self.failed_days)
        total_days = 100

        # Calculate the percentage
        return (success_days / total_days) * 100

    def save_to_file(self):
        data = {
            'start_date': str(self.start_date),
            'failed_days': [str(day) for day in self.failed_days]
        }
        with open(self.save_file_name, 'w') as file:
            json.dump(data, file)

    def get_num_failed_days(self):
        return len(self.failed_days)

    def load_from_file(self):
        try:
            with open(self.save_file_name, 'r') as file:
                data = json.load(file)
                self.start_date = date.fromisoformat(data['start_date'])
                self.failed_days = [date.fromisoformat(day) for day in data['failed_days']]
        except FileNotFoundError:
            # If the file is not found this is the first time, and we can just set start date to today.
            self.start_date = date.today()
            pass

