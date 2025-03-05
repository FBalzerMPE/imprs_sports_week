import streamlit as st

from ..classes.player import Player
from ..data_registry import DataRegistry


def st_display_sports_overview(data: DataRegistry):
    """Displays a page with an overview of all teams and their players belonging to the sports week associated with the data."""
    sports = data.sport_events
    st.write(", ".join(sports.keys()))
