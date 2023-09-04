from datetime import date
from task_tracker import TaskTracker
import random

import streamlit as st

from text import *

all_exercises = home_exercises + mindfulness_exercises


class StreamlitUI:
    def __init__(self, task_tracker):
        self.task_tracker = task_tracker
        self.current_user = ""

    def run(self):
        st.set_page_config(page_title="Success Tracker", page_icon="ico.png")

        st.sidebar.title(f'Welcome to Success Tracker!')

        # Login
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Login"):
            if username == "user" and password == '1234':
                st.sidebar.success("Logged In as {}".format(username))
                task_tracker = TaskTracker()
                self.current_user = username
                self.main()
            else:
                st.sidebar.warning("Incorrect Username/Password")

    def main(self):

        st.title(f":crown: {self.current_user}'s Success Journey")

        # Load state from file
        self.task_tracker.load_from_file()

        # Set start date in the task tracker
        self.task_tracker.set_start_date(st.date_input('Success Start Date', value=self.task_tracker.start_date))

        # Set the buttons
        fail_button = st.button('Slipped +', key='fb1')
        adjust_button = st.button('Slipped -', key='ab1')

        # Failed Button
        if fail_button:
            if self.task_tracker.start_date is not None:
                today = date.today()
                self.task_tracker.increment_failed_day(today)

        # Adjust Button
        if adjust_button:
            if self.task_tracker.start_date is not None:
                self.task_tracker.adjust_failed_day()

        st.write(f'You have slipped up {self.task_tracker.get_num_failed_days()} times.')

        # Calculate and display success percentage
        success_percentage = self.task_tracker.calculate_success_percentage()

        encourage = f"### {random.choice(motivational_statements)}"
        exercise = f"### :green[Today, if you feel an urge:]\n#### :green[{random.choice(all_exercises)}]"

        st.write(f'You have been clean {success_percentage:.2f}% of the past 100 days.')
        st.markdown(encourage)
        st.progress(int(success_percentage), "Your personal victory bar")
        st.markdown(exercise)

        # Save state to file
        self.task_tracker.save_to_file()


if __name__ == '__main__':
    tracker = TaskTracker()
    ui = StreamlitUI(tracker)
    ui.run()

