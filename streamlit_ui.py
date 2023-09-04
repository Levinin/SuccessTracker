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
        self.current_record = None

    def run(self):
        st.set_page_config(page_title="Success Tracker", page_icon="ico.png")

        if 'username' not in st.session_state:
            st.session_state.username = None

        if 'password' not in st.session_state:
            st.session_state.password = None

        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False

        if 'date' not in st.session_state:
            st.session_state.date = None

        if 'slips' not in st.session_state:
            st.session_state.slips = []

        st.sidebar.title(f'Welcome to Success Tracker!')

        # Login
        st.session_state.username = st.sidebar.text_input("Username")
        st.session_state.password = st.sidebar.text_input("Password", type='password')
        self.task_tracker.hash_uname_password(st.session_state.username, st.session_state.password)
        if st.session_state.logged_in:
            self.current_user = st.session_state.username
            self.main()
        else:
            if st.sidebar.button("Login") and not st.session_state.logged_in:
                if self.task_tracker.get_record(st.session_state.username, st.session_state.password):
                    st.sidebar.success("Logged in as {}".format(st.session_state.username))
                    self.current_user = st.session_state.username
                else:
                    st.sidebar.success("Welcome new user: {}".format(st.session_state.username))
                    self.current_user = st.session_state.username
                st.session_state.logged_in = True
                self.main()

    def main(self):

        st.title(f":crown: {self.current_user}'s Success Journey")

        # Set start date in the task tracker
        self.task_tracker.set_start_date(st.date_input('Success Start Date', value=self.task_tracker.start_date))

        # Set the buttons
        fail_button = st.button('Slipped +', key='fb1')
        adjust_button = st.button('Slipped -', key='ab1')

        # Failed Button
        if fail_button:
            if self.task_tracker.start_date is not None:
                # today = date.today()
                # self.task_tracker.increment_failed_day(today)
                slips = st.session_state.slips
                slips.append(date.today())
                st.session_state.slips = slips

        # Adjust Button
        if adjust_button:
            if self.task_tracker.start_date is not None:
                # self.task_tracker.adjust_failed_day()
                slips = st.session_state.slips
                slips.pop()
                st.session_state.slips = slips

        # Calculate and display success percentage
        success_percentage = self.task_tracker.calculate_success_percentage(st.session_state.slips)

        st.write(f'You have slipped up {len(self.task_tracker.failed_days)} times.')

        encourage = f"### {random.choice(motivational_statements)}"
        exercise = f"### :green[Today, if you feel an urge:]\n#### :green[{random.choice(all_exercises)}]"

        st.write(f'You have been clean {success_percentage:.2f}% of the past 100 days.')
        st.markdown(encourage)
        st.progress(int(success_percentage), "Your personal victory bar")
        st.markdown(exercise)

        # Save state to db
        self.task_tracker.save_to_db(st.session_state.slips)


if __name__ == '__main__':
    ui = StreamlitUI(TaskTracker())
    ui.run()

