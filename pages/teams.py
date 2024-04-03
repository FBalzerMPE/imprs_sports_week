import helper_functions as hf
import streamlit as st

hf.st_set_up_header_and_sidebar()

st.write(
    """
This site provides an overview on all of the competing main teams.\\
If you know your team and nickname, you can look up the sports you've been assigned to.

**Hint:** You can sort each table by any of the sports if you want to have an overview of the players.
"""
)

for team in hf.ALL_TEAMS:
    team.write_streamlit_rep()
