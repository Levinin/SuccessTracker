from datetime import date
from task_tracker import TaskTracker
import random

import streamlit as st

from text import *

all_exercises = home_exercises + mindfulness_exercises


class StreamlitUI:
    def __init__(self, task_tracker):
        # self.task_tracker = task_tracker
        self.current_user = ""
        self.current_record = None

    def run(self):
        st.set_page_config(page_title="Success Tracker", page_icon="ico.png")

        if 'tt' not in st.session_state:
            st.session_state.tt = TaskTracker()

        if 'username' not in st.session_state:
            st.session_state.username = None

        if 'password' not in st.session_state:
            st.session_state.password = None

        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False

        st.sidebar.title(f'Welcome to Success Tracker!')

        # Login
        st.session_state.username = st.sidebar.text_input("Username")
        st.session_state.password = st.sidebar.text_input("Password", type='password')
        st.session_state.tt.hash_uname_password(st.session_state.username, st.session_state.password)

        # If we're not logged in, get the login details etc.
        if st.session_state.logged_in:
            self.current_user = st.session_state.username
            self.main()
        else:
            if st.sidebar.button("Login") and not st.session_state.logged_in:
                if st.session_state.tt.get_record(st.session_state.username, st.session_state.password):
                    st.sidebar.success("Logged in as {}".format(st.session_state.username))
                    self.current_user = st.session_state.username
                else:
                    st.sidebar.success("Welcome new user: {}".format(st.session_state.username))
                    self.current_user = st.session_state.username
                st.session_state.logged_in = True
                self.main()

    def main(self):
        st.title(f":crown: {self.current_user}'s Success Journey")

        # Set start date in the task tracker, if not set value will be None and today's date will be used
        st.session_state.tt.set_start_date(st.date_input('Success Start Date', value=st.session_state.tt.start_date))

        # Set the buttons
        fail_button = st.button('Slipped +', key='fb1')
        adjust_button = st.button('Slipped -', key='ab1')

        # Failed Button
        if fail_button:
            st.session_state.tt.increment_failed_day(date.today())

        # Adjust Button
        if adjust_button:
            st.session_state.tt.adjust_failed_day()

        # Calculate and display success percentage
        success_percentage = st.session_state.tt.calculate_success_percentage()

        st.write("<hr>", unsafe_allow_html=True)

        st.write(f'You have slipped up {st.session_state.tt.get_num_failed_days()} times.')
        st.write(f'You have been successful {success_percentage:.2f}% of the past 100 days.')

        encourage = f"### {random.choice(motivational_statements)}"
        st.markdown(encourage)
        st.progress(int(success_percentage), "Your personal victory bar")

        st.write("<hr>", unsafe_allow_html=True)
        exercise = f"### Today, instead of slipping:\n##### {random.choice(all_exercises)}"
        st.markdown(exercise)

        # Save state to db
        reply = st.session_state.tt.save_to_db()
        if reply:
            st.write(reply)


if __name__ == '__main__':
    ui = StreamlitUI(TaskTracker())
    ui.run()

