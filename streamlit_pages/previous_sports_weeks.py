import streamlit as st

import helper_functions as hf
from helper_functions.classes.player import Player

st.write(
    f"""
# Previous Sports Weeks

Here you can find the results of the previous sports week in 2024, which was a blast!

All in all, an astonishing amount of {len(hf.DATA_2024.players)} players were split into {len(hf.DATA_2024.teams)} main teams and competed in {len(hf.DATA_2024.sport_events)} different sports.
"""
)
st.page_link(
    "streamlit_pages/Statistics.py",
    label="Click here for further info on the current sports week",
    icon="📊",
    use_container_width=True,
)

with st.expander("Teams"):
    hf.st_display_team_overview(hf.DATA_2024)

with st.expander("Player/Sports Overview"):
    hf.st_display_player_overview(hf.DATA_2024)

with st.expander("Results"):
    hf.st_display_full_results(hf.DATA_2024)

with st.expander("Top Scorers"):
    hf.st_display_top_scorers(hf.DATA_2024)
