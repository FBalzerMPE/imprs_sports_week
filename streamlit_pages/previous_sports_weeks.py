import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

import helper_functions as hf

_data = hf.DATA_2024

st.write(
    f"""
# Previous Sports Weeks

The first inter-institute sports week was held in 2024, and it was a blast! This page features a summary of the event, including the results, top scorers, and more.

All in all, an astonishing amount of {len(_data.players)} players signed up and were split into {len(_data.teams)} main teams. They competed in {len(_data.sport_events)} different sports, and in the end Team A was able to secure the victory.
"""
)
st.page_link(
    "streamlit_pages/Statistics.py",
    label="Click here for further info on the current sports week",
    icon="📊",
    use_container_width=True,
)


with st.expander(f"{_data.year} Poster"):
    pdf_viewer(hf.DATAPATH.joinpath(f"2024/sports_week_poster.pdf"))

with st.expander("Player/Sports Overview"):
    hf.st_display_player_overview(_data)

with st.expander("Teams"):
    hf.st_display_team_overview(_data)

with st.expander("Results"):
    hf.st_display_full_results(_data)

with st.expander("Top Scorers"):
    hf.st_display_top_scorers(_data)

with st.expander("Organizers"):
    st.write(
        f"The following people helped organize the {_data.year} sports week. All members of the organizing committee are marked with a \\*."
    )
    hf.st_display_organizers(_data, False)
