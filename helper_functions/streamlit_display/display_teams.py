import streamlit as st

from ..constants import CURRENT_YEAR
from ..data_registry import DataRegistry
from .display_player_schedules import st_display_player_schedules


def st_display_team_overview(data: DataRegistry):
    """Displays a page with an overview of all teams and their players belonging to the sports week associated with the data."""
    if not data.has_teams:
        text = "🚧" * 30
        text += "\n\nThe teams for this year haven't been determined yet.\\\nCome back a few days before the sports week starts! You can look at the participants on their own page, or, if you want to read stuff about the team creation that will follow, see the explanation on the FAQ page."
        st.write(text)
        st.page_link(
            "streamlit_pages/participants.py",
            label="Head to Participants",
            icon="👨‍👩‍👦",
            use_container_width=True,
        )
        st.page_link(
            "streamlit_pages/Statistics.py",
            label="Head to FAQ",
            icon="📊",
            use_container_width=True,
        )
        return
    tabs = st.tabs([team.name for team in data.teams])
    for tab, team in zip(tabs, data.teams):
        with tab:
            team.write_streamlit_rep()

            if data.year != CURRENT_YEAR:
                continue
            st_display_player_schedules(team.player_df, team.name, data.matches)
