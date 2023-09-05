# The task tracker object.
# Keeps data in an sqlite3 database.
# Schema is:
# CREATE TABLE user_data (
# id BLOB PRIMARY KEY,

from datetime import date, timedelta
import json
import sqlite3
import hashlib
import pickle
from time import sleep


class TaskTracker:
    def __init__(self):
        self.start_date = None
        self.failed_days = []
        self.save_file_name = 'tracker_data.json'
        self.db_name = "user_data.db"
        self.hash = ""
        self.current_record = None

    def get_record(self, uname, password) -> bool:
        self.hash_uname_password(uname, password)

        while True:
            try:
                db_conn = sqlite3.connect(self.db_name, timeout=10)
                db_curr = db_conn.cursor()
                db_curr.execute("SELECT * FROM user_data WHERE id = ? LIMIT 1;", (self.hash,))
                self.current_record = db_curr.fetchone()
                db_conn.commit()
                break
            except sqlite3.OperationalError as e:
                if "SQLITE_BUSY" in str(e):
                    sleep(0.1)
                else:
                    return "Database read error, please try again later."
            finally:
                db_conn.close()

        if self.current_record:
            self.start_date = date.fromisoformat(self.current_record[1])
            self.failed_days = pickle.loads(self.current_record[2])
            return True
        return False

    def set_start_date(self, start_date):
        self.start_date = start_date

    def increment_failed_day(self, _date: date):
        if len(self.failed_days) < (date.today() - self.start_date).days:
            self.failed_days.append(_date)

    def adjust_failed_day(self):
        self.failed_days = self.failed_days[:-1]

    def hash_uname_password(self, uname, password):
        hash_function = hashlib.sha3_512()
        hash_function.update(uname.encode('utf-8'))
        hash_function.update(password.encode('utf-8'))
        self.hash = hash_function.hexdigest()

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

    def save_to_db(self):
        """Write the hash, start date and failed days to the database. Catch a write failure and return False."""
        start = str(self.start_date)
        slips = pickle.dumps(self.failed_days)

        while True:
            try:
                db_conn = sqlite3.connect(self.db_name, timeout=10)
                db_curr = db_conn.cursor()
                db_curr.execute("INSERT OR IGNORE INTO user_data(id, start, slips) VALUES (?,?,?);",
                                     (self.hash, start, slips))
                db_curr.execute("UPDATE user_data SET start = ?, slips = ? WHERE id = ?;",
                                     (start, slips, self.hash))

                db_conn.commit()
                break
            except sqlite3.OperationalError as e:
                if "SQLITE_BUSY" in str(e):
                    sleep(0.1)
                else:
                    return "Database error, please try again later."
            finally:
                db_conn.close()

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


