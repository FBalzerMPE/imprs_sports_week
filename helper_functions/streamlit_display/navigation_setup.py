import streamlit as st

from ..data_registry import DATA_NOW


def st_set_up_navigation():
    pg = st.navigation(
        {
            "": [
                st.Page(
                    "streamlit_pages/home.py",
                    title="Welcome",
                    url_path="home",
                    icon="🏠",
                ),
                st.Page(
                    "streamlit_pages/Schedule.py",
                    title="Schedule",
                    url_path="schedule",
                    icon="📆",
                ),
                st.Page(
                    "streamlit_pages/Teams.py",
                    title="Teams",
                    url_path="teams",
                    icon="👨‍👩‍👦",
                ),
            ],
            "Sports": [
                st.Page(
                    f"streamlit_pages/events/{sport.sanitized_name}.py",
                    title=sport.name,
                    icon=sport.icon,
                    url_path=sport.sanitized_name,
                )
                for sport in DATA_NOW.sport_events.values()
            ],
            "Other": [
                st.Page(
                    "streamlit_pages/Statistics.py",
                    title="FAQ and Results",
                    icon="📊",
                    url_path="statistics",
                ),
                st.Page(
                    "streamlit_pages/previous_sports_weeks.py",
                    title="Sports Week 2024 Results",
                    icon="⏪",
                    url_path="previous_sports_weeks",
                ),
                st.Page(
                    "streamlit_pages/Contact.py",
                    title="Contact",
                    icon="💬",
                    url_path="contact",
                ),
            ],
        }
    )
    pg.run()
