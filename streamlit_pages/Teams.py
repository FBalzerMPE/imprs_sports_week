import streamlit as st

import helper_functions as hf

st.write("# Teams")


if hf.DATA_NOW.has_teams:
    st.write(
        """
    This site provides an overview on all of the competing main teams.\\
    If you know your team and nickname, you can look up the sports you've been assigned to.

    **Hints:** You can sort each table by any of the sports if you want to have an overview of the players.\\
    You can also double-click on the Avatars to see a slightly bigger version of them :)\\
    Scroll down to see the individual schedules for each player on a team!
    """
    )
hf.st_display_team_overview(hf.DATA_NOW)
